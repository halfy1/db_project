// Инициализация графиков
let bugsChart, fixTimeChart;

function renderCharts() {
    if (bugsChart) bugsChart.destroy();
    if (fixTimeChart) fixTimeChart.destroy();

    const projects = JSON.parse(document.getElementById('projects-data').textContent);
    const bugsData = JSON.parse(document.getElementById('bugs-data').textContent);
    const criticalBugsData = JSON.parse(document.getElementById('critical-bugs-data').textContent);
    const fixTimeData = JSON.parse(document.getElementById('fix-time-data').textContent);

    // График 1
    const bugsCtx = document.getElementById('bugsChart').getContext('2d');
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
            maintainAspectRatio: false
        }
    });

    // График 2
    const fixTimeCtx = document.getElementById('fixTimeChart').getContext('2d');
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
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// Вызываем при загрузке и при переключении вкладок
document.addEventListener('DOMContentLoaded', renderCharts);
window.renderCharts = renderCharts;