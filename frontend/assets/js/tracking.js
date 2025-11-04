// tracking.js - Complaint tracking for iReport
class TrackingManager {
    constructor() {
        this.currentCase = null;
        this.trackingData = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeTracking();
    }

    setupEventListeners() {
        // Track complaint form
        const trackForm = document.getElementById('trackComplaintForm');
        if (trackForm) {
            trackForm.addEventListener('submit', (e) => this.handleTrackComplaint(e));
        }

        // Case ID input
        const caseIdInput = document.getElementById('caseIdInput');
        if (caseIdInput) {
            caseIdInput.addEventListener('input', (e) => this.handleCaseIdInput(e));
        }

        // Share tracking link
        const shareBtn = document.getElementById('shareTrackingLink');
        if (shareBtn) {
            shareBtn.addEventListener('click', () => this.shareTrackingLink());
        }

        // Print tracking info
        const printBtn = document.getElementById('printTrackingInfo');
        if (printBtn) {
            printBtn.addEventListener('click', () => this.printTrackingInfo());
        }

        // Subscribe to updates
        const subscribeBtn = document.getElementById('subscribeUpdates');
        if (subscribeBtn) {
            subscribeBtn.addEventListener('click', () => this.subscribeToUpdates());
        }
    }

    initializeTracking() {
        // Check if case ID is provided in URL
        const urlParams = new URLSearchParams(window.location.search);
        const caseId = urlParams.get('caseId') || urlParams.get('id');
        
        if (caseId) {
            document.getElementById('caseIdInput').value = caseId;
            this.trackComplaint(caseId);
        }
    }

    async handleTrackComplaint(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = APP_UTILS.Form.serializeForm(form);
        const caseId = formData.caseId.trim();
        
        if (!caseId) {
            APP_UTILS.Notification.showToast('Please enter a Case ID', 'error');
            return;
        }

        await this.trackComplaint(caseId);
    }

    async trackComplaint(caseId) {
        try {
            APP_UTILS.Notification.showLoading('Tracking complaint...');

            // Get tracking status
            const statusResponse = await API_SERVICE.trackComplaint(caseId);
            
            if (statusResponse.success) {
                this.currentCase = caseId;
                this.trackingData = statusResponse.data;
                
                // Get detailed tracking information
                const detailsResponse = await API_SERVICE.getTrackingDetails(caseId);
                if (detailsResponse.success) {
                    this.trackingData.details = detailsResponse.data;
                }
                
                this.renderTrackingInfo();
                this.updateURL(caseId);
                
            } else {
                throw new Error(statusResponse.message || 'Case not found');
            }

        } catch (error) {
            console.error('Track complaint error:', error);
            APP_UTILS.Notification.showToast(
                APP_UTILS.API.handleError(error, 'Failed to track complaint. Please check the Case ID.'),
                'error'
            );
            this.renderErrorState();
        } finally {
            APP_UTILS.Notification.hideLoading();
        }
    }

    renderTrackingInfo() {
        const container = document.getElementById('trackingResults');
        if (!container) return;

        const caseData = this.trackingData.details || this.trackingData;
        const statusInfo = APP_UTILS.CrimeReport.getStatusInfo(caseData.status);
        const priorityInfo = APP_UTILS.CrimeReport.getPriorityInfo(caseData.priority);

        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <h4 class="card-title mb-0">Case Tracking: ${this.currentCase}</h4>
                        <div class="tracking-actions">
                            <button id="shareTrackingLink" class="btn btn-sm btn-outline-primary">
                                <i class="fas fa-share-alt me-1"></i>Share
                            </button>
                            <button id="printTrackingInfo" class="btn btn-sm btn-outline-secondary">
                                <i class="fas fa-print me-1"></i>Print
                            </button>
                        </div>
                    </div>
                </div>
                <div class="card-body">
                    <!-- Case Overview -->
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <h5>Case Information</h5>
                            <table class="table table-sm">
                                <tr>
                                    <td><strong>Title:</strong></td>
                                    <td>${caseData.title || 'N/A'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Crime Type:</strong></td>
                                    <td>${APP_UTILS.CrimeReport.getCrimeTypeDisplay(caseData.crime_type)}</td>
                                </tr>
                                <tr>
                                    <td><strong>Priority:</strong></td>
                                    <td><span class="${priorityInfo.class}">${priorityInfo.display}</span></td>
                                </tr>
                                <tr>
                                    <td><strong>Location:</strong></td>
                                    <td>${caseData.location || 'N/A'}</td>
                                </tr>
                            </table>
                        </div>
                        <div class="col-md-6">
                            <h5>Current Status</h5>
                            <div class="text-center py-3">
                                <div class="status-indicator ${caseData.status} mb-3">
                                    <i class="fas ${this.getStatusIcon(caseData.status)} fa-3x text-${statusInfo.color}"></i>
                                </div>
                                <h4 class="text-${statusInfo.color}">${statusInfo.display}</h4>
                                <p class="text-muted">Last updated: ${APP_UTILS.Date.formatDate(caseData.updated_at, 'dd/mm/yyyy hh:mm')}</p>
                            </div>
                        </div>
                    </div>

                    <!-- Status Timeline -->
                    <div class="mb-4">
                        <h5>Case Timeline</h5>
                        ${this.renderTimeline(caseData.timeline || [])}
                    </div>

                    <!-- Assigned Officer -->
                    ${caseData.assigned_officer ? `
                    <div class="mb-4">
                        <h5>Assigned Officer</h5>
                        <div class="assigned-officer card">
                            <div class="card-body">
                                <div class="d-flex align-items-center">
                                    <div class="officer-avatar me-3">
                                        <i class="fas fa-user-shield fa-2x text-primary"></i>
                                    </div>
                                    <div>
                                        <h6 class="mb-1">${caseData.assigned_officer.name}</h6>
                                        <p class="text-muted mb-1">Badge: ${caseData.assigned_officer.badge_number}</p>
                                        <p class="text-muted mb-0">Contact: ${caseData.assigned_officer.contact}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    ` : ''}

                    <!-- Next Steps -->
                    <div class="mb-4">
                        <h5>Next Steps</h5>
                        <div class="alert alert-info">
                            ${this.getNextSteps(caseData.status)}
                        </div>
                    </div>

                    <!-- Updates Subscription -->
                    <div class="updates-subscription">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="subscribeUpdates">
                            <label class="form-check-label" for="subscribeUpdates">
                                Get email/SMS updates for this case
                            </label>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Re-attach event listeners
        this.setupTrackingActions();
    }

    renderTimeline(timeline) {
        if (!timeline || timeline.length === 0) {
            return '<p class="text-muted text-center">No timeline data available</p>';
        }

        return `
            <div class="timeline">
                ${timeline.map(event => `
                    <div class="timeline-item">
                        <div class="timeline-marker bg-${this.getTimelineEventColor(event.type)}"></div>
                        <div class="timeline-content">
                            <div class="d-flex justify-content-between">
                                <strong>${event.title}</strong>
                                <small class="text-muted">${APP_UTILS.Date.formatDate(event.timestamp, 'dd/mm/yyyy hh:mm')}</small>
                            </div>
                            <p class="mb-1">${event.description}</p>
                            ${event.updated_by ? `<small class="text-muted">By: ${event.updated_by}</small>` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderErrorState() {
        const container = document.getElementById('trackingResults');
        if (!container) return;

        container.innerHTML = `
            <div class="card">
                <div class="card-body text-center py-5">
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <h4 class="text-muted">Case Not Found</h4>
                    <p class="text-muted mb-4">
                        We couldn't find a case with the provided ID. Please check the Case ID and try again.
                    </p>
                    <div class="suggestions">
                        <h6>Suggestions:</h6>
                        <ul class="text-start">
                            <li>Double-check the Case ID for typos</li>
                            <li>Ensure you're using the correct format</li>
                            <li>Contact support if you believe this is an error</li>
                        </ul>
                    </div>
                </div>
            </div>
        `;
    }

    setupTrackingActions() {
        // Share tracking link
        const shareBtn = document.getElementById('shareTrackingLink');
        if (shareBtn) {
            shareBtn.addEventListener('click', () => this.shareTrackingLink());
        }

        // Print tracking info
        const printBtn = document.getElementById('printTrackingInfo');
        if (printBtn) {
            printBtn.addEventListener('click', () => this.printTrackingInfo());
        }

        // Subscribe to updates
        const subscribeBtn = document.getElementById('subscribeUpdates');
        if (subscribeBtn) {
            subscribeBtn.addEventListener('click', () => this.subscribeToUpdates());
        }
    }

    shareTrackingLink() {
        if (!this.currentCase) return;

        const trackingUrl = `${window.location.origin}${window.location.pathname}?caseId=${this.currentCase}`;
        
        if (navigator.share) {
            navigator.share({
                title: `Track Case ${this.currentCase} - iReport`,
                text: `Track the status of case ${this.currentCase} on iReport`,
                url: trackingUrl
            });
        } else if (navigator.clipboard) {
            navigator.clipboard.writeText(trackingUrl).then(() => {
                APP_UTILS.Notification.showToast('Tracking link copied to clipboard!', 'success');
            });
        } else {
            // Fallback
            prompt('Copy this tracking link:', trackingUrl);
        }
    }

    printTrackingInfo() {
        APP_UTILS.Export.printElement('trackingResults');
    }

    async subscribeToUpdates() {
        if (!this.currentCase) return;

        const subscribeCheckbox = document.getElementById('subscribeUpdates');
        const subscribe = subscribeCheckbox.checked;

        try {
            APP_UTILS.Notification.showLoading('Updating subscription...');

            // Here you would call an API to subscribe/unsubscribe from updates
            // For now, we'll simulate the API call
            await new Promise(resolve => setTimeout(resolve, 1000));

            APP_UTILS.Notification.showToast(
                subscribe ? 
                'You will receive updates for this case' : 
                'You have unsubscribed from updates for this case',
                'success'
            );

        } catch (error) {
            console.error('Subscription error:', error);
            APP_UTILS.Notification.showToast('Failed to update subscription', 'error');
            
            // Revert checkbox state
            subscribeCheckbox.checked = !subscribe;
        } finally {
            APP_UTILS.Notification.hideLoading();
        }
    }

    handleCaseIdInput(e) {
        const caseId = e.target.value.trim();
        const helpText = document.getElementById('caseIdHelp');
        
        if (helpText) {
            if (caseId.length > 0) {
                helpText.textContent = 'Press Enter or click Track to search';
                helpText.className = 'form-text text-info';
            } else {
                helpText.textContent = 'Enter your Case ID to track its status';
                helpText.className = 'form-text text-muted';
            }
        }
    }

    updateURL(caseId) {
        const newUrl = `${window.location.pathname}?caseId=${caseId}`;
        window.history.pushState({}, '', newUrl);
    }

    getStatusIcon(status) {
        const icons = {
            'pending': 'fa-clock',
            'assigned': 'fa-user-plus',
            'in_progress': 'fa-sync-alt',
            'resolved': 'fa-check-circle',
            'closed': 'fa-archive'
        };
        return icons[status] || 'fa-question-circle';
    }

    getTimelineEventColor(eventType) {
        const colors = {
            'filed': 'primary',
            'assigned': 'info',
            'updated': 'warning',
            'resolved': 'success',
            'closed': 'secondary'
        };
        return colors[eventType] || 'primary';
    }

    getNextSteps(status) {
        const nextSteps = {
            'pending': 'Your complaint has been received and is awaiting assignment to an officer.',
            'assigned': 'An officer has been assigned to your case and will begin investigation shortly.',
            'in_progress': 'Your case is currently under investigation. The assigned officer is working on it.',
            'resolved': 'Your case has been resolved. You will receive a detailed report soon.',
            'closed': 'This case has been closed. Thank you for using iReport.'
        };
        return nextSteps[status] || 'Your case is being processed.';
    }

    // Auto-refresh tracking data
    startAutoRefresh() {
        if (this.currentCase) {
            this.autoRefreshInterval = setInterval(() => {
                this.refreshTrackingData();
            }, 30000); // Refresh every 30 seconds
        }
    }

    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }
    }

    async refreshTrackingData() {
        if (!this.currentCase) return;

        try {
            const response = await API_SERVICE.trackComplaint(this.currentCase);
            if (response.success && response.data.status !== this.trackingData.status) {
                // Status changed, update the display
                this.trackingData = response.data;
                this.renderTrackingInfo();
                
                // Show notification about status change
                APP_UTILS.Notification.showToast(
                    `Case status updated to: ${APP_UTILS.CrimeReport.getStatusInfo(response.data.status).display}`,
                    'info'
                );
            }
        } catch (error) {
            console.error('Auto-refresh error:', error);
        }
    }
}

// Initialize Tracking Manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.trackingManager = new TrackingManager();
});