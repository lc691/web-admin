/**
 * Charts Module
 * Initialize and manage all charts
 */

const Charts = {
    currentChart: null,
    revenueChart: null,

    // Initialize all charts
    init: function() {
        console.log('Initializing charts...');
        
        this.initVIPChart();
        this.initRevenuePieChart();
        
        // Handle window resize
        window.addEventListener('resize', this.handleResize.bind(this));
    },

    // VIP Users Trend Chart
    initVIPChart: function() {
        const canvas = document.getElementById('vipUsersChart');
        if (!canvas) {
            console.warn('VIP chart canvas not found');
            return;
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Destroy existing chart
        if (this.currentChart) {
            this.currentChart.destroy();
            this.currentChart = null;
        }

        // Get data
        let labels = window.__CHART_LABELS__ || [];
        let data = window.__CHART_DATA__ || [];

        // Use sample data if empty
        if (!labels.length || !data.length) {
            console.warn('No chart data, using sample data');
            labels = [];
            data = [];
            for (let i = 29; i >= 0; i--) {
                const date = new Date();
                date.setDate(date.getDate() - i);
                labels.push(date.toLocaleDateString('id-ID', {day:'numeric', month:'short'}));
                data.push(Math.floor(Math.random() * 50) + 10);
            }
        }

        // Create chart
        this.currentChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'VIP Users',
                    data: data,
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.05)',
                    borderWidth: 3,
                    pointRadius: 4,
                    pointBackgroundColor: '#8b5cf6',
                    pointBorderColor: '#fff',
                    pointHoverRadius: 6,
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            font: { size: 13 }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return 'VIP Users: ' + context.parsed.y.toLocaleString();
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Jumlah VIP Users'
                        }
                    }
                }
            }
        });

        console.log('VIP chart created with', labels.length, 'data points');
    },

    // Revenue Distribution Pie Chart
    initRevenuePieChart: function() {
        const canvas = document.getElementById('revenuePieChart');
        if (!canvas) {
            console.warn('Revenue pie chart canvas not found');
            return;
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Destroy existing chart
        if (this.revenueChart) {
            this.revenueChart.destroy();
            this.revenueChart = null;
        }

        // Get revenue data
        let revenueData = window.__REVENUE_DATA__ || [0, 0, 0];
        revenueData = revenueData.map(v => Number(v) || 0);

        const labels = [];
        const values = [];
        const colors = [];
        const colorMap = ['#6366f1', '#10b981', '#f59e0b'];
        const labelMap = ['VIP Packages', 'Donations', 'Vouchers'];

        revenueData.forEach((val, index) => {
            if (val > 0) {
                labels.push(labelMap[index]);
                values.push(val);
                colors.push(colorMap[index]);
            }
        });

        // If all data is zero, show placeholder
        if (values.length === 0) {
            labels.push('No Data Available');
            values.push(1);
            colors.push('#94a3b8');
        }

        // Create chart
        this.revenueChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                    borderWidth: 0,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: { size: 12 }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const val = context.raw || 0;
                                const total = values.reduce((a, b) => a + b, 0);
                                const percentage = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                                
                                if (context.label === 'No Data Available') {
                                    return 'No revenue data available';
                                }
                                
                                return context.label + ': Rp ' + 
                                       val.toLocaleString('id-ID') + 
                                       ' (' + percentage + '%)';
                            }
                        }
                    }
                },
                cutout: '65%'
            }
        });

        console.log('Revenue pie chart created');
    },

    // Handle window resize
    handleResize: function() {
        if (this.currentChart) this.currentChart.resize();
        if (this.revenueChart) this.revenueChart.resize();
    },

    // Update charts with new data
    update: function(chartData, revenueData) {
        if (this.currentChart && chartData) {
            this.currentChart.data.labels = chartData.labels || this.currentChart.data.labels;
            this.currentChart.data.datasets[0].data = chartData.values || this.currentChart.data.datasets[0].data;
            this.currentChart.update();
        }

        if (this.revenueChart && revenueData) {
            window.__REVENUE_DATA__ = revenueData;
            this.initRevenuePieChart();
        }
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Give a small delay to ensure data is loaded
    setTimeout(() => {
        Charts.init();
    }, 200);
});

// Make globally accessible
window.Charts = Charts;
window.currentChart = Charts.currentChart;
window.revenueChart = Charts.revenueChart;
window.initCharts = () => Charts.init();