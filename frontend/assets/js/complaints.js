// complaints.js - Complaints management for iReport
class ComplaintsManager {
    constructor() {
        this.currentFilters = {
            status: '',
            priority: '',
            crime_type: '',
            date_from: '',
            date_to: '',
            page: 1,
            limit: 10
        };
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadComplaints();
        this.initializeComponents();
    }

    // Setup event listeners
    setupEventListeners() {
        // Complaint form
        const complaintForm = document.getElementById('complaintForm');
        if (complaintForm) {
            complaintForm.addEventListener('submit', (e) => this.handleFileComplaint(e));
        }

        // Anonymous complaint form
        const anonymousForm = document.getElementById('anonymousComplaintForm');
        if (anonymousForm) {
            anonymousForm.addEventListener('submit', (e) => this.handleAnonymousComplaint(e));
        }

        // Filter forms
        const filterForm = document.getElementById('complaintFilters');
        if (filterForm) {
            filterForm.addEventListener('submit', (e) => this.handleFilter(e));
            filterForm.addEventListener('reset', (e) => this.handleResetFilters(e));
        }

        // Search input
        const searchInput = document.getElementById('complaintSearch');
        if (searchInput) {
            APP_UTILS.DOM.debouncedEventListener(searchInput, 'input', 
                (e) => this.handleSearch(e), 500);
        }

        // File upload
        const fileInputs = document.querySelectorAll('.evidence-upload');
        fileInputs.forEach(input => {
            input.addEventListener('change', (e) => this.handleFileUpload(e));
        });

        // Status update buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('update-status-btn')) {
                this.handleStatusUpdate(e);
            }
            
            if (e.target.classList.contains('view-details-btn')) {
                this.handleViewDetails(e);
            }
            
            if (e.target.classList.contains('track-complaint-btn')) {
                this.handleTrackComplaint(e);
            }
        });

        // Pagination
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('page-link')) {
                e.preventDefault();
                this.handlePagination(e);
            }
        });
    }

    // Initialize components
    initializeComponents() {
        // Initialize date pickers
        this.initializeDatePickers();
        
        // Initialize maps if available
        this.initializeLocationMap();
        
        // Load crime types dropdown
        this.loadCrimeTypes();
    }

    // Initialize date pickers
    initializeDatePickers() {
        const dateInputs = document.querySelectorAll('.date-picker');
        dateInputs.forEach(input => {
            // You can integrate with a date picker library here
            input.type = 'date';
        });
    }

    // Initialize location map
    initializeLocationMap() {
        const mapElement = document.getElementById('locationMap');
        if (mapElement && typeof L !== 'undefined') {
            this.map = L.map('locationMap').setView([20.5937, 78.9629], 5); // Center on India
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(this.map);
            
            // Add click event to get coordinates
            this.map.on('click', (e) => {
                this.handleMapClick(e);
            });
        }
    }

    // Load crime types dropdown
    loadCrimeTypes() {
        const crimeTypeSelects = document.querySelectorAll('.crime-type-select');
        crimeTypeSelects.forEach(select => {
            // Clear existing options except the first one
            while (select.options.length > 1) {
                select.remove(1);
            }
            
            // Add crime types from constants
            Object.entries(APP_CONSTANTS.CRIME_TYPES).forEach(([key, value]) => {
                const option = document.createElement('option');
                option.value = value;
                option.textContent = APP_UTILS.CrimeReport.getCrimeTypeDisplay(value);
                select.appendChild(option);
            });
        });
    }

    // Handle filing a complaint
    async handleFileComplaint(e) {
        e.preventDefault();
        
        if (!requireAuth()) return;
        
        const form = e.target;
        const formData = APP_UTILS.Form.serializeForm(form);
        
        // Validate complaint data
        const validation = APP_UTILS.CrimeReport.validateCrimeReport(formData);
        if (!validation.isValid) {
            APP_UTILS.Form.showFormErrors(form, validation.errors);
            return;
        }

        try {
            APP_UTILS.Notification.showLoading('Filing complaint...');
            APP_UTILS.Form.disableForm(form, true);

            // Handle file uploads if any
            const evidenceFiles = form.querySelector('#evidenceFiles').files;
            if (evidenceFiles.length > 0) {
                // You might want to upload files first and then include references in complaint data
                formData.evidence_files = await this.uploadEvidenceFiles(evidenceFiles);
            }

            const result = await API_SERVICE.fileComplaint(formData);
            
            if (result.success) {
                APP_UTILS.Notification.showToast('Complaint filed successfully!', 'success');
                form.reset();
                
                // Reset map if exists
                if (this.map) {
                    this.map.eachLayer((layer) => {
                        if (layer instanceof L.Marker) {
                            this.map.removeLayer(layer);
                        }
                    });
                }
                
                // Show tracking information
                this.showTrackingInfo(result.data);
                
            } else {
                throw new Error(result.message || 'Failed to file complaint');
            }
            
        } catch (error) {
            console.error('File complaint error:', error);
            APP_UTILS.Notification.showToast(
                APP_UTILS.API.handleError(error, 'Failed to file complaint. Please try again.'),
                'error'
            );
        } finally {
            APP_UTILS.Notification.hideLoading();
            APP_UTILS.Form.disableForm(form, false);
        }
    }

    // Handle anonymous complaint
    async handleAnonymousComplaint(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = APP_UTILS.Form.serializeForm(form);
        
        // Validate complaint data
        const validation = APP_UTILS.CrimeReport.validateCrimeReport(formData);
        if (!validation.isValid) {
            APP_UTILS.Form.showFormErrors(form, validation.errors);
            return;
        }

        try {
            APP_UTILS.Notification.showLoading('Filing anonymous complaint...');
            APP_UTILS.Form.disableForm(form, true);

            const result = await API_SERVICE.fileAnonymousComplaint(formData);
            
            if (result.success) {
                APP_UTILS.Notification.showToast('Anonymous complaint filed successfully!', 'success');
                form.reset();
                
                // Show tracking information
                this.showTrackingInfo(result.data, true);
                
            } else {
                throw new Error(result.message || 'Failed to file anonymous complaint');
            }
            
        } catch (error) {
            console.error('Anonymous complaint error:', error);
            APP_UTILS.Notification.showToast(
                APP_UTILS.API.handleError(error, 'Failed to file anonymous complaint. Please try again.'),
                'error'
            );
        } finally {
            APP_UTILS.Notification.hideLoading();
            APP_UTILS.Form.disableForm(form, false);
        }
    }

    // Handle file upload
    async handleFileUpload(e) {
        const input = e.target;
        const files = input.files;
        
        if (files.length === 0) return;
        
        const allowedTypes = APP_CONFIG.UI.ALLOWED_FILE_TYPES;
        const maxSize = APP_CONFIG.UI.MAX_FILE_SIZE;
        
        for (let file of files) {
            const validation = APP_UTILS.Validation.validateFile(file, allowedTypes, maxSize);
            if (!validation.isValid) {
                APP_UTILS.Notification.showToast(validation.errors[0], 'error');
                input.value = '';
                return;
            }
        }
        
        // Show file previews
        this.showFilePreviews(files, input);
    }

    // Upload evidence files
    async uploadEvidenceFiles(files) {
        const uploadedFiles = [];
        
        for (let file of files) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('type', 'evidence');
            
            try {
                // This would need a dedicated file upload endpoint
                // const response = await API_SERVICE.upload('/api/upload/evidence', formData);
                // uploadedFiles.push(response.data);
                
                // For now, just return file names
                uploadedFiles.push({
                    name: file.name,
                    size: file.size,
                    type: file.type
                });
            } catch (error) {
                console.error('File upload error:', error);
                APP_UTILS.Notification.showToast(`Failed to upload ${file.name}`, 'error');
            }
        }
        
        return uploadedFiles;
    }

    // Show file previews
    showFilePreviews(files, input) {
        const previewContainer = input.parentNode.querySelector('.file-previews');
        if (!previewContainer) return;
        
        previewContainer.innerHTML = '';
        
        Array.from(files).forEach(file => {
            const preview = APP_UTILS.DOM.createElement('div', {
                className: 'file-preview'
            }, [
                APP_UTILS.DOM.createElement('span', {
                    className: 'file-name'
                }, [file.name]),
                APP_UTILS.DOM.createElement('span', {
                    className: 'file-size'
                }, [`(${APP_UTILS.String.formatFileSize(file.size)})`]),
                APP_UTILS.DOM.createElement('button', {
                    type: 'button',
                    className: 'btn btn-sm btn-outline-danger remove-file',
                    onclick: (e) => this.removeFilePreview(e, file, input)
                }, ['×'])
            ]);
            
            previewContainer.appendChild(preview);
        });
    }

    // Remove file preview
    removeFilePreview(e, file, input) {
        e.target.closest('.file-preview').remove();
        
        // Remove file from input
        const dt = new DataTransfer();
        const files = input.files;
        
        for (let i = 0; i < files.length; i++) {
            if (files[i] !== file) {
                dt.items.add(files[i]);
            }
        }
        
        input.files = dt.files;
    }

    // Handle map click
    handleMapClick(e) {
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;
        
        // Update form fields
        const latInput = document.getElementById('latitude');
        const lngInput = document.getElementById('longitude');
        const locationInput = document.getElementById('location');
        
        if (latInput) latInput.value = lat;
        if (lngInput) lngInput.value = lng;
        
        // Reverse geocode to get address (simplified)
        if (locationInput) {
            locationInput.value = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
        }
        
        // Add marker to map
        if (this.map) {
            this.map.eachLayer((layer) => {
                if (layer instanceof L.Marker) {
                    this.map.removeLayer(layer);
                }
            });
            
            L.marker([lat, lng]).addTo(this.map)
                .bindPopup('Incident Location')
                .openPopup();
        }
    }

    // Load complaints based on current filters
    async loadComplaints() {
        const complaintsContainer = document.getElementById('complaintsContainer');
        if (!complaintsContainer) return;
        
        try {
            APP_UTILS.Notification.showLoading('Loading complaints...');
            
            let response;
            if (isPolice() || isAdmin()) {
                response = await API_SERVICE.getAllComplaints(this.currentFilters);
            } else {
                response = await API_SERVICE.getMyComplaints(this.currentFilters);
            }
            
            if (response.success) {
                this.renderComplaints(response.data.complaints || response.data);
                this.renderPagination(response.data.pagination);
                this.updateStats(response.data.stats);
            } else {
                throw new Error(response.message || 'Failed to load complaints');
            }
            
        } catch (error) {
            console.error('Load complaints error:', error);
            APP_UTILS.Notification.showToast(
                APP_UTILS.API.handleError(error, 'Failed to load complaints.'),
                'error'
            );
            
            complaintsContainer.innerHTML = `
                <div class="alert alert-danger">
                    Failed to load complaints. Please try again.
                </div>
            `;
        } finally {
            APP_UTILS.Notification.hideLoading();
        }
    }

    // Render complaints list
    renderComplaints(complaints) {
        const container = document.getElementById('complaintsContainer');
        if (!container) return;
        
        if (!complaints || complaints.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">No complaints found</h5>
                    <p class="text-muted">Try adjusting your filters or file a new complaint.</p>
                </div>
            `;
            return;
        }
        
        const complaintsHTML = complaints.map(complaint => {
            const summary = APP_UTILS.CrimeReport.generateCaseSummary(complaint);
            
            return `
                <div class="complaint-card card mb-3" data-case-id="${summary.id}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h5 class="card-title mb-0">${summary.title}</h5>
                            <div class="d-flex gap-2">
                                <span class="${summary.priorityClass}">${summary.priority}</span>
                                <span class="${summary.statusClass}">${summary.status}</span>
                            </div>
                        </div>
                        
                        <p class="card-text text-muted mb-2">
                            <i class="fas fa-shield-alt me-1"></i>
                            ${summary.crimeType}
                        </p>
                        
                        <p class="card-text mb-2">
                            <i class="fas fa-map-marker-alt me-1"></i>
                            ${summary.location}
                        </p>
                        
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                <i class="fas fa-clock me-1"></i>
                                ${summary.relativeTime}
                            </small>
                            
                            <div class="action-buttons">
                                <button class="btn btn-sm btn-outline-primary view-details-btn" 
                                        data-case-id="${summary.id}">
                                    <i class="fas fa-eye me-1"></i>View
                                </button>
                                
                                ${isPolice() || isAdmin() ? `
                                <button class="btn btn-sm btn-outline-secondary update-status-btn" 
                                        data-case-id="${summary.id}">
                                    <i class="fas fa-edit me-1"></i>Update
                                </button>
                                ` : ''}
                                
                                <button class="btn btn-sm btn-outline-info track-complaint-btn" 
                                        data-case-id="${summary.id}">
                                    <i class="fas fa-search me-1"></i>Track
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = complaintsHTML;
    }

    // Render pagination
    renderPagination(pagination) {
        const paginationContainer = document.getElementById('paginationContainer');
        if (!paginationContainer || !pagination) return;
        
        const { current_page, total_pages, has_previous, has_next } = pagination;
        
        let paginationHTML = `
            <nav aria-label="Complaints pagination">
                <ul class="pagination justify-content-center">
        `;
        
        // Previous button
        paginationHTML += `
            <li class="page-item ${!has_previous ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${current_page - 1}">
                    <i class="fas fa-chevron-left"></i>
                </a>
            </li>
        `;
        
        // Page numbers
        for (let i = 1; i <= total_pages; i++) {
            if (i === 1 || i === total_pages || (i >= current_page - 2 && i <= current_page + 2)) {
                paginationHTML += `
                    <li class="page-item ${i === current_page ? 'active' : ''}">
                        <a class="page-link" href="#" data-page="${i}">${i}</a>
                    </li>
                `;
            } else if (i === current_page - 3 || i === current_page + 3) {
                paginationHTML += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }
        
        // Next button
        paginationHTML += `
            <li class="page-item ${!has_next ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${current_page + 1}">
                    <i class="fas fa-chevron-right"></i>
                </a>
            </li>
        `;
        
        paginationHTML += `</ul></nav>`;
        paginationContainer.innerHTML = paginationHTML;
    }

    // Update statistics
    updateStats(stats) {
        if (!stats) return;
        
        const statsElements = {
            'totalComplaints': document.getElementById('totalComplaints'),
            'pendingComplaints': document.getElementById('pendingComplaints'),
            'resolvedComplaints': document.getElementById('resolvedComplaints'),
            'highPriorityComplaints': document.getElementById('highPriorityComplaints')
        };
        
        Object.entries(statsElements).forEach(([key, element]) => {
            if (element && stats[key] !== undefined) {
                element.textContent = stats[key];
            }
        });
    }

    // Handle filter application
    handleFilter(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = APP_UTILS.Form.serializeForm(form);
        
        // Update current filters
        this.currentFilters = {
            ...this.currentFilters,
            ...formData,
            page: 1 // Reset to first page when filtering
        };
        
        // Load complaints with new filters
        this.loadComplaints();
    }

    // Handle reset filters
    handleResetFilters(e) {
        e.preventDefault();
        
        this.currentFilters = {
            status: '',
            priority: '',
            crime_type: '',
            date_from: '',
            date_to: '',
            page: 1,
            limit: 10
        };
        
        this.loadComplaints();
    }

    // Handle search
    handleSearch(e) {
        const searchTerm = e.target.value.trim();
        this.currentFilters.search = searchTerm;
        this.currentFilters.page = 1;
        
        this.loadComplaints();
    }

    // Handle pagination
    handlePagination(e) {
        const page = parseInt(e.target.getAttribute('data-page'));
        if (!isNaN(page)) {
            this.currentFilters.page = page;
            this.loadComplaints();
            
            // Scroll to top of complaints list
            const complaintsContainer = document.getElementById('complaintsContainer');
            if (complaintsContainer) {
                APP_UTILS.DOM.scrollToElement(complaintsContainer, 100);
            }
        }
    }

    // Handle status update
    async handleStatusUpdate(e) {
        const caseId = e.target.getAttribute('data-case-id');
        if (!caseId) return;
        
        const currentStatus = e.target.closest('.complaint-card').querySelector('.badge').textContent;
        const newStatus = prompt('Enter new status (pending, assigned, in_progress, resolved, closed):', currentStatus);
        
        if (!newStatus || !['pending', 'assigned', 'in_progress', 'resolved', 'closed'].includes(newStatus)) {
            APP_UTILS.Notification.showToast('Invalid status', 'error');
            return;
        }
        
        try {
            APP_UTILS.Notification.showLoading('Updating status...');
            
            const result = await API_SERVICE.updateComplaintStatus(caseId, {
                status: newStatus
            });
            
            if (result.success) {
                APP_UTILS.Notification.showToast('Status updated successfully!', 'success');
                this.loadComplaints(); // Reload the list
            } else {
                throw new Error(result.message || 'Failed to update status');
            }
            
        } catch (error) {
            console.error('Update status error:', error);
            APP_UTILS.Notification.showToast(
                APP_UTILS.API.handleError(error, 'Failed to update status.'),
                'error'
            );
        } finally {
            APP_UTILS.Notification.hideLoading();
        }
    }

    // Handle view details
    async handleViewDetails(e) {
        const caseId = e.target.getAttribute('data-case-id');
        if (!caseId) return;
        
        try {
            APP_UTILS.Notification.showLoading('Loading complaint details...');
            
            const response = await API_SERVICE.getComplaintDetails(caseId);
            
            if (response.success) {
                this.showComplaintDetails(response.data);
            } else {
                throw new Error(response.message || 'Failed to load complaint details');
            }
            
        } catch (error) {
            console.error('View details error:', error);
            APP_UTILS.Notification.showToast(
                APP_UTILS.API.handleError(error, 'Failed to load complaint details.'),
                'error'
            );
        } finally {
            APP_UTILS.Notification.hideLoading();
        }
    }

    // Handle track complaint
    async handleTrackComplaint(e) {
        const caseId = e.target.getAttribute('data-case-id');
        if (!caseId) return;
        
        try {
            APP_UTILS.Notification.showLoading('Loading tracking information...');
            
            const response = await API_SERVICE.getTrackingDetails(caseId);
            
            if (response.success) {
                this.showTrackingInfo(response.data);
            } else {
                throw new Error(response.message || 'Failed to load tracking information');
            }
            
        } catch (error) {
            console.error('Track complaint error:', error);
            APP_UTILS.Notification.showToast(
                APP_UTILS.API.handleError(error, 'Failed to load tracking information.'),
                'error'
            );
        } finally {
            APP_UTILS.Notification.hideLoading();
        }
    }

    // Show complaint details in modal
    showComplaintDetails(complaint) {
        const summary = APP_UTILS.CrimeReport.generateCaseSummary(complaint);
        
        const modalHTML = `
            <div class="modal fade" id="complaintDetailsModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Complaint Details - ${summary.id}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>Basic Information</h6>
                                    <p><strong>Title:</strong> ${summary.title}</p>
                                    <p><strong>Crime Type:</strong> ${summary.crimeType}</p>
                                    <p><strong>Priority:</strong> <span class="${summary.priorityClass}">${summary.priority}</span></p>
                                    <p><strong>Status:</strong> <span class="${summary.statusClass}">${summary.status}</span></p>
                                </div>
                                <div class="col-md-6">
                                    <h6>Location & Time</h6>
                                    <p><strong>Location:</strong> ${summary.location}</p>
                                    <p><strong>Filed:</strong> ${summary.createdAt}</p>
                                    ${summary.assignedOfficer ? `
                                    <p><strong>Assigned Officer:</strong> ${summary.assignedOfficer}</p>
                                    ` : ''}
                                    ${summary.responseTime ? `
                                    <p><strong>Response Time:</strong> ${summary.responseTime} hours</p>
                                    ` : ''}
                                </div>
                            </div>
                            
                            <div class="mt-3">
                                <h6>Description</h6>
                                <p>${complaint.description || 'No description provided'}</p>
                            </div>
                            
                            ${complaint.evidence && complaint.evidence.length > 0 ? `
                            <div class="mt-3">
                                <h6>Evidence</h6>
                                <div class="evidence-gallery">
                                    ${complaint.evidence.map(evidence => `
                                        <div class="evidence-item">
                                            <img src="${evidence.url}" alt="Evidence" class="img-thumbnail" style="max-height: 100px;">
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                            ` : ''}
                            
                            ${complaint.updates && complaint.updates.length > 0 ? `
                            <div class="mt-3">
                                <h6>Case Updates</h6>
                                <div class="timeline">
                                    ${complaint.updates.map(update => `
                                        <div class="timeline-item">
                                            <div class="timeline-marker"></div>
                                            <div class="timeline-content">
                                                <strong>${APP_UTILS.Date.formatDate(update.created_at, 'dd/mm/yyyy hh:mm')}</strong>
                                                <p>${update.description}</p>
                                                <small class="text-muted">By: ${update.updated_by}</small>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                            ` : ''}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            ${isPolice() || isAdmin() ? `
                            <button type="button" class="btn btn-primary update-status-btn" data-case-id="${summary.id}">
                                Update Status
                            </button>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal
        const existingModal = document.getElementById('complaintDetailsModal');
        if (existingModal) existingModal.remove();
        
        // Add new modal to body
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('complaintDetailsModal'));
        modal.show();
    }

    // Show tracking information
    showTrackingInfo(trackingData, isAnonymous = false) {
        const modalHTML = `
            <div class="modal fade" id="trackingInfoModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Complaint Tracking</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="text-center mb-4">
                                <i class="fas fa-check-circle fa-3x text-success mb-3"></i>
                                <h4>Complaint Filed Successfully!</h4>
                            </div>
                            
                            <div class="tracking-info">
                                <p><strong>Case ID:</strong> ${trackingData.case_id}</p>
                                <p><strong>Status:</strong> <span class="badge bg-secondary">Pending</span></p>
                                <p><strong>Filed At:</strong> ${APP_UTILS.Date.formatDate(new Date(), 'dd/mm/yyyy hh:mm')}</p>
                                
                                ${isAnonymous ? `
                                <div class="alert alert-warning">
                                    <i class="fas fa-exclamation-triangle me-2"></i>
                                    <strong>Anonymous Complaint:</strong> Please save your Case ID for tracking purposes.
                                </div>
                                ` : ''}
                                
                                <div class="alert alert-info">
                                    <i class="fas fa-info-circle me-2"></i>
                                    You can track your complaint status using the Case ID.
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            <button type="button" class="btn btn-primary" onclick="window.location.href='track-complaint.html'">
                                Track Another Complaint
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal
        const existingModal = document.getElementById('trackingInfoModal');
        if (existingModal) existingModal.remove();
        
        // Add new modal to body
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('trackingInfoModal'));
        modal.show();
    }
}

// Initialize Complaints Manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.complaintsManager = new ComplaintsManager();
});