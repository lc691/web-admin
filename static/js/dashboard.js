/**
 * Dashboard JavaScript Module
 * Handle all dashboard interactions
 */

const Dashboard = {
    // Initialize dashboard
    init: function() {
        console.log('Dashboard initialized');
        
        this.setupDarkMode();
        this.setupLiveDate();
        this.setupKeyboardShortcuts();
        this.setupRefreshButton();
        this.setupChartPeriodHandler();
    },

    // Dark Mode Handler
    setupDarkMode: function() {
        const toggle = document.getElementById('darkToggle');
        const body = document.body;

        if (!toggle) return;

        // Load saved theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            body.classList.add('dark-mode');
            toggle.innerHTML = '☀️';
        }

        // Check system preference
        if (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            body.classList.add('dark-mode');
            toggle.innerHTML = '☀️';
        }

        // Toggle handler
        toggle.addEventListener('click', () => {
            body.classList.toggle('dark-mode');
            const isDark = body.classList.contains('dark-mode');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            toggle.innerHTML = isDark ? '☀️' : '🌙';
        });
    },

    // Live Date Update
    setupLiveDate: function() {
        const days = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
        const months = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 
                       'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'];

        function updateDateTime() {
            const now = new Date();
            const dateStr = days[now.getDay()] + ', ' + 
                           now.getDate() + ' ' + 
                           months[now.getMonth()] + ' ' + 
                           now.getFullYear();

            const el = document.getElementById('liveDate');
            if (el && el.textContent !== dateStr) {
                el.textContent = dateStr;
            }
        }

        updateDateTime();
        setInterval(updateDateTime, 60000);
    },

    // Keyboard Shortcuts
    setupKeyboardShortcuts: function() {
        document.addEventListener('keydown', (e) => {
            // Ctrl + R = Refresh
            if (e.ctrlKey && e.key === 'r') {
                e.preventDefault();
                this.refreshData();
            }
            // Ctrl + S = Add Show
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                window.location.href = '/shows/add';
            }
        });
    },

    // Refresh Button Handler
    setupRefreshButton: function() {
        const refreshBtn = document.querySelector('.quick-action-btn:last-child');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }
    },

    // Refresh Dashboard Data
    refreshData: async function() {
        const refreshBtn = document.querySelector('.quick-action-btn:last-child i');
        if (refreshBtn) {
            refreshBtn.classList.add('fa-spin');
        }

        try {
            const response = await fetch(window.location.href + '?ajax=1', {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const data = await response.json();
            console.log('Refresh data received:', data);

            // Update stat values
            if (data.stats) {
                document.querySelectorAll('.stat-value').forEach(el => {
                    const statName = el.dataset.stat;
                    const newValue = data.stats[statName];
                    if (newValue !== undefined && String(newValue) !== el.textContent) {
                        el.classList.remove('count-up');
                        el.textContent = typeof newValue === 'number' ? 
                            newValue.toLocaleString() : newValue;
                        el.classList.add('count-up');
                    }
                });
            }

            // Update charts
            if (data.chart_labels && data.chart_values && window.currentChart) {
                window.currentChart.data.labels = data.chart_labels;
                window.currentChart.data.datasets[0].data = data.chart_values;
                window.currentChart.update();
            }

            if (data.revenue_distribution && window.revenueChart) {
                window.__REVENUE_DATA__ = data.revenue_distribution;
                window.initCharts();
            }

            // Update last update time
            const lastUpdateEl = document.getElementById('lastUpdate');
            if (lastUpdateEl) {
                const now = new Date();
                lastUpdateEl.textContent = now.toLocaleTimeString('id-ID');
            }

            // Show success notification
            Swal.fire({
                icon: 'success',
                title: 'Data Diperbarui',
                text: 'Dashboard telah diperbarui',
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 2000
            });

        } catch (err) {
            console.error('Refresh failed:', err);
            Swal.fire({
                icon: 'error',
                title: 'Gagal Refresh',
                text: 'Tidak dapat memperbarui data dashboard',
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 3000
            });
        } finally {
            if (refreshBtn) {
                refreshBtn.classList.remove('fa-spin');
            }
        }
    },

    // Chart Period Handler
    setupChartPeriodHandler: function() {
        const periodSelect = document.getElementById('chartPeriod');
        if (!periodSelect) return;

        periodSelect.addEventListener('change', function() {
            const period = this.value;
            console.log('Chart period changed to:', period);

            const chartContainer = document.querySelector('#vipUsersChart')?.parentElement;
            if (chartContainer) chartContainer.style.opacity = '0.5';

            fetch(`/api/dashboard/chart?period=${period}`)
                .then(response => {
                    if (!response.ok) throw new Error('Network error');
                    return response.json();
                })
                .then(data => {
                    if (window.currentChart && data.labels && data.values) {
                        window.currentChart.data.labels = data.labels;
                        window.currentChart.data.datasets[0].data = data.values;
                        window.currentChart.update();
                    }
                    if (chartContainer) chartContainer.style.opacity = '1';
                })
                .catch(err => {
                    console.error('Error loading chart data:', err);
                    if (chartContainer) chartContainer.style.opacity = '1';
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'Gagal memuat data grafik',
                        toast: true,
                        position: 'top-end',
                        showConfirmButton: false,
                        timer: 3000
                    });
                });
        });
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    Dashboard.init();
});

// Make functions globally accessible
window.refreshDashboardData = () => Dashboard.refreshData();
window.Dashboard = Dashboard;