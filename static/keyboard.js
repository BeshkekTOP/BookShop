// Система горячих клавиш для книжного магазина
// Реализует 8+ горячих клавиш для частых операций

const KeyboardShortcuts = {
    shortcuts: [],
    
    // Регистрация сочетания клавиш
    register(keyCombo, callback, description) {
        this.shortcuts.push({
            combo: keyCombo,
            callback: callback,
            description: description
        });
    },
    
    // Инициализация системы
    init() {
        document.addEventListener('keydown', (e) => {
            // Проверяем, не вводит ли пользователь текст
            const target = e.target;
            if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
                return;
            }
            
            // Формируем комбинацию клавиш
            let combo = '';
            if (e.ctrlKey || e.metaKey) combo += 'ctrl+';
            if (e.altKey) combo += 'alt+';
            if (e.shiftKey) combo += 'shift+';
            combo += e.key.toLowerCase();
            
            // Поиск соответствующей команды
            const shortcut = this.shortcuts.find(s => s.combo === combo);
            if (shortcut) {
                e.preventDefault();
                shortcut.callback(e);
                this.showNotification(`Выполнено: ${shortcut.description}`);
            }
        });
        
        // Показываем подсказку при первом запуске
        this.showHelp();
    },
    
    // Показ уведомления
    showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'keyboard-notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--primary);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: var(--shadow);
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    },
    
    // Показ справки по горячим клавишам
    showHelp() {
        if (sessionStorage.getItem('keyboard_help_shown') === 'true') return;
        
        const helpModal = document.createElement('div');
        helpModal.id = 'keyboard-help';
        helpModal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10001;
        `;
        
        const helpContent = document.createElement('div');
        helpContent.style.cssText = `
            background: white;
            padding: 24px;
            border-radius: 12px;
            max-width: 500px;
            box-shadow: var(--shadow);
        `;
        
        let html = '<h2>Горячие клавиши</h2><ul style="list-style:none;padding:0">';
        this.shortcuts.forEach(s => {
            html += `<li style="padding:8px;border-bottom:1px solid var(--border)">
                <strong>${s.combo}</strong> - ${s.description}
            </li>`;
        });
        html += '</ul>';
        html += '<button onclick="this.closest(\'#keyboard-help\').remove()" class="btn" style="margin-top:16px;width:100%">Понятно</button>';
        
        helpContent.innerHTML = html;
        helpModal.appendChild(helpContent);
        document.body.appendChild(helpModal);
        
        sessionStorage.setItem('keyboard_help_shown', 'true');
    }
};

// Регистрация горячих клавиш
document.addEventListener('DOMContentLoaded', () => {
    // 1. Alt+H - Главная страница
    KeyboardShortcuts.register('alt+h', () => {
        window.location.href = '/';
    }, 'Перейти на главную');
    
    // 2. Alt+C - Каталог
    KeyboardShortcuts.register('alt+c', () => {
        window.location.href = '/catalog/';
    }, 'Открыть каталог');
    
    // 3. Alt+B - Корзина
    KeyboardShortcuts.register('alt+b', () => {
        window.location.href = '/cart/';
    }, 'Открыть корзину');
    
    // 4. Alt+S - Поиск (фокус на поле поиска)
    KeyboardShortcuts.register('alt+s', () => {
        const searchInput = document.querySelector('input[type="search"], input[type="text"]');
        if (searchInput) searchInput.focus();
    }, 'Начать поиск');
    
    // 5. Alt+P - Профиль
    KeyboardShortcuts.register('alt+p', () => {
        window.location.href = '/profile/';
    }, 'Открыть профиль');
    
    // 6. Alt+A - Админка (если есть права)
    KeyboardShortcuts.register('alt+a', () => {
        if (document.body.dataset.isStaff === 'true') {
            window.location.href = '/admin/';
        }
    }, 'Админ-панель');
    
    // 7. Escape - Закрыть модальные окна
    KeyboardShortcuts.register('Escape', () => {
        const modals = document.querySelectorAll('.modal, #keyboard-help');
        modals.forEach(modal => modal.remove());
    }, 'Закрыть окно');
    
    // 8. Ctrl+K или Cmd+K - Показать подсказки
    KeyboardShortcuts.register('ctrl+k', () => {
        KeyboardShortcuts.showHelp();
    }, 'Показать горячие клавиши');
    
    KeyboardShortcuts.register('ctrl+meta+k', () => {
        KeyboardShortcuts.showHelp();
    }, 'Показать горячие клавиши');
    
    // 9. Alt+L - Вход/Выход
    KeyboardShortcuts.register('alt+l', () => {
        const isAuth = document.body.dataset.isAuthenticated === 'true';
        window.location.href = isAuth ? '/logout/' : '/login/';
    }, 'Вход/Выход');
    
    // 10. Ctrl+/ - Показать подсказки (дублирующая команда)
    KeyboardShortcuts.register('ctrl+/', () => {
        KeyboardShortcuts.showHelp();
    }, 'Показать справку');
    
    // Инициализация
    KeyboardShortcuts.init();
});

// Добавляем CSS для анимаций
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

