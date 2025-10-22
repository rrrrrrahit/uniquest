// =====================================
// UniQuest — главные анимации и интерактив
// =====================================

// ---------------------------
// Плавное появление элементов при скролле
// ---------------------------
document.addEventListener('DOMContentLoaded', () => {
    const animatedElements = document.querySelectorAll('main, .card, .btn, header, footer');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('appear');
            }
        });
    }, { threshold: 0.1 });

    animatedElements.forEach(el => observer.observe(el));
});

// ---------------------------
// Анимация прогресс-баров
// ---------------------------
document.addEventListener('DOMContentLoaded', () => {
    const bars = document.querySelectorAll('.progress-bar');
    bars.forEach(bar => {
        const value = bar.getAttribute('data-value');
        bar.style.width = '0';
        setTimeout(() => {
            bar.style.transition = 'width 1.5s ease-in-out';
            bar.style.width = `${value}%`;
        }, 300);
    });
});

// ---------------------------
// Плавающие формы на фоне (движение через JS)
// ---------------------------
const shapes = document.querySelector('.floating-shapes');
if (shapes) {
    let posX = 0;
    let posY = 0;
    let angle = 0;

    function animateShapes() {
        angle += 0.002;
        posX = Math.sin(angle) * 30;
        posY = Math.cos(angle) * 20;
        shapes.style.transform = `translate(${posX}px, ${posY}px)`;
        requestAnimationFrame(animateShapes);
    }

    animateShapes();
}

// ---------------------------
// Кнопки с подсветкой
// ---------------------------
const buttons = document.querySelectorAll('.btn');
buttons.forEach(btn => {
    btn.addEventListener('mouseenter', () => {
        btn.style.boxShadow = '0 0 20px rgba(255,255,255,0.4)';
    });
    btn.addEventListener('mouseleave', () => {
        btn.style.boxShadow = 'none';
    });
});

// ---------------------------
// Форма входа: enter = submit
// ---------------------------
const loginForm = document.querySelector('.login-page form');
if (loginForm) {
    loginForm.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') loginForm.submit();
    });
}

// ---------------------------
// Форма регистрации: проверка совпадения паролей
// ---------------------------
const registerForm = document.querySelector('.register-page form');
if (registerForm) {
    const pass1 = registerForm.querySelector('input[name="password1"]');
    const pass2 = registerForm.querySelector('input[name="password2"]');

    registerForm.addEventListener('submit', (e) => {
        if (pass1.value !== pass2.value) {
            e.preventDefault();
            alert('Пароли не совпадают!');
        }
    });
}
