import json
from pathlib import Path
from typing import List, Dict, Any

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
    
    # Простой текстовый поиск как основной fallback (работает всегда)
    try:
        # Ищем по заголовку и содержимому
        lectures = Lecture.objects.filter(
            Q(title__icontains=query) | 
            Q(content_text__icontains=query)
        )[:top_k]
        
        if lectures.exists():
            results = []
            for lec in lectures:
                # Простой подсчет релевантности по количеству вхождений
                title_matches = lec.title.lower().count(query.lower())
                content_matches = lec.content_text.lower().count(query.lower()) if lec.content_text else 0
                score = (title_matches * 2 + content_matches) / max(len(lec.content_text or ""), 1) * 100
                
                results.append(_lecture_to_result(lec, min(score, 100.0)))
            
            # Сортируем по релевантности
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:top_k]
    except Exception:
        pass

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
                results.append(_lecture_to_result(lec, float(s)))
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
            return [_lecture_to_result(lec, score) for score, lec in scored[:top_k]]
        except Exception:  # pragma: no cover
            pass

    # BM25 fallback
    try:
        from rank_bm25 import BM25Okapi  # type: ignore
    except Exception:  # pragma: no cover
        # Простейший fallback: фильтрация по вхождению текста
        qs: QuerySet[Lecture] = Lecture.objects.filter(content_text__icontains=query)[
            :top_k
        ]
        return [_lecture_to_result(lec, 1.0) for lec in qs]

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
        return [_lecture_to_result(lec, float(score)) for score, lec in scored[:top_k]]
    except Exception:
        # Fallback: простой поиск по вхождению
        qs = Lecture.objects.filter(content_text__icontains=query)[:top_k]
        return [_lecture_to_result(lec, 1.0) for lec in qs]


def _lecture_to_result(lecture: Lecture, score: float) -> Dict[str, Any]:
    text = lecture.content_text or ""
    snippet = text[:200] + ("..." if len(text) > 200 else "")
    return {
        "id": lecture.id,
        "title": lecture.title,
        "snippet": snippet,
        "url": lecture.content_url,
        "score": score,
    }



