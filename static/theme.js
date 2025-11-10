// Управление темами
class ThemeManager {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'light';
        this.applyTheme(this.theme);
        this.init();
    }

    init() {
        this.applyTheme(this.theme);
        this.createThemeToggle();
        this.bindEvents();
    }

    applyTheme(theme) {
        // Убираем старые классы
        document.body.classList.remove('light', 'dark');
        // Применяем новый класс
        document.body.classList.add(theme);
        localStorage.setItem('theme', theme);
    }
    
    getStoredTheme() {
        return localStorage.getItem('theme') || 'light';
    }

    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        this.applyTheme(this.theme);
        this.updateToggleButton();
    }

    createThemeToggle() {
        // Создаем кнопку переключения темы
        const navRight = document.querySelector('.nav-right');
        if (navRight && !document.querySelector('.theme-toggle')) {
            const themeToggle = document.createElement('button');
            themeToggle.className = 'theme-toggle';
            themeToggle.setAttribute('aria-label', 'Переключить тему');
            
            // Определяем текущую иконку
            const icon = this.theme === 'dark' ? '🌙' : '☀️';
            themeToggle.textContent = icon;
            
            // Добавляем стили для кнопки
            themeToggle.style.cssText = `
                border: 1px solid var(--border);
                background: var(--card);
                border-radius: 50%;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                font-size: 18px;
                transition: all 0.3s ease;
            `;
            
            // Добавляем обработчик hover
            themeToggle.addEventListener('mouseenter', () => {
                themeToggle.style.transform = 'scale(1.1)';
                themeToggle.style.boxShadow = 'var(--shadow)';
            });
            
            themeToggle.addEventListener('mouseleave', () => {
                themeToggle.style.transform = 'scale(1)';
                themeToggle.style.boxShadow = 'none';
            });
            
            // Обновляем иконку при изменении темы
            this.themeToggleButton = themeToggle;
            
            navRight.insertBefore(themeToggle, navRight.firstChild);
        }
    }

    updateToggleButton() {
        const toggle = this.themeToggleButton || document.querySelector('.theme-toggle');
        if (toggle) {
            // Обновляем иконку
            const icon = this.theme === 'dark' ? '🌙' : '☀️';
            toggle.textContent = icon;
            
            // Анимация переключения
            toggle.style.transform = 'scale(0.9)';
            setTimeout(() => {
                toggle.style.transform = 'scale(1)';
            }, 150);
        }
    }

    bindEvents() {
        const toggle = document.querySelector('.theme-toggle');
        if (toggle) {
            toggle.addEventListener('click', () => this.toggleTheme());
        }

        // Обработка системной темы
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            mediaQuery.addListener((e) => {
                if (localStorage.getItem('theme') === 'auto') {
                    this.applyTheme(e.matches ? 'dark' : 'light');
                }
            });
        }
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    new ThemeManager();
});

// Утилиты для анимаций
class AnimationUtils {
    static fadeIn(element, duration = 300) {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = `opacity ${duration}ms ease, transform ${duration}ms ease`;
        
        requestAnimationFrame(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        });
    }

    static slideIn(element, duration = 300) {
        element.style.opacity = '0';
        element.style.transform = 'translateX(-20px)';
        element.style.transition = `opacity ${duration}ms ease, transform ${duration}ms ease`;
        
        requestAnimationFrame(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateX(0)';
        });
    }

    static scaleIn(element, duration = 200) {
        element.style.opacity = '0';
        element.style.transform = 'scale(0.9)';
        element.style.transition = `opacity ${duration}ms ease, transform ${duration}ms ease`;
        
        requestAnimationFrame(() => {
            element.style.opacity = '1';
            element.style.transform = 'scale(1)';
        });
    }
}

// Анимация появления карточек
document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.card, .stat-card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            AnimationUtils.fadeIn(card);
        }, index * 100);
    });
});

// Плавная прокрутка для якорных ссылок
document.addEventListener('DOMContentLoaded', () => {
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector(link.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Улучшенные уведомления
class NotificationManager {
    static show(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} notification`;
        notification.textContent = message;
        
        // Стили для уведомления
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            max-width: 400px;
            box-shadow: var(--shadow-lg);
            animation: slideInRight 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        // Анимация появления
        AnimationUtils.slideIn(notification);
        
        // Автоматическое удаление
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, duration);
    }
}

// Добавляем CSS для анимации уведомлений
const notificationStyle = document.createElement('style');
notificationStyle.textContent = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
`;
document.head.appendChild(notificationStyle);

// Экспорт для использования в других скриптах
window.ThemeManager = ThemeManager;
window.AnimationUtils = AnimationUtils;
window.NotificationManager = NotificationManager;
