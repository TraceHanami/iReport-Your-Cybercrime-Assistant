// dashboard.js - Dashboard management for iReport
class DashboardManager {
    constructor() {
        this.currentView = 'overview';
        this.dashboardData = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboard();
        this.initializeCharts();
    }

    // Setup event listeners
    setupEventListeners() {
        // Navigation tabs
        const navTabs = document.querySelectorAll('.dashboard-nav .nav-link');
        navTabs.forEach(tab => {
            tab.addEventListener('click', (e) => this.handleNavigation(e));
        });

        // Refresh button
        const refreshBtn = document.getElementById('refreshDashboard');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadDashboard());
        }

        // Date range filters
        const dateRangeSelect = document.getElementById('dateRange');
        if (dateRangeSelect) {
            dateRangeSelect.addEventListener('change', (e) => this.handleDateRangeChange(e));
        }

        // Export buttons
        const exportButtons = document.querySelectorAll('.export-btn');
        exportButtons.forEach(btn => {
            btn.addEventListener('click', (e) => this.handleExport(e));
        });

        // Quick action buttons
        const quickActionButtons = document.querySelectorAll('.quick-action-btn');
        quickActionButtons.forEach(btn => {
            btn.addEventListener('click', (e) => this.handleQuickAction(e));
        });
    }

    // Initialize charts
    initializeCharts() {
        // This would initialize Chart.js or other charting library
        // For now, we'll create placeholder functions
        this.charts = {};
    }

    // Load dashboard data
    async loadDashboard() {
        try {
            APP_UTILS.Notification.showLoading('Loading dashboard...');

            let response;
            if (isAdmin()) {
                response = await API_SERVICE.getAdminDashboard();
            } else if (isPolice()) {
                response = await API_SERVICE.getPoliceDashboard();
            } else {
                // For citizens, use their complaints as dashboard data
                response = await API_SERVICE.getMyComplaints({ limit: 10 });
            }

            if (response.success) {
                this.dashboardData = response.data;
                this.renderDashboard();
                this.updateCharts();
            } else {
                throw new Error(response.message || 'Failed to load dashboard');
            }

        } catch (error) {
            console.error('Load dashboard error:', error);
            APP_UTILS.Notification.showToast(
                APP_UTILS.API.handleError(error, 'Failed to load dashboard.'),
                'error'
            );
        } finally {
            APP_UTILS.Notification.hideLoading();
        }
    }

    // Render dashboard based on user role
    renderDashboard() {
        if (!this.dashboardData) return;

        if (isAdmin()) {
            this.renderAdminDashboard();
        } else if (isPolice()) {
            this.renderPoliceDashboard();
        } else {
            this.renderCitizenDashboard();
        }

        this.updateStatsCards();
        this.renderRecentActivity();
    }

    // Render admin dashboard
    renderAdminDashboard() {
        const container = document.getElementById('dashboardContent');
        if (!container) return;

        const data = this.dashboardData;

        container.innerHTML = `
            <div class="row">
                <!-- Statistics Cards -->
                <div class="col-12">
                    <div class="row" id="statsCards"></div>
                </div>

                <!-- Charts Row -->
                <div class="col-lg-8">
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Complaints Overview</h5>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="complaintsChart" height="300"></canvas>
                            </div>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-6">
                            <div class="card mb-4">
                                <div class="card-header">
                                    <h5 class="card-title mb-0">Crime Types Distribution</h5>
                                </div>
                                <div class="card-body">
                                    <canvas id="crimeTypesChart" height="250"></canvas>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card mb-4">
                                <div class="card-header">
                                    <h5 class="card-title mb-0">Priority Distribution</h5>
                                </div>
                                <div class="card-body">
                                    <canvas id="priorityChart" height="250"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Sidebar -->
                <div class="col-lg-4">
                    <!-- System Status -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="card-title mb-0">System Status</h5>
                        </div>
                        <div class="card-body">
                            ${this.renderSystemStatus(data.system_status)}
                        </div>
                    </div>

                    <!-- Recent Activity -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Recent Activity</h5>
                        </div>
                        <div class="card-body">
                            <div id="recentActivity"></div>
                        </div>
                    </div>

                    <!-- Quick Actions -->
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Quick Actions</h5>
                        </div>
                        <div class="card-body">
                            <div class="d-grid gap-2">
                                <button class="btn btn-outline-primary quick-action-btn" data-action="manageUsers">
                                    <i class="fas fa-users me-2"></i>Manage Users
                                </button>
                                <button class="btn btn-outline-primary quick-action-btn" data-action="assignCases">
                                    <i class="fas fa-tasks me-2"></i>Assign Cases
                                </button>
                                <button class="btn btn-outline-primary quick-action-btn" data-action="viewReports">
                                    <i class="fas fa-chart-bar me-2"></i>View Reports
                                </button>
                                <button class="btn btn-outline-primary quick-action-btn" data-action="systemSettings">
                                    <i class="fas fa-cog me-2"></i>System Settings
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Render police dashboard
    renderPoliceDashboard() {
        const container = document.getElementById('dashboardContent');
        if (!container) return;

        const data = this.dashboardData;

        container.innerHTML = `
            <div class="row">
                <!-- Statistics Cards -->
                <div class="col-12">
                    <div class="row" id="statsCards"></div>
                </div>

                <!-- Main Content -->
                <div class="col-lg-8">
                    <!-- Assigned Cases -->
                    <div class="card mb-4">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="card-title mb-0">My Assigned Cases</h5>
                            <a href="police-cases.html" class="btn btn-sm btn-outline-primary">View All</a>
                        </div>
                        <div class="card-body">
                            ${this.renderAssignedCases(data.assigned_cases)}
                        </div>
                    </div>

                    <!-- Performance Metrics -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Performance Metrics</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="metric-card text-center">
                                        <h3 class="text-primary">${data.performance?.response_time || '0'}h</h3>
                                        <p class="text-muted">Avg. Response Time</p>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="metric-card text-center">
                                        <h3 class="text-success">${data.performance?.resolution_rate || '0'}%</h3>
                                        <p class="text-muted">Resolution Rate</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Sidebar -->
                <div class="col-lg-4">
                    <!-- Today's Schedule -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Today's Schedule</h5>
                        </div>
                        <div class="card-body">
                            ${this.renderSchedule(data.schedule)}
                        </div>
                    </div>

                    <!-- Quick Actions -->
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Quick Actions</h5>
                        </div>
                        <div class="card-body">
                            <div class="d-grid gap-2">
                                <button class="btn btn-outline-primary quick-action-btn" data-action="updateCases">
                                    <i class="fas fa-edit me-2"></i>Update Cases
                                </button>
                                <button class="btn btn-outline-primary quick-action-btn" data-action="fileReport">
                                    <i class="fas fa-file-alt me-2"></i>File Report
                                </button>
                                <button class="btn btn-outline-primary quick-action-btn" data-action="viewAnalytics">
                                    <i class="fas fa-chart-line me-2"></i>View Analytics
                                </button>
                                <button class="btn btn-outline-primary quick-action-btn" data-action="updateAvailability">
                                    <i class="fas fa-user-clock me-2"></i>Update Availability
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Render citizen dashboard
    renderCitizenDashboard() {
        const container = document.getElementById('dashboardContent');
        if (!container) return;

        const complaints = this.dashboardData.complaints || this.dashboardData;

        container.innerHTML = `
            <div class="row">
                <!-- Welcome Section -->
                <div class="col-12">
                    <div class="card bg-primary text-white mb-4">
                        <div class="card-body">
                            <div class="row align-items-center">
                                <div class="col-md-8">
                                    <h3 class="card-title">Welcome back, ${getUserDisplayName()}!</h3>
                                    <p class="card-text">Thank you for helping make our community safer.</p>
                                </div>
                                <div class="col-md-4 text-end">
                                    <i class="fas fa-shield-alt fa-4x opacity-50"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Quick Actions -->
                <div class="col-md-4 mb-4">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-plus-circle fa-3x text-primary mb-3"></i>
                            <h5>File New Complaint</h5>
                            <p class="text-muted">Report a crime or incident</p>
                            <a href="file-complaint.html" class="btn btn-primary">Get Started</a>
                        </div>
                    </div>
                </div>

                <div class="col-md-4 mb-4">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-search fa-3x text-info mb-3"></i>
                            <h5>Track Complaint</h5>
                            <p class="text-muted">Check status of your reports</p>
                            <a href="track-complaint.html" class="btn btn-info">Track Now</a>
                        </div>
                    </div>
                </div>

                <div class="col-md-4 mb-4">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-robot fa-3x text-success mb-3"></i>
                            <h5>Get Help</h5>
                            <p class="text-muted">Chat with our assistant</p>
                            <a href="chatbot.html" class="btn btn-success">Start Chat</a>
                        </div>
                    </div>
                </div>

                <!-- Recent Complaints -->
                <div class="col-12">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="card-title mb-0">My Recent Complaints</h5>
                            <a href="my-complaints.html" class="btn btn-sm btn-outline-primary">View All</a>
                        </div>
                        <div class="card-body">
                            ${this.renderRecentComplaints(complaints)}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Update statistics cards
    updateStatsCards() {
        const statsCards = document.getElementById('statsCards');
        if (!statsCards || !this.dashboardData) return;

        const stats = this.dashboardData.stats || {};
        const role = getUserRole();

        let statsConfig = [];

        if (role === 'admin') {
            statsConfig = [
                { key: 'total_complaints', label: 'Total Complaints', icon: 'fas fa-clipboard-list', color: 'primary' },
                { key: 'pending_complaints', label: 'Pending Cases', icon: 'fas fa-clock', color: 'warning' },
                { key: 'resolved_complaints', label: 'Resolved Cases', icon: 'fas fa-check-circle', color: 'success' },
                { key: 'total_users', label: 'Total Users', icon: 'fas fa-users', color: 'info' },
                { key: 'active_officers', label: 'Active Officers', icon: 'fas fa-shield-alt', color: 'secondary' },
                { key: 'response_time', label: 'Avg. Response Time', icon: 'fas fa-stopwatch', color: 'dark', suffix: 'h' }
            ];
        } else if (role === 'police') {
            statsConfig = [
                { key: 'assigned_cases', label: 'Assigned Cases', icon: 'fas fa-tasks', color: 'primary' },
                { key: 'pending_cases', label: 'Pending Cases', icon: 'fas fa-clock', color: 'warning' },
                { key: 'resolved_cases', label: 'Resolved Cases', icon: 'fas fa-check-circle', color: 'success' },
                { key: 'high_priority', label: 'High Priority', icon: 'fas fa-exclamation-triangle', color: 'danger' },
                { key: 'response_time', label: 'Avg. Response Time', icon: 'fas fa-stopwatch', color: 'info', suffix: 'h' },
                { key: 'resolution_rate', label: 'Resolution Rate', icon: 'fas fa-chart-line', color: 'secondary', suffix: '%' }
            ];
        } else {
            statsConfig = [
                { key: 'total_complaints', label: 'My Complaints', icon: 'fas fa-clipboard-list', color: 'primary' },
                { key: 'pending_complaints', label: 'Pending', icon: 'fas fa-clock', color: 'warning' },
                { key: 'resolved_complaints', label: 'Resolved', icon: 'fas fa-check-circle', color: 'success' },
                { key: 'high_priority', label: 'High Priority', icon: 'fas fa-exclamation-triangle', color: 'danger' }
            ];
        }

        const statsHTML = statsConfig.map(stat => {
            const value = stats[stat.key] || 0;
            return `
                <div class="col-md-4 col-lg-2 mb-4">
                    <div class="card stat-card border-${stat.color}">
                        <div class="card-body text-center">
                            <i class="${stat.icon} fa-2x text-${stat.color} mb-2"></i>
                            <h3 class="card-title">${value}${stat.suffix || ''}</h3>
                            <p class="card-text text-muted">${stat.label}</p>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        statsCards.innerHTML = statsHTML;
    }

    // Render recent activity
    renderRecentActivity() {
        const container = document.getElementById('recentActivity');
        if (!container || !this.dashboardData) return;

        const activities = this.dashboardData.recent_activity || [];
        
        if (activities.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">No recent activity</p>';
            return;
        }

        const activityHTML = activities.map(activity => `
            <div class="activity-item mb-3">
                <div class="d-flex">
                    <div class="activity-icon me-3">
                        <i class="fas ${this.getActivityIcon(activity.type)} text-${this.getActivityColor(activity.type)}"></i>
                    </div>
                    <div class="activity-content">
                        <p class="mb-1">${activity.description}</p>
                        <small class="text-muted">${APP_UTILS.Date.getRelativeTime(activity.timestamp)}</small>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = activityHTML;
    }

    // Render assigned cases for police
    renderAssignedCases(cases) {
        if (!cases || cases.length === 0) {
            return '<p class="text-muted text-center">No assigned cases</p>';
        }

        return cases.map(case_ => {
            const summary = APP_UTILS.CrimeReport.generateCaseSummary(case_);
            return `
                <div class="assigned-case mb-3 p-3 border rounded">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="mb-1">${summary.title}</h6>
                            <p class="mb-1 text-muted">${summary.crimeType} • ${summary.location}</p>
                            <small class="text-muted">Filed ${summary.relativeTime}</small>
                        </div>
                        <div class="text-end">
                            <span class="${summary.priorityClass}">${summary.priority}</span>
                            <br>
                            <span class="${summary.statusClass}">${summary.status}</span>
                        </div>
                    </div>
                    <div class="mt-2">
                        <button class="btn btn-sm btn-outline-primary update-case-btn" data-case-id="${summary.id}">
                            Update Case
                        </button>
                        <button class="btn btn-sm btn-outline-info view-details-btn" data-case-id="${summary.id}">
                            View Details
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }

    // Render schedule for police
    renderSchedule(schedule) {
        if (!schedule || schedule.length === 0) {
            return '<p class="text-muted text-center">No schedule for today</p>';
        }

        return schedule.map(item => `
            <div class="schedule-item mb-2 p-2 border-start border-3 border-primary">
                <div class="d-flex justify-content-between">
                    <strong>${item.title}</strong>
                    <span class="text-muted">${item.time}</span>
                </div>
                <small class="text-muted">${item.location}</small>
            </div>
        `).join('');
    }

    // Render recent complaints for citizens
    renderRecentComplaints(complaints) {
        if (!complaints || complaints.length === 0) {
            return '<p class="text-muted text-center">You haven\'t filed any complaints yet</p>';
        }

        return complaints.map(complaint => {
            const summary = APP_UTILS.CrimeReport.generateCaseSummary(complaint);
            return `
                <div class="recent-complaint mb-3 p-3 border rounded">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="mb-1">${summary.title}</h6>
                            <p class="mb-1 text-muted">${summary.crimeType} • ${summary.location}</p>
                            <small class="text-muted">Filed ${summary.relativeTime}</small>
                        </div>
                        <div class="text-end">
                            <span class="${summary.statusClass}">${summary.status}</span>
                        </div>
                    </div>
                    <div class="mt-2">
                        <button class="btn btn-sm btn-outline-info track-complaint-btn" data-case-id="${summary.id}">
                            Track Status
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }

    // Render system status
    renderSystemStatus(status) {
        if (!status) return '<p class="text-muted">System status unavailable</p>';

        const statusItems = [
            { key: 'api', label: 'API Server', icon: 'fas fa-server' },
            { key: 'database', label: 'Database', icon: 'fas fa-database' },
            { key: 'sms', label: 'SMS Service', icon: 'fas fa-sms' },
            { key: 'storage', label: 'File Storage', icon: 'fas fa-hdd' }
        ];

        return statusItems.map(item => {
            const isOnline = status[item.key];
            return `
                <div class="system-status-item d-flex justify-content-between align-items-center mb-2">
                    <div>
                        <i class="${item.icon} me-2"></i>
                        <span>${item.label}</span>
                    </div>
                    <span class="badge bg-${isOnline ? 'success' : 'danger'}">
                        ${isOnline ? 'Online' : 'Offline'}
                    </span>
                </div>
            `;
        }).join('');
    }

    // Get activity icon
    getActivityIcon(activityType) {
        const icons = {
            'complaint_filed': 'fa-clipboard-list',
            'case_assigned': 'fa-user-plus',
            'status_updated': 'fa-sync-alt',
            'case_resolved': 'fa-check-circle',
            'user_registered': 'fa-user-plus',
            'system_alert': 'fa-bell'
        };
        return icons[activityType] || 'fa-circle';
    }

    // Get activity color
    getActivityColor(activityType) {
        const colors = {
            'complaint_filed': 'primary',
            'case_assigned': 'info',
            'status_updated': 'warning',
            'case_resolved': 'success',
            'user_registered': 'secondary',
            'system_alert': 'danger'
        };
        return colors[activityType] || 'muted';
    }

    // Update charts
    updateCharts() {
        // This would update Chart.js charts with actual data
        // For now, this is a placeholder
        console.log('Updating charts with data:', this.dashboardData);
    }

    // Handle navigation
    handleNavigation(e) {
        e.preventDefault();
        
        const target = e.target.getAttribute('data-target');
        if (!target) return;
        
        this.currentView = target;
        
        // Update active tab
        const navTabs = document.querySelectorAll('.dashboard-nav .nav-link');
        navTabs.forEach(tab => tab.classList.remove('active'));
        e.target.classList.add('active');
        
        // Load view-specific data
        this.loadViewData(target);
    }

    // Handle date range change
    handleDateRangeChange(e) {
        const range = e.target.value;
        this.currentFilters.date_range = range;
        this.loadDashboard();
    }

    // Handle export
    handleExport(e) {
        const format = e.target.getAttribute('data-format');
        const type = e.target.getAttribute('data-type');
        
        if (format === 'csv') {
            APP_UTILS.Export.exportToCSV(this.dashboardData, `dashboard-${type}.csv`);
        } else if (format === 'json') {
            APP_UTILS.Export.exportToJSON(this.dashboardData, `dashboard-${type}.json`);
        }
    }

    // Handle quick action
    handleQuickAction(e) {
        const action = e.target.getAttribute('data-action');
        
        const actionHandlers = {
            'manageUsers': () => window.location.href = 'manage-users.html',
            'assignCases': () => window.location.href = 'case-assignment.html',
            'viewReports': () => window.location.href = 'reports.html',
            'systemSettings': () => window.location.href = 'system-settings.html',
            'updateCases': () => window.location.href = 'police-cases.html',
            'fileReport': () => window.location.href = 'file-report.html',
            'viewAnalytics': () => window.location.href = 'analytics.html',
            'updateAvailability': () => this.updateAvailability()
        };
        
        if (actionHandlers[action]) {
            actionHandlers[action]();
        }
    }

    // Update police availability
    async updateAvailability() {
        const newStatus = prompt('Enter your availability status (available, busy, offline):', 'available');
        
        if (!newStatus || !['available', 'busy', 'offline'].includes(newStatus)) {
            APP_UTILS.Notification.showToast('Invalid status', 'error');
            return;
        }
        
        try {
            APP_UTILS.Notification.showLoading('Updating availability...');
            
            const result = await API_SERVICE.updateAvailability({
                status: newStatus
            });
            
            if (result.success) {
                APP_UTILS.Notification.showToast('Availability updated successfully!', 'success');
            } else {
                throw new Error(result.message || 'Failed to update availability');
            }
            
        } catch (error) {
            console.error('Update availability error:', error);
            APP_UTILS.Notification.showToast(
                APP_UTILS.API.handleError(error, 'Failed to update availability.'),
                'error'
            );
        } finally {
            APP_UTILS.Notification.hideLoading();
        }
    }

    // Load view-specific data
    async loadViewData(view) {
        // This would load additional data for specific views
        // For now, we'll just update the URL
        window.history.pushState({}, '', `#${view}`);
    }
}

// Initialize Dashboard Manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.dashboardManager = new DashboardManager();
});