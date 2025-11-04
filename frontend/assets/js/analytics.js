// analytics.js - Analytics management for iReport
class AnalyticsManager {
    constructor() {
        this.currentFilters = {
            date_range: '7d',
            crime_type: '',
            priority: '',
            location: ''
        };
        this.analyticsData = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadAnalytics();
        this.initializeCharts();
    }

    // Setup event listeners
    setupEventListeners() {
        // Filter forms
        const filterForm = document.getElementById('analyticsFilters');
        if (filterForm) {
            filterForm.addEventListener('submit', (e) => this.handleFilter(e));
            filterForm.addEventListener('reset', (e) => this.handleResetFilters(e));
        }

        // Date range selector
        const dateRangeSelect = document.getElementById('analyticsDateRange');
        if (dateRangeSelect) {
            dateRangeSelect.addEventListener('change', (e) => this.handleDateRangeChange(e));
        }

        // Export buttons
        const exportButtons = document.querySelectorAll('.export-analytics');
        exportButtons.forEach(btn => {
            btn.addEventListener('click', (e) => this.handleExport(e));
        });

        // Tab navigation
        const analyticsTabs = document.querySelectorAll('.analytics-nav .nav-link');
        analyticsTabs.forEach(tab => {
            tab.addEventListener('click', (e) => this.handleTabChange(e));
        });

        // Refresh button
        const refreshBtn = document.getElementById('refreshAnalytics');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadAnalytics());
        }
    }

    // Initialize charts
    initializeCharts() {
        // Initialize Chart.js instances
        this.charts = {
            trends: null,
            crimeTypes: null,
            priorities: null,
            heatmap: null,
            performance: null
        };
    }

    // Load analytics data
    async loadAnalytics() {
        try {
            APP_UTILS.Notification.showLoading('Loading analytics...');

            let response;
            if (isAdmin()) {
                response = await API_SERVICE.getAdminAnalyticsOverview();
            } else if (isPolice()) {
                response = await API_SERVICE.getPerformanceMetrics();
            } else {
                response = await API_SERVICE.getTrendAnalytics(this.currentFilters);
            }

            if (response.success) {
                this.analyticsData = response.data;
                this.renderAnalytics();
                this.updateCharts();
            } else {
                throw new Error(response.message || 'Failed to load analytics');
            }

        } catch (error) {
            console.error('Load analytics error:', error);
            APP_UTILS.Notification.showToast(
                APP_UTILS.API.handleError(error, 'Failed to load analytics.'),
                'error'
            );
        } finally {
            APP_UTILS.Notification.hideLoading();
        }
    }

    // Render analytics based on user role
    renderAnalytics() {
        if (!this.analyticsData) return;

        if (isAdmin()) {
            this.renderAdminAnalytics();
        } else if (isPolice()) {
            this.renderPoliceAnalytics();
        } else {
            this.renderPublicAnalytics();
        }
    }

    // Render admin analytics
    renderAdminAnalytics() {
        const container = document.getElementById('analyticsContent');
        if (!container) return;

        const data = this.analyticsData;

        container.innerHTML = `
            <div class="row">
                <!-- Key Metrics -->
                <div class="col-12">
                    <div class="row" id="analyticsMetrics"></div>
                </div>

                <!-- Main Charts -->
                <div class="col-lg-8">
                    <!-- Trends Chart -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Complaints Trend</h5>
                        </div>
                        <div class="card-body">
                            <canvas id="trendsChart" height="300"></canvas>
                        </div>
                    </div>

                    <!-- Performance Metrics -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Officer Performance</h5>
                        </div>
                        <div class="card-body">
                            <canvas id="performanceChart" height="300"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Sidebar -->
                <div class="col-lg-4">
                    <!-- Crime Distribution -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Crime Type Distribution</h5>
                        </div>
                        <div class="card-body">
                            <canvas id="crimeTypesChart" height="250"></canvas>
                        </div>
                    </div>

                    <!-- Priority Distribution -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Priority Distribution</h5>
                        </div>
                        <div class="card-body">
                            <canvas id="priorityChart" height="250"></canvas>
                        </div>
                    </div>

                    <!-- High Risk Areas -->
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">High Risk Areas</h5>
                        </div>
                        <div class="card-body">
                            ${this.renderHighRiskAreas(data.high_risk_areas)}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Predictive Insights -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Predictive Insights</h5>
                        </div>
                        <div class="card-body">
                            ${this.renderPredictiveInsights(data.predictive_insights)}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Render police analytics
    renderPoliceAnalytics() {
        const container = document.getElementById('analyticsContent');
        if (!container) return;

        const data = this.analyticsData;

        container.innerHTML = `
            <div class="row">
                <!-- Performance Metrics -->
                <div class="col-12">
                    <div class="row" id="analyticsMetrics"></div>
                </div>

                <!-- Main Content -->
                <div class="col-lg-8">
                    <!-- Case Resolution Trends -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Case Resolution Trends</h5>
                        </div>
                        <div class="card-body">
                            <canvas id="trendsChart" height="300"></canvas>
                        </div>
                    </div>

                    <!-- Team Performance -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Team Performance</h5>
                        </div>
                        <div class="card-body">
                            <canvas id="performanceChart" height="300"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Sidebar -->
                <div class="col-lg-4">
                    <!-- Patrol Recommendations -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Patrol Recommendations</h5>
                        </div>
                        <div class="card-body">
                            ${this.renderPatrolRecommendations(data.patrol_recommendations)}
                        </div>
                    </div>

                    <!-- Heatmap -->
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Crime Heatmap</h5>
                        </div>
                        <div class="card-body">
                            <div id="heatmapContainer" style="height: 300px;">
                                <canvas id="heatmapChart" height="300"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Render public analytics (limited view)
    renderPublicAnalytics() {
        const container = document.getElementById('analyticsContent');
        if (!container) return;

        const data = this.analyticsData;

        container.innerHTML = `
            <div class="row">
                <!-- Public Statistics -->
                <div class="col-12">
                    <div class="row" id="analyticsMetrics"></div>
                </div>

                <!-- Crime Trends -->
                <div class="col-lg-8">
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Community Crime Trends</h5>
                        </div>
                        <div class="card-body">
                            <canvas id="trendsChart" height="300"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Crime Distribution -->
                <div class="col-lg-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Crime Type Distribution</h5>
                        </div>
                        <div class="card-body">
                            <canvas id="crimeTypesChart" height="250"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Safety Tips -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Safety Tips</h5>
                        </div>
                        <div class="card-body">
                            ${this.renderSafetyTips()}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Update analytics metrics
    updateAnalyticsMetrics() {
        const metricsContainer = document.getElementById('analyticsMetrics');
        if (!metricsContainer || !this.analyticsData) return;

        const metrics = this.analyticsData.metrics || {};
        const role = getUserRole();

        let metricsConfig = [];

        if (role === 'admin') {
            metricsConfig = [
                { key: 'total_cases', label: 'Total Cases', icon: 'fas fa-clipboard-list', color: 'primary' },
                { key: 'resolution_rate', label: 'Resolution Rate', icon: 'fas fa-chart-line', color: 'success', suffix: '%' },
                { key: 'avg_response_time', label: 'Avg Response Time', icon: 'fas fa-stopwatch', color: 'info', suffix: 'h' },
                { key: 'high_risk_locations', label: 'High Risk Areas', icon: 'fas fa-map-marker-alt', color: 'warning' },
                { key: 'officer_performance', label: 'Officer Performance', icon: 'fas fa-user-shield', color: 'secondary', suffix: '%' },
                { key: 'citizen_satisfaction', label: 'Citizen Satisfaction', icon: 'fas fa-smile', color: 'success', suffix: '%' }
            ];
        } else if (role === 'police') {
            metricsConfig = [
                { key: 'cases_resolved', label: 'Cases Resolved', icon: 'fas fa-check-circle', color: 'success' },
                { key: 'resolution_rate', label: 'My Resolution Rate', icon: 'fas fa-chart-line', color: 'primary', suffix: '%' },
                { key: 'avg_response_time', label: 'My Response Time', icon: 'fas fa-stopwatch', color: 'info', suffix: 'h' },
                { key: 'team_performance', label: 'Team Performance', icon: 'fas fa-users', color: 'secondary', suffix: '%' },
                { key: 'high_priority_cases', label: 'High Priority', icon: 'fas fa-exclamation-triangle', color: 'warning' },
                { key: 'patrol_efficiency', label: 'Patrol Efficiency', icon: 'fas fa-map-marked-alt', color: 'success', suffix: '%' }
            ];
        } else {
            metricsConfig = [
                { key: 'community_cases', label: 'Community Cases', icon: 'fas fa-clipboard-list', color: 'primary' },
                { key: 'resolution_rate', label: 'Resolution Rate', icon: 'fas fa-chart-line', color: 'success', suffix: '%' },
                { key: 'common_crime_type', label: 'Most Common Crime', icon: 'fas fa-shield-alt', color: 'info' },
                { key: 'safety_index', label: 'Safety Index', icon: 'fas fa-chart-pie', color: 'warning', suffix: '/100' },
                { key: 'response_efficiency', label: 'Response Efficiency', icon: 'fas fa-bolt', color: 'success', suffix: '%' },
                { key: 'prevention_tips', label: 'Prevention Tips', icon: 'fas fa-lightbulb', color: 'secondary' }
            ];
        }

        const metricsHTML = metricsConfig.map(metric => {
            let value = metrics[metric.key] || 'N/A';
            
            // Handle special cases for public metrics
            if (role === 'public') {
                if (metric.key === 'common_crime_type' && value !== 'N/A') {
                    value = APP_UTILS.CrimeReport.getCrimeTypeDisplay(value);
                }
                if (metric.key === 'prevention_tips') {
                    value = 'Available';
                }
            }

            return `
                <div class="col-md-4 col-lg-2 mb-4">
                    <div class="card metric-card text-center">
                        <div class="card-body">
                            <i class="${metric.icon} fa-2x text-${metric.color} mb-2"></i>
                            <h3 class="card-title">${value}${metric.suffix || ''}</h3>
                            <p class="card-text text-muted">${metric.label}</p>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        metricsContainer.innerHTML = metricsHTML;
    }

    // Update charts with data
    updateCharts() {
        if (!this.analyticsData) return;

        // This would update Chart.js instances with actual data
        // For now, we'll create placeholder chart rendering
        this.renderTrendsChart();
        this.renderCrimeTypesChart();
        this.renderPriorityChart();
        
        if (isAdmin() || isPolice()) {
            this.renderPerformanceChart();
        }
        
        if (isPolice()) {
            this.renderHeatmap();
        }
    }

    // Render trends chart
    renderTrendsChart() {
        const ctx = document.getElementById('trendsChart');
        if (!ctx) return;

        const trendsData = this.analyticsData.trends || this.generateSampleTrendsData();
        
        // This would use Chart.js to render the chart
        console.log('Rendering trends chart with data:', trendsData);
    }

    // Render crime types chart
    renderCrimeTypesChart() {
        const ctx = document.getElementById('crimeTypesChart');
        if (!ctx) return;

        const crimeData = this.analyticsData.crime_distribution || this.generateSampleCrimeData();
        
        // This would use Chart.js to render the chart
        console.log('Rendering crime types chart with data:', crimeData);
    }

    // Render priority chart
    renderPriorityChart() {
        const ctx = document.getElementById('priorityChart');
        if (!ctx) return;

        const priorityData = this.analyticsData.priority_distribution || this.generateSamplePriorityData();
        
        // This would use Chart.js to render the chart
        console.log('Rendering priority chart with data:', priorityData);
    }

    // Render performance chart
    renderPerformanceChart() {
        const ctx = document.getElementById('performanceChart');
        if (!ctx) return;

        const performanceData = this.analyticsData.performance || this.generateSamplePerformanceData();
        
        // This would use Chart.js to render the chart
        console.log('Rendering performance chart with data:', performanceData);
    }

    // Render heatmap
    renderHeatmap() {
        const ctx = document.getElementById('heatmapChart');
        if (!ctx) return;

        const heatmapData = this.analyticsData.heatmap || this.generateSampleHeatmapData();
        
        // This would render a heatmap chart
        console.log('Rendering heatmap with data:', heatmapData);
    }

    // Render high risk areas
    renderHighRiskAreas(areas) {
        if (!areas || areas.length === 0) {
            return '<p class="text-muted text-center">No high risk areas identified</p>';
        }

        return areas.map(area => `
            <div class="high-risk-area mb-3 p-3 border rounded">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">${area.location}</h6>
                        <p class="mb-1 text-muted">${area.crime_type} • ${area.incident_count} incidents</p>
                        <small class="text-muted">Risk Level: ${area.risk_level}/10</small>
                    </div>
                    <span class="badge bg-${this.getRiskLevelColor(area.risk_level)}">
                        ${area.risk_level}/10
                    </span>
                </div>
                <div class="mt-2">
                    <small class="text-muted">Recommendation: ${area.recommendation}</small>
                </div>
            </div>
        `).join('');
    }

    // Render patrol recommendations
    renderPatrolRecommendations(recommendations) {
        if (!recommendations || recommendations.length === 0) {
            return '<p class="text-muted text-center">No patrol recommendations</p>';
        }

        return recommendations.map(rec => `
            <div class="patrol-recommendation mb-3 p-3 border rounded">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">${rec.area}</h6>
                        <p class="mb-1 text-muted">Priority: ${rec.priority}</p>
                        <small class="text-muted">Recommended: ${rec.patrol_time}</small>
                    </div>
                    <i class="fas fa-map-marker-alt text-${rec.priority === 'high' ? 'danger' : 'warning'}"></i>
                </div>
                <div class="mt-2">
                    <small class="text-muted">${rec.reason}</small>
                </div>
            </div>
        `).join('');
    }

    // Render predictive insights
    renderPredictiveInsights(insights) {
        if (!insights || insights.length === 0) {
            return '<p class="text-muted text-center">No predictive insights available</p>';
        }

        return insights.map(insight => `
            <div class="predictive-insight mb-3 p-3 border rounded">
                <div class="d-flex align-items-start">
                    <i class="fas ${this.getInsightIcon(insight.type)} fa-2x text-${this.getInsightColor(insight.type)} me-3 mt-1"></i>
                    <div>
                        <h6 class="mb-1">${insight.title}</h6>
                        <p class="mb-1">${insight.description}</p>
                        <small class="text-muted">
                            Confidence: ${insight.confidence}% • 
                            Timeframe: ${insight.timeframe}
                        </small>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // Render safety tips
    renderSafetyTips() {
        const safetyTips = [
            "Always be aware of your surroundings",
            "Avoid walking alone in poorly lit areas",
            "Keep valuable items out of sight",
            "Report suspicious activities immediately",
            "Use well-traveled routes, especially at night",
            "Keep emergency numbers saved in your phone",
            "Trust your instincts - if something feels wrong, it probably is"
        ];

        return `
            <div class="row">
                ${safetyTips.map((tip, index) => `
                    <div class="col-md-6 mb-3">
                        <div class="safety-tip p-3 border rounded">
                            <i class="fas fa-lightbulb text-warning me-2"></i>
                            ${tip}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    // Get risk level color
    getRiskLevelColor(level) {
        if (level >= 8) return 'danger';
        if (level >= 6) return 'warning';
        if (level >= 4) return 'info';
        return 'success';
    }

    // Get insight icon
    getInsightIcon(type) {
        const icons = {
            'crime_spike': 'fa-chart-line',
            'pattern': 'fa-project-diagram',
            'prevention': 'fa-shield-alt',
            'efficiency': 'fa-bolt',
            'trend': 'fa-chart-bar'
        };
        return icons[type] || 'fa-chart-pie';
    }

    // Get insight color
    getInsightColor(type) {
        const colors = {
            'crime_spike': 'danger',
            'pattern': 'warning',
            'prevention': 'success',
            'efficiency': 'info',
            'trend': 'primary'
        };
        return colors[type] || 'secondary';
    }

    // Handle filter application
    handleFilter(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = APP_UTILS.Form.serializeForm(form);
        
        this.currentFilters = {
            ...this.currentFilters,
            ...formData
        };
        
        this.loadAnalytics();
    }

    // Handle reset filters
    handleResetFilters(e) {
        e.preventDefault();
        
        this.currentFilters = {
            date_range: '7d',
            crime_type: '',
            priority: '',
            location: ''
        };
        
        this.loadAnalytics();
    }

    // Handle date range change
    handleDateRangeChange(e) {
        this.currentFilters.date_range = e.target.value;
        this.loadAnalytics();
    }

    // Handle export
    handleExport(e) {
        const format = e.target.getAttribute('data-format');
        const type = e.target.getAttribute('data-type');
        
        if (format === 'csv') {
            APP_UTILS.Export.exportToCSV(this.analyticsData, `analytics-${type}.csv`);
        } else if (format === 'json') {
            APP_UTILS.Export.exportToJSON(this.analyticsData, `analytics-${type}.json`);
        } else if (format === 'pdf') {
            APP_UTILS.Export.printElement('analyticsContent');
        }
    }

    // Handle tab change
    handleTabChange(e) {
        e.preventDefault();
        
        const target = e.target.getAttribute('data-target');
        if (!target) return;
        
        // Update active tab
        const tabs = document.querySelectorAll('.analytics-nav .nav-link');
        tabs.forEach(tab => tab.classList.remove('active'));
        e.target.classList.add('active');
        
        // Show/hide content sections
        const sections = document.querySelectorAll('.analytics-section');
        sections.forEach(section => {
            if (section.id === `${target}Section`) {
                APP_UTILS.DOM.show(section);
            } else {
                APP_UTILS.DOM.hide(section);
            }
        });
        
        // Load section-specific data if needed
        this.loadSectionData(target);
    }

    // Load section-specific data
    async loadSectionData(section) {
        try {
            APP_UTILS.Notification.showLoading(`Loading ${section} data...`);
            
            let response;
            switch (section) {
                case 'trends':
                    response = await API_SERVICE.getTrendAnalytics(this.currentFilters);
                    break;
                case 'heatmap':
                    response = await API_SERVICE.getHeatmapData();
                    break;
                case 'performance':
                    response = isAdmin() ? 
                        await API_SERVICE.getOfficerPerformanceAnalytics() :
                        await API_SERVICE.getPerformanceMetrics();
                    break;
                case 'predictive':
                    response = await API_SERVICE.getPredictiveInsights();
                    break;
                default:
                    return;
            }
            
            if (response.success) {
                this.analyticsData[section] = response.data;
                this.updateSectionCharts(section);
            } else {
                throw new Error(response.message || `Failed to load ${section} data`);
            }
            
        } catch (error) {
            console.error(`Load ${section} data error:`, error);
            APP_UTILS.Notification.showToast(
                APP_UTILS.API.handleError(error, `Failed to load ${section} data.`),
                'error'
            );
        } finally {
            APP_UTILS.Notification.hideLoading();
        }
    }

    // Update section-specific charts
    updateSectionCharts(section) {
        // This would update charts for the specific section
        console.log(`Updating ${section} charts`);
    }

    // Generate sample data for demonstration
    generateSampleTrendsData() {
        return {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Complaints',
                data: [65, 59, 80, 81, 56, 55],
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        };
    }

    generateSampleCrimeData() {
        return {
            labels: ['Theft', 'Burglary', 'Assault', 'Fraud', 'Other'],
            datasets: [{
                data: [30, 25, 15, 20, 10],
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'
                ]
            }]
        };
    }

    generateSamplePriorityData() {
        return {
            labels: ['Low', 'Medium', 'High', 'Critical'],
            datasets: [{
                data: [40, 30, 20, 10],
                backgroundColor: [
                    '#28a745', '#ffc107', '#fd7e14', '#dc3545'
                ]
            }]
        };
    }

    generateSamplePerformanceData() {
        return {
            labels: ['Officer A', 'Officer B', 'Officer C', 'Officer D'],
            datasets: [{
                label: 'Resolution Rate (%)',
                data: [85, 78, 92, 88],
                backgroundColor: 'rgba(54, 162, 235, 0.5)'
            }]
        };
    }

    generateSampleHeatmapData() {
        return {
            // This would be geographic heatmap data
            locations: [
                { lat: 28.6139, lng: 77.2090, intensity: 0.8 },
                { lat: 28.6129, lng: 77.2290, intensity: 0.6 },
                { lat: 28.6149, lng: 77.2190, intensity: 0.9 }
            ]
        };
    }
}

// Initialize Analytics Manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.analyticsManager = new AnalyticsManager();
});