// Переключение темы
const themeToggle = document.getElementById('themeToggle');
themeToggle.addEventListener('click', () => {
    document.documentElement.classList.toggle('dark');
    localStorage.setItem('darkMode', document.documentElement.classList.contains('dark'));
});

// Проверка сохраненной темы
if (localStorage.getItem('darkMode') === 'true') {
    document.documentElement.classList.add('dark');
}

// Переключение между вкладками
function showTab(tabId) {
    // Скрыть все вкладки
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Показать выбранную вкладку
    document.getElementById(tabId).classList.add('active');

    // Обновить активную кнопку в меню
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('bg-blue-50', 'dark:bg-blue-900', 'text-blue-700', 'dark:text-blue-200');
        btn.classList.add('hover:bg-gray-100', 'dark:hover:bg-gray-700', 'text-gray-700', 'dark:text-gray-300');
    });

    // Сделать активную кнопку выделенной
    document.querySelector(`.tab-btn[onclick="showTab('${tabId}')"]`).classList.add('bg-blue-50', 'dark:bg-blue-900', 'text-blue-700', 'dark:text-blue-200');
    document.querySelector(`.tab-btn[onclick="showTab('${tabId}')"]`).classList.remove('hover:bg-gray-100', 'dark:hover:bg-gray-700', 'text-gray-700', 'dark:text-gray-300');

    // Если это вкладка с графиками, перерисовать их
    if (tabId === 'quality-metrics') {
        setTimeout(renderCharts, 100);
    }
}

// Фильтрация сотрудников
const employeeSelect = document.getElementById('employeeSelect');
const employeeSearch = document.getElementById('employeeSearch');

if (employeeSelect && employeeSearch) {
    employeeSelect.addEventListener('change', filterEmployees);
    employeeSearch.addEventListener('input', filterEmployees);
}

function filterEmployees() {
    const selectedId = employeeSelect.value;
    const searchTerm = employeeSearch.value.toLowerCase();

    document.querySelectorAll('.employee-card').forEach(card => {
        const name = card.dataset.name.toLowerCase();
        const id = card.dataset.id;

        const matchesSearch = name.includes(searchTerm);
        const matchesSelect = selectedId === 'all' || id === selectedId;

        if (matchesSearch && matchesSelect) {
            card.classList.remove('hidden');
        } else {
            card.classList.add('hidden');
        }
    });
}

// Фильтрация проектов в разделе качества
document.querySelectorAll('.project-toggle').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.project-toggle').forEach(b => b.classList.remove('active', 'bg-indigo-600', 'dark:bg-indigo-700', 'text-white'));
        this.classList.add('active', 'bg-indigo-600', 'dark:bg-indigo-700', 'text-white');

        // Здесь должна быть логика фильтрации данных для графиков
        // В демонстрационных целях просто перерисовываем графики
        if (typeof renderCharts === 'function') {
            renderCharts();
        }
    });
});

// Инициализация графиков
let bugsChart, fixTimeChart;

function renderCharts() {
    // Уничтожаем старые графики, если они есть
    if (bugsChart) bugsChart.destroy();
    if (fixTimeChart) fixTimeChart.destroy();

    // Данные для демонстрации
    const projects = ['CRM система', 'Мобильное приложение', 'Платежная система'];
    const bugsData = [42, 28, 15];
    const criticalBugsData = [5, 2, 1];
    const fixTimeData = [2.3, 1.7, 3.1];

    // График 1: Статистика багов
    const bugsCtx = document.getElementById('bugsChart')?.getContext('2d');
    if (bugsCtx) {
        bugsChart = new Chart(bugsCtx, {
            type: 'bar',
            data: {
                labels: projects,
                datasets: [
                    {
                        label: 'Все баги',
                        data: bugsData,
                        backgroundColor: '#6366F1',
                        borderColor: '#4F46E5',
                        borderWidth: 1
                    },
                    {
                        label: 'Критические баги',
                        data: criticalBugsData,
                        backgroundColor: '#EC4899',
                        borderColor: '#DB2777',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#E5E7EB',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#6B7280'
                        }
                    },
                    x: {
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            color: '#6B7280'
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: '#6B7280',
                            boxWidth: 12,
                            padding: 20
                        }
                    }
                }
            }
        });
    }

    // График 2: Время исправления багов
    const fixTimeCtx = document.getElementById('fixTimeChart')?.getContext('2d');
    if (fixTimeCtx) {
        fixTimeChart = new Chart(fixTimeCtx, {
            type: 'line',
            data: {
                labels: projects,
                datasets: [{
                    label: 'Среднее время исправления (дни)',
                    data: fixTimeData,
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    borderColor: '#6366F1',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    pointBackgroundColor: '#FFFFFF',
                    pointBorderColor: '#6366F1',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#E5E7EB',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#6B7280'
                        }
                    },
                    x: {
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            color: '#6B7280'
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: '#6B7280',
                            boxWidth: 12,
                            padding: 20
                        }
                    }
                }
            }
        });
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Показать первую вкладку
    showTab('current-projects');
});