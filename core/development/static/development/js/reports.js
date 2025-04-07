// Управление темой
const themeToggle = document.getElementById('themeToggle');
themeToggle.addEventListener('click', () => {
    document.documentElement.classList.toggle('dark');
    localStorage.setItem('darkMode', document.documentElement.classList.contains('dark'));
});

// Проверка сохраненной темы
if (localStorage.getItem('darkMode') === 'true') {
    document.documentElement.classList.add('dark');
}

// Управление вкладками
function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    document.getElementById(tabId).classList.add('active');

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('bg-blue-50', 'dark:bg-blue-900', 'text-blue-700', 'dark:text-blue-200');
        btn.classList.add('hover:bg-gray-100', 'dark:hover:bg-gray-700', 'text-gray-700', 'dark:text-gray-300');
    });

    document.querySelector(`.tab-btn[onclick="showTab('${tabId}')"]`).classList.add(
        'bg-blue-50', 'dark:bg-blue-900', 'text-blue-700', 'dark:text-blue-200'
    );
}

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    showTab('current-projects');
});