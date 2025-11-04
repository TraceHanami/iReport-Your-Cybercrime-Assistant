// police.js - Police management for iReport
class PoliceManager {
    constructor() {
        this.currentView = 'dashboard';
        this.assignedCases = [];
        this.init();
    }

    init() {
        if (!isPolice() && !isAdmin()) {
            window.location.href = 'unauthorized.html';
            return;
        }

        this.setupEventListeners();
        this.loadPoliceData();
        this.initializeComponents();
    }

    setupEventListeners() {
        // Police navigation
        const policeNavItems = document.querySelectorAll('.police-nav-item');
        policeNavItems.forEach(item => {
            item.addEventListener('click', (e) => this.handleNavigation(e));
        });

        // Case management
        const caseSearch = document.getElementById('caseSearch');
        if (caseSearch) {
            APP_UTILS.DOM.debouncedEventListener(caseSearch, 'input', 
                (e) => this.handleCaseSearch(e), 500);
        }

        // Update case status
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('update-case-status')) {
                this.handleUpdateCaseStatus(e);
            }
        });

        // Case filters
        const caseFilters = document.getElementById('caseFilters');
        if (caseFilters) {
            caseFilters.addEventListener('change', (e) => this.handleCaseFilter(e));
        }

        // Availability toggle
        const availabilityToggle = document.getElementById('availabilityToggle');
        if (availabilityToggle) {
            availabilityToggle.addEventListener('change', (e) => this.handleAvailabilityToggle(e));
        }

        // Report generation
        const generateReportBtn = document.getElementById('generateReport');
        if (generateReportBtn) {
            generateReportBtn.addEventListener('click', () => this.generateDailyReport());
        }
    }

    initializeComponents() {
        this.initializeMaps();
        this.initializeCharts();
    }

    initializeMaps() {
        // Initialize maps for patrol areas if needed
    }

    initializeCharts() {
        // Initialize police-specific charts
    }

    async loadPoliceData() {
        try {
            APP_UTILS.Notification.showLoading('Loading police data...');

            const [dashboardData, casesData, performanceData] = await Promise.all([
                API_SERVICE.getPoliceDashboard(),
                API_SERVICE.getPoliceCases(),
                API_SERVICE.getOfficerPerformance()
            ]);

            if (dashboardData.success) {
                this.policeData = dashboardData.data;
                this.renderPoliceDashboard();
            }

            if (casesData.success) {
                this.assignedCases = casesData.data.cases || casesData.data;
                this.renderAssignedCases();
            }

            if (performanceData.success) {
                this.performanceData = performanceData.data;
                this.renderPerformanceMetrics();
            }

        } catch (error) {
            console.error('Load police data error:', error);
            APP_UTILS.Notification.showToast(
                APP_UTILS.API.handleError(error, 'Failed to load police data.'),
                'error'
            );
        } finally {
            APP_UTILS.Notification.hideLoading();
        }
    }

    handleNavigation(e) {
        e.preventDefault();
        
        const target = e.target.getAttribute('data-target');
        if (!target) return;
        
        this.currentView = target;
        
        // Update active nav item
        const navItems = document.querySelectorAll('.police-nav-item');
        navItems.forEach(item => item.classList.remove('active'));
        e.target.classList.add('active');
        
        // Load view-specific data
        this.loadViewData(target);
    }

    async loadViewData(view) {
        try {
            APP_UTILS.Notification.showLoading(`Loading ${view}...`);
            
            switch (view) {
                case 'cases':
                    await this.loadCasesData();
                    break;
                case 'patrol':
                    await this.loadPatrolData();
                    break;
                case 'reports':
                    await this.loadReportsData();
                    break;
                case 'performance':
                    await this.loadPerformanceData();
                    break;
            }
            
        } catch (error) {
            console.error(`Load ${view} data error:`, error);
            APP_UTILS.Notification.showToast(`Failed to load ${view} data`, 'error');
        } finally {
            APP_UTILS.Notification.hideLoading();
        }
    }

    renderPoliceDashboard() {
        const container = document.getElementById('policeDashboard');
        if (!container || !this.policeData) return;

        const stats = this.policeData.stats || {};
        
        container.innerHTML = `
            <div class="row">
                <!-- Quick Stats -->
                <div class="col-12">
                    <div class="row" id="policeStats"></div>
                </div>

                <!-- Assigned Cases -->
                <div class="col-lg-8">
                    <div class="card mb-4">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="card-title mb-0">My Assigned Cases</h5>
                            <a href="police-cases.html" class="btn btn-sm btn-outline-primary">View All</a>
                        </div>
                        <div class="card-body">
                            <div id="assignedCasesList"></div>
                        </div>
                    </div>

                    <!-- Patrol Recommendations -->
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Patrol Recommendations</h5>
                        </div>
                        <div class="card-body">
                            <div id="patrolRecommendations"></div>
                        </div>
                    </div>
                </div>

                <!-- Sidebar -->
                <div class="col-lg-4">
                    <!-- Availability -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Availability Status</h5>
                        </div>
                        <div class="card-body">
                            <div class="form-check form-switch">
                                <input class="form-check-input" type="checkbox" id="availabilityToggle" 
                                       ${this.policeData.availability === 'available' ? 'checked' : ''}>
                                <label class="form-check-label" for="availabilityToggle">
                                    Available for new assignments
                                </label>
                            </div>
                            <small class="text-muted">
                                Current status: <span class="badge bg-${this.getAvailabilityColor(this.policeData.availability)}">
                                    ${this.policeData.availability}
                                </span>
                            </small>
                        </div>
                    </div>

                    <!-- Quick Actions -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Quick Actions</h5>
                        </div>
                        <div class="card-body">
                            <div class="d-grid gap-2">
                                <button class="btn btn-outline-primary" onclick="this.startNewPatrol()">
                                    <i class="fas fa-map-marked-alt me-2"></i>Start Patrol
                                </button>
                                <button class="btn btn-outline-success" id="generateReport">
                                    <i class="fas fa-file-alt me-2"></i>Daily Report
                                </button>
                                <button class="btn btn-outline-info" onclick="this.viewHotspots()">
                                    <i class="fas fa-map me-2"></i>View Hotspots
                                </button>
                                <button class="btn btn-outline-warning" onclick="this.requestBackup()">
                                    <i class="fas fa-users me-2"></i>Request Backup
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Team Activity -->
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Team Activity</h5>
                        </div>
                        <div class="card-body">
                            <div id="teamActivity"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.updatePoliceStats(stats);
        this.renderAssignedCases();
        this.renderPatrolRecommendations();
        this.renderTeamActivity();
    }

    updatePoliceStats(stats) {
        const container = document.getElementById('policeStats');
        if (!container) return;

        const statsConfig = [
            { key: 'assigned_cases', label: 'Assigned Cases', icon: 'fas fa-tasks', color: 'primary' },
            { key: 'cases_resolved', label: 'Cases Resolved', icon: 'fas fa-check-circle', color: 'success' },
            { key: 'pending_cases', label: 'Pending Cases', icon: 'fas fa-clock', color: 'warning' },
            { key: 'response_time', label: 'Avg Response Time', icon: 'fas fa-stopwatch', color: 'info', suffix: 'h' },
            { key: 'high_priority', label: 'High Priority', icon: 'fas fa-exclamation-triangle', color: 'danger' },
            { key: 'efficiency', label: 'Efficiency Score', icon: 'fas fa-chart-line', color: 'secondary', suffix: '%' }
        ];

        const statsHTML = statsConfig.map(stat => {
            const value = stats[stat.key] || 0;
            return `
                <div class="col-md-4 col-lg-2 mb-4">
                    <div class="card stat-card text-center">
                        <div class="card-body">
                            <i class="${stat.icon} fa-2x text-${stat.color} mb-2"></i>
                            <h3 class="card-title">${value}${stat.suffix || ''}</h3>
                            <p class="card-text text-muted">${stat.label}</p>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = statsHTML;
    }

    renderAssignedCases() {
        const container = document.getElementById('assignedCasesList');
        if (!container) return;

        if (!this.assignedCases || this.assignedCases.length === 0) {
            container.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-clipboard-list fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">No assigned cases</h5>
                    <p class="text-muted">You don't have any cases assigned at the moment.</p>
                </div>
            `;
            return;
        }

        const casesHTML = this.assignedCases.slice(0, 5).map(case_ => {
            const summary = APP_UTILS.CrimeReport.generateCaseSummary(case_);
            
            return `
                <div class="assigned-case-item mb-3 p-3 border rounded">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h6 class="mb-1">${summary.title}</h6>
                            <p class="text-muted mb-1">
                                ${summary.crimeType} • ${summary.location}
                            </p>
                            <div class="d-flex gap-2 mb-2">
                                <span class="${summary.priorityClass}">${summary.priority}</span>
                                <span class="${summary.statusClass}">${summary.status}</span>
                            </div>
                            <small class="text-muted">
                                <i class="fas fa-clock me-1"></i>
                                ${summary.relativeTime}
                            </small>
                        </div>
                        <div class="case-actions">
                            <button class="btn btn-sm btn-outline-primary update-case-status" 
                                    data-case-id="${summary.id}">
                                Update
                            </button>
                            <button class="btn btn-sm btn-outline-info view-case-details" 
                                    data-case-id="${summary.id}">
                                Details
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = casesHTML;

        // Add event listeners to case action buttons
        this.setupCaseActions();
    }

    renderPatrolRecommendations() {
        const container = document.getElementById('patrolRecommendations');
        if (!container) return;

        const recommendations = this.policeData.patrol_recommendations || [];
        
        if (recommendations.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">No patrol recommendations</p>';
            return;
        }

        const recommendationsHTML = recommendations.map(rec => `
            <div class="patrol-recommendation mb-3 p-3 border rounded">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">${rec.area}</h6>
                        <p class="text-muted mb-1">Priority: ${rec.priority}</p>
                        <small class="text-muted">${rec.reason}</small>
                    </div>
                    <span class="badge bg-${rec.priority === 'high' ? 'danger' : 'warning'}">
                        ${rec.priority}
                    </span>
                </div>
                <div class="mt-2">
                    <button class="btn btn-sm btn-outline-primary start-patrol-btn" 
                            data-area="${rec.area}">
                        <i class="fas fa-play me-1"></i>Start Patrol
                    </button>
                </div>
            </div>
        `).join('');

        container.innerHTML = recommendationsHTML;

        // Add event listeners to patrol buttons
        const patrolBtns = document.querySelectorAll('.start-patrol-btn');
        patrolBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const area = e.target.getAttribute('data-area');
                this.startPatrol(area);
            });
        });
    }

    renderTeamActivity() {
        const container = document.getElementById('teamActivity');
        if (!container) return;

        const teamActivity = this.policeData.team_activity || [];
        
        if (teamActivity.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">No team activity</p>';
            return;
        }

        const activityHTML = teamActivity.map(activity => `
            <div class="team-activity-item mb-2">
                <div class="d-flex justify-content-between">
                    <span class="fw-bold">${activity.officer}</span>
                    <small class="text-muted">${activity.status}</small>
                </div>
                <small class="text-muted">${activity.location}</small>
            </div>
        `).join('');

        container.innerHTML = activityHTML;
    }

    setupCaseActions() {
        // Update case status buttons
        const updateButtons = document.querySelectorAll('.update-case-status');
        updateButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const caseId = e.target.getAttribute('data-case-id');
                this.showUpdateCaseModal(caseId);
            });
        });

        // View case details buttons
        const viewButtons = document.querySelectorAll('.view-case-details');
        viewButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const caseId = e.target.getAttribute('data-case-id');
                this.viewCaseDetails(caseId);
            });
        });
    }

    async showUpdateCaseModal(caseId) {
        const case_ = this.assignedCases.find(c => c.id == caseId);
        if (!case_) return;

        const modalHTML = `
            <div class="modal fade" id="updateCaseModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Update Case Status</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="updateCaseForm">
                                <input type="hidden" name="case_id" value="${caseId}">
                                
                                <div class="mb-3">
                                    <label class="form-label">Current Status</label>
                                    <p class="form-control-plaintext">
                                        ${APP_UTILS.CrimeReport.getStatusInfo(case_.status).display}
                                    </p>
                                </div>

                                <div class="mb-3">
                                    <label for="newStatus" class="form-label">New Status</label>
                                    <select class="form-select" id="newStatus" name="status" required>
                                        <option value="">Select status...</option>
                                        <option value="in_progress">In Progress</option>
                                        <option value="resolved">Resolved</option>
                                        <option value="closed">Closed</option>
                                    </select>
                                </div>

                                <div class="mb-3">
                                    <label for="updateNotes" class="form-label">Update Notes</label>
                                    <textarea class="form-control" id="updateNotes" name="notes" 
                                              rows="3" placeholder="Add update notes..."></textarea>
                                </div>

                                <div class="mb-3">
                                    <label class="form-label">Next Action Required</label>
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" name="needs_followup" id="needsFollowup">
                                        <label class="form-check-label" for="needsFollowup">
                                            Requires follow-up
                                        </label>
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="submitCaseUpdate">Update Case</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('updateCaseModal');
        if (existingModal) existingModal.remove();

        // Add new modal to body
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('updateCaseModal'));
        modal.show();

        // Add submit handler
        const submitBtn = document.getElementById('submitCaseUpdate');
        submitBtn.addEventListener('click', () => this.submitCaseUpdate(caseId));
    }

    async submitCaseUpdate(caseId) {
        const form = document.getElementById('updateCaseForm');
        const formData = APP_UTILS.Form.serializeForm(form);

        try {
            APP_UTILS.Notification.showLoading('Updating case...');

            const response = await API_SERVICE.updatePoliceCase(caseId, formData);
            
            if (response.success) {
                APP_UTILS.Notification.showToast('Case updated successfully!', 'success');
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('updateCaseModal'));
                modal.hide();
                
                // Reload cases data
                this.loadPoliceData();
            } else {
                throw new Error(response.message || 'Failed to update case');
            }
            
        } catch (error) {
            console.error('Update case error:', error);
            APP_UTILS.Notification.showToast(
                APP_UTILS.API.handleError(error, 'Failed to update case.'),
                'error'
            );
        } finally {
            APP_UTILS.Notification.hideLoading();
        }
    }

    async viewCaseDetails(caseId) {
        try {
            APP_UTILS.Notification.showLoading('Loading case details...');

            const response = await API_SERVICE.getPoliceCaseDetails(caseId);
            
            if (response.success) {
                this.showCaseDetailsModal(response.data);
            } else {
                throw new Error(response.message || 'Failed to load case details');
            }
            
        } catch (error) {
            console.error('View case details error:', error);
            APP_UTILS.Notification.showToast(
                APP_UTILS.API.handleError(error, 'Failed to load case details.'),
                'error'
            );
        } finally {
            APP_UTILS.Notification.hideLoading();
        }
    }

    showCaseDetailsModal(caseData) {
        // Implementation for showing case details modal
        // Similar to the one in complaints.js but with police-specific actions
    }

    handleCaseSearch(e) {
        const searchTerm = e.target.value.toLowerCase();
        const caseItems = document.querySelectorAll('.assigned-case-item');
        
        caseItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    }

    handleCaseFilter(e) {
        const filterValue = e.target.value;
        const caseItems = document.querySelectorAll('.assigned-case-item');
        
        caseItems.forEach(item => {
            if (filterValue === 'all') {
                item.style.display = '';
            } else {
                const hasStatus = item.querySelector(`.${filterValue}`);
                item.style.display = hasStatus ? '' : 'none';
            }
        });
    }

    async handleAvailabilityToggle(e) {
        const isAvailable = e.target.checked;
        const status = isAvailable ? 'available' : 'busy';

        try {
            const response = await API_SERVICE.updateAvailability({ status: status });
            
            if (response.success) {
                APP_UTILS.Notification.showToast(
                    `You are now ${status} for assignments`,
                    'success'
                );
            } else {
                throw new Error(response.message || 'Failed to update availability');
            }
            
        } catch (error) {
            console.error('Update availability error:', error);
            APP_UTILS.Notification.showToast('Failed to update availability', 'error');
            
            // Revert toggle
            e.target.checked = !isAvailable;
        }
    }

    async startPatrol(area) {
        try {
            APP_UTILS.Notification.showLoading('Starting patrol...');

            // Here you would call an API to log patrol start
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            APP_UTILS.Notification.showToast(`Patrol started in ${area}`, 'success');
            
            // Show patrol interface
            this.showPatrolInterface(area);
            
        } catch (error) {
            console.error('Start patrol error:', error);
            APP_UTILS.Notification.showToast('Failed to start patrol', 'error');
        } finally {
            APP_UTILS.Notification.hideLoading();
        }
    }

    showPatrolInterface(area) {
        // Implementation for patrol interface
        APP_UTILS.Notification.showToast(`Patrol interface for ${area} would open here`, 'info');
    }

    async generateDailyReport() {
        try {
            APP_UTILS.Notification.showLoading('Generating daily report...');

            const response = await API_SERVICE.generateCaseReport('daily', {
                date: APP_UTILS.Date.formatDate(new Date(), 'yyyy-mm-dd'),
                type: 'daily_summary'
            });
            
            if (response.success) {
                APP_UTILS.Notification.showToast('Daily report generated successfully!', 'success');
                
                // Show report or trigger download
                this.showGeneratedReport(response.data);
            } else {
                throw new Error(response.message || 'Failed to generate report');
            }
            
        } catch (error) {
            console.error('Generate report error:', error);
            APP_UTILS.Notification.showToast('Failed to generate daily report', 'error');
        } finally {
            APP_UTILS.Notification.hideLoading();
        }
    }

    showGeneratedReport(reportData) {
        // Implementation for showing generated report
        APP_UTILS.Notification.showToast('Report would be displayed here', 'info');
    }

    getAvailabilityColor(status) {
        const colors = {
            'available': 'success',
            'busy': 'warning',
            'offline': 'secondary'
        };
        return colors[status] || 'secondary';
    }

    // Additional police-specific methods
    async requestBackup() {
        const confirmed = await APP_UTILS.Notification.showConfirm(
            'Request backup support? This will alert nearby officers.',
            'Request Backup'
        );

        if (confirmed) {
            APP_UTILS.Notification.showToast('Backup requested successfully', 'success');
        }
    }

    async logIncident(incidentData) {
        // Implementation for logging incidents during patrol
    }

    async syncOfflineData() {
        // Implementation for syncing data when coming online
    }
}

// Initialize Police Manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (isPolice() || isAdmin()) {
        window.policeManager = new PoliceManager();
    }
});