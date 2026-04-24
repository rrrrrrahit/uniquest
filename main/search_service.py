import json
from pathlib import Path
from typing import List, Dict, Any
import io
import math

from django.db.models import QuerySet, Q

from .models import Lecture


MODELS_DIR = Path("models")
FAISS_INDEX_PATH = MODELS_DIR / "faiss_index.bin"
FAISS_MAPPING_PATH = MODELS_DIR / "faiss_mapping.json"
EMBEDDINGS_INFO_PATH = MODELS_DIR / "embeddings_info.json"


def _load_embeddings_backend():
    """
    Читает информацию о доступном бэкенде семантического поиска.
    """
    if not EMBEDDINGS_INFO_PATH.exists():
        return {"backend": "bm25", "has_embeddings": False}
    try:
        return json.loads(EMBEDDINGS_INFO_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"backend": "bm25", "has_embeddings": False}


def _encode_query(text: str):
    """
    Кодирует запрос в вектор, если возможно.
    """
    try:
        from sentence_transformers import SentenceTransformer

        info = _load_embeddings_backend()
        model_name = info.get("model_name") or "sentence-transformers/all-MiniLM-L6-v2"
        model = SentenceTransformer(model_name)
        return model.encode([text])[0]
    except Exception:  # pragma: no cover - внешняя зависимость
        return None


def semantic_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Ищет релевантные лекции по запросу.
    Использует (в порядке приоритета):
      1) FAISS-индекс
      2) vector_embedding в БД
      3) BM25 (rank-bm25) по тексту
      4) Простой текстовый поиск (fallback)
    """
    query = (query or "").strip()
    if not query:
        return []
    
    info = _load_embeddings_backend()
    backend = info.get("backend", "simple")

    if backend == "faiss" and FAISS_INDEX_PATH.exists() and FAISS_MAPPING_PATH.exists():
        try:
            import faiss  # type: ignore
            import numpy as np

            from sentence_transformers import SentenceTransformer

            model_name = info.get("model_name") or "sentence-transformers/all-MiniLM-L6-v2"
            model = SentenceTransformer(model_name)

            index = faiss.read_index(str(FAISS_INDEX_PATH))
            mapping = json.loads(FAISS_MAPPING_PATH.read_text(encoding="utf-8"))

            q_vec = model.encode([query])[0].astype("float32")
            scores, indices = index.search(q_vec.reshape(1, -1), top_k)
            scores = scores[0]
            indices = indices[0]

            results = []
            for s, idx in zip(scores, indices):
                if idx < 0 or idx >= len(mapping):
                    continue
                lec_id = mapping[idx]
                try:
                    lec = Lecture.objects.get(id=lec_id)
                except Lecture.DoesNotExist:
                    continue
                results.append(_lecture_to_result(lec, float(s), query))
            return results
        except Exception:  # pragma: no cover
            backend = "database"

    if backend in ("database",) and info.get("has_embeddings"):
        try:
            import numpy as np

            q_vec = _encode_query(query)
            if q_vec is None:
                raise RuntimeError("no embeddings model")

            lectures = Lecture.objects.exclude(vector_embedding__isnull=True)
            scored = []
            for lec in lectures:
                emb = lec.vector_embedding
                if not emb:
                    continue
                v = np.array(emb, dtype=float)
                q = np.array(q_vec, dtype=float)
                denom = (np.linalg.norm(v) * np.linalg.norm(q)) or 1.0
                score = float(np.dot(v, q) / denom)
                scored.append((score, lec))
            scored.sort(key=lambda x: x[0], reverse=True)
            return [_lecture_to_result(lec, score, query) for score, lec in scored[:top_k]]
        except Exception:  # pragma: no cover
            pass

    # Семантический fallback без torch: LSA (TF-IDF + SVD).
    lsa_results = _lsa_semantic_search(query, top_k)
    if lsa_results:
        return lsa_results

    # Лексический поиск по реальному содержимому документа.
    text_results = _text_search_results(query, top_k)
    if text_results:
        return text_results

    # BM25 fallback
    try:
        from rank_bm25 import BM25Okapi  # type: ignore
    except Exception:  # pragma: no cover
        # Простейший fallback: фильтрация по вхождению текста
        qs: QuerySet[Lecture] = Lecture.objects.filter(content_text__icontains=query)[
            :top_k
        ]
        return [_lecture_to_result(lec, 1.0, query) for lec in qs]

    lectures = Lecture.objects.exclude(content_text__isnull=True).exclude(content_text='')
    if not lectures.exists():
        # Если нет лекций с текстом, возвращаем пустой список
        return []
    
    corpus = []
    valid_lectures = []
    for lec in lectures:
        if lec.content_text:
            try:
                corpus.append(lec.content_text.split())
                valid_lectures.append(lec)
            except Exception:
                continue
    
    if not corpus:
        return []
    
    try:
        bm25 = BM25Okapi(corpus)
        scores = bm25.get_scores(query.split())
        scored = list(zip(scores, valid_lectures))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [_lecture_to_result(lec, float(score), query) for score, lec in scored[:top_k]]
    except Exception:
        # Fallback: простой поиск по вхождению
        qs = Lecture.objects.filter(content_text__icontains=query)[:top_k]
        return [_lecture_to_result(lec, 1.0, query) for lec in qs]


def _lecture_to_result(lecture: Lecture, score: float, query: str = "") -> Dict[str, Any]:
    text = _get_search_text(lecture)
    snippet = _build_snippet(text, query)
    return {
        "id": lecture.id,
        "title": lecture.title,
        "snippet": snippet,
        "url": lecture.content_url,
        "score": score,
    }


def _extract_text_from_lecture_file(lecture: Lecture) -> str:
    file_field = getattr(lecture, "lecture_file", None)
    if not file_field:
        return ""

    file_name = (getattr(file_field, "name", "") or "").lower()
    ext = file_name.rsplit(".", 1)[-1] if "." in file_name else ""
    if not ext:
        return ""

    try:
        raw = file_field.read()
    except Exception:
        return ""
    finally:
        try:
            file_field.seek(0)
        except Exception:
            pass

    if not raw:
        return ""

    if ext in {"txt", "md", "csv", "json", "log", "py"}:
        for encoding in ("utf-8", "utf-8-sig", "cp1251", "latin1"):
            try:
                return raw.decode(encoding).strip()
            except Exception:
                continue
        return ""

    if ext == "pdf":
        try:
            from pypdf import PdfReader  # type: ignore

            reader = PdfReader(io.BytesIO(raw))
            pages = [(page.extract_text() or "") for page in reader.pages]
            return "\n".join(pages).strip()
        except Exception:
            return ""

    if ext == "docx":
        try:
            from docx import Document  # type: ignore

            doc = Document(io.BytesIO(raw))
            return "\n".join(p.text for p in doc.paragraphs if p.text).strip()
        except Exception:
            return ""

    return ""


def _get_search_text(lecture: Lecture) -> str:
    base = (lecture.content_text or "").strip()
    if base:
        return base

    extracted = _extract_text_from_lecture_file(lecture).strip()
    if extracted:
        # Кешируем в БД, чтобы следующий поиск был быстрее и стабильнее.
        lecture.content_text = extracted
        try:
            lecture.save(update_fields=["content_text"])
        except Exception:
            pass
    return extracted


def build_lecture_snippet(lecture: Lecture, query: str = "", max_len: int = 320) -> str:
    text = _get_search_text(lecture)
    snippet = _build_snippet(text, query, max_len=max_len).strip()
    if snippet:
        return snippet
    if lecture.lecture_file:
        return f"Файл: {Path(lecture.lecture_file.name).name}"
    if lecture.content_url:
        return f"Ссылка: {lecture.content_url}"
    return "Текст фрагмента пока недоступен для этого материала."


def _text_search_results(query: str, top_k: int) -> List[Dict[str, Any]]:
    try:
        terms = [term.lower() for term in query.split() if term]
        query_lower = query.lower()
        lectures = Lecture.objects.all().select_related("course")
        results = []

        for lec in lectures:
            title_lower = (lec.title or "").lower()
            content_lower = _get_search_text(lec).lower()

            if not content_lower and not title_lower:
                continue

            title_matches = title_lower.count(query_lower)
            content_matches = content_lower.count(query_lower)
            term_matches = 0
            for term in terms:
                term_matches += title_lower.count(term) * 3
                term_matches += content_lower.count(term)

            score_raw = (title_matches * 5) + (content_matches * 2) + term_matches
            if score_raw <= 0:
                continue

            score = min((score_raw / max(len(content_lower), 1)) * 2500, 100.0)
            results.append(_lecture_to_result(lec, score, query))

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    except Exception:
        return []


def _build_snippet(text: str, query: str, max_len: int = 320) -> str:
    text = (text or "").strip()
    if not text:
        return ""

    if not query:
        return text[:max_len] + ("..." if len(text) > max_len else "")

    text_lower = text.lower()
    query_lower = query.lower()
    terms = [t.lower() for t in query.split() if t]

    match_pos = text_lower.find(query_lower)
    if match_pos < 0:
        for term in terms:
            pos = text_lower.find(term)
            if pos >= 0:
                match_pos = pos
                break

    if match_pos < 0:
        return text[:max_len] + ("..." if len(text) > max_len else "")

    start = max(0, match_pos - max_len // 3)
    end = min(len(text), start + max_len)
    snippet = text[start:end].strip()

    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    return snippet


def _lsa_semantic_search(query: str, top_k: int) -> List[Dict[str, Any]]:
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.decomposition import TruncatedSVD
        from sklearn.metrics.pairwise import cosine_similarity
    except Exception:
        return []

    lectures = list(Lecture.objects.all().select_related("course"))
    if not lectures:
        return []

    docs = []
    valid = []
    for lec in lectures:
        text = _get_search_text(lec)
        if not text:
            continue
        # Добавляем заголовок в документ для лучшего семантического контекста.
        docs.append(f"{lec.title}\n\n{text}")
        valid.append(lec)

    if not docs:
        return []

    try:
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.98,
            sublinear_tf=True,
        )
        doc_matrix = vectorizer.fit_transform(docs)
        query_matrix = vectorizer.transform([query])

        # Если корпус очень маленький, работаем напрямую в TF-IDF пространстве.
        if doc_matrix.shape[0] < 3 or doc_matrix.shape[1] < 3:
            sims = cosine_similarity(query_matrix, doc_matrix).flatten()
        else:
            n_components = min(128, doc_matrix.shape[0] - 1, doc_matrix.shape[1] - 1)
            if n_components < 2:
                sims = cosine_similarity(query_matrix, doc_matrix).flatten()
            else:
                svd = TruncatedSVD(n_components=n_components, random_state=42)
                doc_lsa = svd.fit_transform(doc_matrix)
                query_lsa = svd.transform(query_matrix)
                sims = cosine_similarity(query_lsa, doc_lsa).flatten()

        ranked = sorted(
            [(float(score), lec) for score, lec in zip(sims, valid) if score > 0],
            key=lambda item: item[0],
            reverse=True,
        )[:top_k]

        return [_lecture_to_result(lec, min(score * 100.0, 100.0), query) for score, lec in ranked]
    except Exception:
        return []



