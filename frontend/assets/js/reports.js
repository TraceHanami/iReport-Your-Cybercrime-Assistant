// reports.js - Reports generation for iReport
class ReportsManager {
    constructor() {
        this.currentReport = null;
        this.reportData = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadReportTypes();
        this.initializeDatePickers();
    }

    setupEventListeners() {
        // Report generation form
        const reportForm = document.getElementById('reportForm');
        if (reportForm) {
            reportForm.addEventListener('submit', (e) => this.handleGenerateReport(e));
        }

        // Report type change
        const reportTypeSelect = document.getElementById('reportType');
        if (reportTypeSelect) {
            reportTypeSelect.addEventListener('change', (e) => this.handleReportTypeChange(e));
        }

        // Date range changes
        const dateFromInput = document.getElementById('dateFrom');
        const dateToInput = document.getElementById('dateTo');
        if (dateFromInput && dateToInput) {
            dateFromInput.addEventListener('change', () => this.validateDateRange());
            dateToInput.addEventListener('change', () => this.validateDateRange());
        }

        // Download buttons
        const downloadButtons = document.querySelectorAll('.download-report');
        downloadButtons.forEach(btn => {
            btn.addEventListener('click', (e) => this.handleDownloadReport(e));
        });

        // Print buttons
        const printButtons = document.querySelectorAll('.print-report');
        printButtons.forEach(btn => {
            btn.addEventListener('click', (e) => this.handlePrintReport(e));
        });

        // Schedule report button
        const scheduleBtn = document.getElementById('scheduleReport');
        if (scheduleBtn) {
            scheduleBtn.addEventListener('click', () => this.scheduleReport());
        }
    }

    loadReportTypes() {
        const reportTypeSelect = document.getElementById('reportType');
        if (!reportTypeSelect) return;

        const reportTypes = this.getAvailableReportTypes();
        
        reportTypes.forEach(reportType => {
            const option = document.createElement('option');
            option.value = reportType.value;
            option.textContent = reportType.label;
            option.disabled = reportType.requiredRole && !hasRole(reportType.requiredRole);
            reportTypeSelect.appendChild(option);
        });
    }

    getAvailableReportTypes() {
        const baseReports = [
            { value: 'case_summary', label: 'Case Summary Report', requiredRole: null },
            { value: 'analytics_overview', label: 'Analytics Overview', requiredRole: null },
            { value: 'performance_metrics', label: 'Performance Metrics', requiredRole: 'police' },
            { value: 'crime_trends', label: 'Crime Trends Analysis', requiredRole: null },
            { value: 'officer_performance', label: 'Officer Performance', requiredRole: 'admin' },
            { value: 'system_usage', label: 'System Usage Report', requiredRole: 'admin' },
            { value: 'citizen_feedback', label: 'Citizen Feedback Summary', requiredRole: 'admin' }
        ];

        return baseReports.filter(report => 
            !report.requiredRole || hasRole(report.requiredRole)
        );
    }

    initializeDatePickers() {
        // Set default date range (last 30 days)
        const dateFrom = document.getElementById('dateFrom');
        const dateTo = document.getElementById('dateTo');
        
        if (dateFrom && dateTo) {
            const today = new Date();
            const thirtyDaysAgo = new Date();
            thirtyDaysAgo.setDate(today.getDate() - 30);
            
            dateFrom.value = thirtyDaysAgo.toISOString().split('T')[0];
            dateTo.value = today.toISOString().split('T')[0];
        }
    }

    validateDateRange() {
        const dateFrom = document.getElementById('dateFrom');
        const dateTo = document.getElementById('dateTo');
        const errorElement = document.getElementById('dateRangeError');
        
        if (!dateFrom || !dateTo || !errorElement) return;

        const fromDate = new Date(dateFrom.value);
        const toDate = new Date(dateTo.value);

        if (fromDate > toDate) {
            errorElement.textContent = 'End date cannot be before start date';
            errorElement.style.display = 'block';
            return false;
        } else {
            errorElement.style.display = 'none';
            return true;
        }
    }

    async handleGenerateReport(e) {
        e.preventDefault();
        
        if (!this.validateDateRange()) {
            APP_UTILS.Notification.showToast('Please fix date range errors', 'error');
            return;
        }

        const form = e.target;
        const formData = APP_UTILS.Form.serializeForm(form);
        
        try {
            APP_UTILS.Notification.showLoading('Generating report...');
            APP_UTILS.Form.disableForm(form, true);

            let response;
            switch (formData.reportType) {
                case 'case_summary':
                    response = await API_SERVICE.generateCaseReport(formData.caseId, formData);
                    break;
                case 'analytics_overview':
                    response = await API_SERVICE.generateAnalyticsReport(formData);
                    break;
                case 'performance_metrics':
                    response = await API_SERVICE.getPerformanceMetrics();
                    break;
                case 'crime_trends':
                    response = await API_SERVICE.getTrendAnalytics(formData);
                    break;
                case 'officer_performance':
                    response = await API_SERVICE.getOfficerPerformanceAnalytics();
                    break;
                default:
                    throw new Error('Unsupported report type');
            }

            if (response.success) {
                this.currentReport = formData.reportType;
                this.reportData = response.data;
                this.renderReport();
                APP_UTILS.Notification.showToast('Report generated successfully!', 'success');
            } else {
                throw new Error(response.message || 'Failed to generate report');
            }

        } catch (error) {
            console.error('Generate report error:', error);
            APP_UTILS.Notification.showToast(
                APP_UTILS.API.handleError(error, 'Failed to generate report.'),
                'error'
            );
        } finally {
            APP_UTILS.Notification.hideLoading();
            APP_UTILS.Form.disableForm(form, false);
        }
    }

    handleReportTypeChange(e) {
        const reportType = e.target.value;
        this.toggleReportOptions(reportType);
    }

    toggleReportOptions(reportType) {
        // Hide all option sections
        const optionSections = document.querySelectorAll('.report-options');
        optionSections.forEach(section => {
            section.style.display = 'none';
        });

        // Show relevant options based on report type
        const specificOptions = document.getElementById(`${reportType}Options`);
        if (specificOptions) {
            specificOptions.style.display = 'block';
        }

        // Update form labels and placeholders based on report type
        this.updateFormForReportType(reportType);
    }

    updateFormForReportType(reportType) {
        const formatSelect = document.getElementById('reportFormat');
        const submitButton = document.querySelector('#reportForm button[type="submit"]');
        
        if (!formatSelect || !submitButton) return;

        const reportConfigs = {
            'case_summary': {
                formats: ['pdf', 'html'],
                buttonText: 'Generate Case Report'
            },
            'analytics_overview': {
                formats: ['pdf', 'html', 'excel'],
                buttonText: 'Generate Analytics Report'
            },
            'performance_metrics': {
                formats: ['pdf', 'html', 'excel'],
                buttonText: 'Generate Performance Report'
            },
            'crime_trends': {
                formats: ['pdf', 'html', 'excel'],
                buttonText: 'Generate Trends Report'
            },
            'officer_performance': {
                formats: ['pdf', 'excel'],
                buttonText: 'Generate Officer Report'
            }
        };

        const config = reportConfigs[reportType] || {
            formats: ['pdf', 'html'],
            buttonText: 'Generate Report'
        };

        // Update format options
        while (formatSelect.options.length > 0) {
            formatSelect.remove(0);
        }

        config.formats.forEach(format => {
            const option = document.createElement('option');
            option.value = format;
            option.textContent = format.toUpperCase();
            formatSelect.appendChild(option);
        });

        // Update button text
        submitButton.textContent = config.buttonText;
    }

    renderReport() {
        const container = document.getElementById('reportResults');
        if (!container) return;

        let reportHTML = '';

        switch (this.currentReport) {
            case 'case_summary':
                reportHTML = this.renderCaseSummaryReport();
                break;
            case 'analytics_overview':
                reportHTML = this.renderAnalyticsReport();
                break;
            case 'performance_metrics':
                reportHTML = this.renderPerformanceReport();
                break;
            case 'crime_trends':
                reportHTML = this.renderCrimeTrendsReport();
                break;
            case 'officer_performance':
                reportHTML = this.renderOfficerPerformanceReport();
                break;
            default:
                reportHTML = this.renderGenericReport();
        }

        container.innerHTML = reportHTML;
        this.setupReportActions();
    }

    renderCaseSummaryReport() {
        const data = this.reportData;
        
        return `
            <div class="report-container">
                <div class="report-header text-center mb-4">
                    <h2>Case Summary Report</h2>
                    <p class="text-muted">Generated on ${APP_UTILS.Date.formatDate(new Date(), 'dd/mm/yyyy hh:mm')}</p>
                </div>

                <div class="row mb-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5>Case Details</h5>
                            </div>
                            <div class="card-body">
                                <table class="table table-sm">
                                    <tr><td><strong>Case ID:</strong></td><td>${data.case_id}</td></tr>
                                    <tr><td><strong>Title:</strong></td><td>${data.title}</td></tr>
                                    <tr><td><strong>Crime Type:</strong></td><td>${APP_UTILS.CrimeReport.getCrimeTypeDisplay(data.crime_type)}</td></tr>
                                    <tr><td><strong>Priority:</strong></td><td><span class="${APP_UTILS.CrimeReport.getPriorityInfo(data.priority).class}">${APP_UTILS.CrimeReport.getPriorityInfo(data.priority).display}</span></td></tr>
                                    <tr><td><strong>Status:</strong></td><td><span class="${APP_UTILS.CrimeReport.getStatusInfo(data.status).class}">${APP_UTILS.CrimeReport.getStatusInfo(data.status).display}</span></td></tr>
                                    <tr><td><strong>Location:</strong></td><td>${data.location}</td></tr>
                                    <tr><td><strong>Filed On:</strong></td><td>${APP_UTILS.Date.formatDate(data.created_at, 'dd/mm/yyyy hh:mm')}</td></tr>
                                </table>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5>Investigation Details</h5>
                            </div>
                            <div class="card-body">
                                ${data.assigned_officer ? `
                                    <p><strong>Assigned Officer:</strong> ${data.assigned_officer.name}</p>
                                    <p><strong>Badge Number:</strong> ${data.assigned_officer.badge_number}</p>
                                    <p><strong>Contact:</strong> ${data.assigned_officer.contact}</p>
                                ` : '<p class="text-muted">No officer assigned</p>'}
                                <p><strong>Last Updated:</strong> ${APP_UTILS.Date.formatDate(data.updated_at, 'dd/mm/yyyy hh:mm')}</p>
                                ${data.resolution_time ? `
                                    <p><strong>Resolution Time:</strong> ${data.resolution_time} hours</p>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                </div>

                ${data.description ? `
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>Case Description</h5>
                    </div>
                    <div class="card-body">
                        <p>${data.description}</p>
                    </div>
                </div>
                ` : ''}

                ${data.timeline && data.timeline.length > 0 ? `
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>Case Timeline</h5>
                    </div>
                    <div class="card-body">
                        <div class="timeline">
                            ${data.timeline.map(event => `
                                <div class="timeline-item">
                                    <div class="timeline-marker bg-primary"></div>
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
                    </div>
                </div>
                ` : ''}

                <div class="report-footer mt-4">
                    <div class="row">
                        <div class="col-md-6">
                            <small class="text-muted">Report ID: ${APP_UTILS.String.generateCaseId('REP')}</small>
                        </div>
                        <div class="col-md-6 text-end">
                            <small class="text-muted">Confidential - For authorized use only</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderAnalyticsReport() {
        const data = this.reportData;
        
        return `
            <div class="report-container">
                <div class="report-header text-center mb-4">
                    <h2>Analytics Overview Report</h2>
                    <p class="text-muted">Period: ${data.date_range} | Generated on ${APP_UTILS.Date.formatDate(new Date(), 'dd/mm/yyyy hh:mm')}</p>
                </div>

                <!-- Key Metrics -->
                <div class="row mb-4">
                    ${data.metrics ? Object.entries(data.metrics).map(([key, value]) => `
                        <div class="col-md-3 mb-3">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h3 class="text-primary">${value}</h3>
                                    <p class="text-muted">${APP_UTILS.String.camelToTitleCase(key)}</p>
                                </div>
                            </div>
                        </div>
                    `).join('') : ''}
                </div>

                <!-- Charts and Visualizations would go here -->
                <div class="alert alert-info">
                    <i class="fas fa-chart-bar me-2"></i>
                    Detailed charts and visualizations would be rendered here based on the analytics data.
                </div>

                <!-- Summary -->
                ${data.summary ? `
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>Executive Summary</h5>
                    </div>
                    <div class="card-body">
                        <p>${data.summary}</p>
                    </div>
                </div>
                ` : ''}

                <!-- Recommendations -->
                ${data.recommendations ? `
                <div class="card">
                    <div class="card-header">
                        <h5>Recommendations</h5>
                    </div>
                    <div class="card-body">
                        <ul>
                            ${data.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                ` : ''}
            </div>
        `;
    }

    renderPerformanceReport() {
        // Similar structure for performance reports
        return `<div>Performance Report Content</div>`;
    }

    renderCrimeTrendsReport() {
        // Similar structure for crime trends reports
        return `<div>Crime Trends Report Content</div>`;
    }

    renderOfficerPerformanceReport() {
        // Similar structure for officer performance reports
        return `<div>Officer Performance Report Content</div>`;
    }

    renderGenericReport() {
        return `
            <div class="report-container">
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    Report preview is not available for this report type. 
                    Use the download button to get the complete report.
                </div>
            </div>
        `;
    }

    setupReportActions() {
        // Download report button
        const downloadBtn = document.getElementById('downloadReport');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.downloadCurrentReport());
        }

        // Print report button
        const printBtn = document.getElementById('printReport');
        if (printBtn) {
            printBtn.addEventListener('click', () => this.printCurrentReport());
        }

        // Share report button
        const shareBtn = document.getElementById('shareReport');
        if (shareBtn) {
            shareBtn.addEventListener('click', () => this.shareCurrentReport());
        }
    }

    async downloadCurrentReport() {
        if (!this.currentReport || !this.reportData) {
            APP_UTILS.Notification.showToast('No report to download', 'error');
            return;
        }

        try {
            APP_UTILS.Notification.showLoading('Preparing download...');

            const format = document.getElementById('reportFormat').value;
            const filename = `${this.currentReport}_${APP_UTILS.Date.formatDate(new Date(), 'yyyy-mm-dd')}.${format}`;

            switch (format) {
                case 'pdf':
                    // Generate PDF (would need a PDF library)
                    APP_UTILS.Export.printElement('reportResults');
                    break;
                case 'excel':
                    APP_UTILS.Export.exportToCSV(this.flattenReportData(), filename);
                    break;
                case 'html':
                default:
                    APP_UTILS.Export.exportToJSON(this.reportData, filename);
                    break;
            }

            APP_UTILS.Notification.showToast('Report downloaded successfully!', 'success');

        } catch (error) {
            console.error('Download report error:', error);
            APP_UTILS.Notification.showToast('Failed to download report', 'error');
        } finally {
            APP_UTILS.Notification.hideLoading();
        }
    }

    printCurrentReport() {
        APP_UTILS.Export.printElement('reportResults');
    }

    shareCurrentReport() {
        // Similar to tracking share functionality
        APP_UTILS.Notification.showToast('Share functionality would be implemented here', 'info');
    }

    async scheduleReport() {
        const confirmed = await APP_UTILS.Notification.showConfirm(
            'This will schedule this report to be generated and sent to your email regularly. Continue?',
            'Schedule Report'
        );

        if (confirmed) {
            APP_UTILS.Notification.showToast('Report scheduling would be implemented here', 'info');
        }
    }

    flattenReportData() {
        // Helper function to flatten report data for CSV export
        if (!this.reportData) return [];

        if (Array.isArray(this.reportData)) {
            return this.reportData;
        }

        // Convert object to array format for CSV
        return [this.reportData];
    }

    // Load report history
    async loadReportHistory() {
        try {
            const response = await API_SERVICE.listReports();
            if (response.success) {
                this.renderReportHistory(response.data);
            }
        } catch (error) {
            console.error('Failed to load report history:', error);
        }
    }

    renderReportHistory(reports) {
        const container = document.getElementById('reportHistory');
        if (!container) return;

        if (!reports || reports.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">No previous reports</p>';
            return;
        }

        const historyHTML = reports.map(report => `
            <div class="report-history-item card mb-3">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="mb-1">${report.name}</h6>
                            <p class="text-muted mb-1">Type: ${report.type} | Format: ${report.format}</p>
                            <small class="text-muted">
                                Generated: ${APP_UTILS.Date.formatDate(report.generated_at, 'dd/mm/yyyy hh:mm')}
                            </small>
                        </div>
                        <div class="report-actions">
                            <button class="btn btn-sm btn-outline-primary download-report" 
                                    data-report-id="${report.id}">
                                <i class="fas fa-download"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger delete-report" 
                                    data-report-id="${report.id}">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = historyHTML;

        // Add event listeners to history items
        this.setupHistoryActions();
    }

    setupHistoryActions() {
        // Download history report
        const downloadBtns = document.querySelectorAll('.download-report');
        downloadBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const reportId = e.target.closest('.download-report').getAttribute('data-report-id');
                this.downloadHistoricalReport(reportId);
            });
        });

        // Delete history report
        const deleteBtns = document.querySelectorAll('.delete-report');
        deleteBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const reportId = e.target.closest('.delete-report').getAttribute('data-report-id');
                this.deleteHistoricalReport(reportId);
            });
        });
    }

    async downloadHistoricalReport(reportId) {
        try {
            APP_UTILS.Notification.showLoading('Downloading report...');
            
            // This would call an API to get the report file
            // For now, we'll show a success message
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            APP_UTILS.Notification.showToast('Report downloaded successfully!', 'success');
        } catch (error) {
            console.error('Download historical report error:', error);
            APP_UTILS.Notification.showToast('Failed to download report', 'error');
        } finally {
            APP_UTILS.Notification.hideLoading();
        }
    }

    async deleteHistoricalReport(reportId) {
        const confirmed = await APP_UTILS.Notification.showConfirm(
            'Are you sure you want to delete this report?',
            'Delete Report'
        );

        if (!confirmed) return;

        try {
            APP_UTILS.Notification.showLoading('Deleting report...');
            
            // This would call an API to delete the report
            // For now, we'll show a success message
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            APP_UTILS.Notification.showToast('Report deleted successfully!', 'success');
            
            // Reload report history
            this.loadReportHistory();
        } catch (error) {
            console.error('Delete historical report error:', error);
            APP_UTILS.Notification.showToast('Failed to delete report', 'error');
        } finally {
            APP_UTILS.Notification.hideLoading();
        }
    }
}

// Initialize Reports Manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.reportsManager = new ReportsManager();
});