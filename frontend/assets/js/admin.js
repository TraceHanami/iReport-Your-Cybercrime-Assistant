// admin.js - Admin management for iReport
class AdminManager {
    constructor() {
        this.currentView = 'dashboard';
        this.init();
    }

    init() {
        if (!isAdmin()) {
            window.location.href = 'unauthorized.html';
            return;
        }

        this.setupEventListeners();
        this.loadAdminData();
        this.initializeComponents();
    }

    setupEventListeners() {
        // Admin navigation
        const adminNavItems = document.querySelectorAll('.admin-nav-item');
        adminNavItems.forEach(item => {
            item.addEventListener('click', (e) => this.handleNavigation(e));
        });

        // User management
        const userSearch = document.getElementById('userSearch');
        if (userSearch) {
            APP_UTILS.DOM.debouncedEventListener(userSearch, 'input', 
                (e) => this.handleUserSearch(e), 500);
        }

        // Case assignment
        const assignCaseForm = document.getElementById('assignCaseForm');
        if (assignCaseForm) {
            assignCaseForm.addEventListener('submit', (e) => this.handleAssignCase(e));
        }

        // Police officer management
        const createOfficerForm = document.getElementById('createOfficerForm');
        if (createOfficerForm) {
            createOfficerForm.addEventListener('submit', (e) => this.handleCreateOfficer(e));
        }

        // Volunteer management
        const volunteerActions = document.querySelectorAll('.volunteer-action');
        volunteerActions.forEach(btn => {
            btn.addEventListener('click', (e) => this.handleVolunteerAction(e));
        });

        // System settings
        const systemSettingsForm = document.getElementById('systemSettingsForm');
        if (systemSettingsForm) {
            systemSettingsForm.addEventListener('submit', (e) => this.handleSaveSystemSettings(e));
        }
    }

    initializeComponents() {
        this.initializeDataTables();
        this.initializeCharts();
    }

    initializeDataTables() {
        // Initialize DataTables for admin tables if library is available
        if (typeof $.fn.DataTable !== 'undefined') {
            $('.admin-table').DataTable({
                pageLength: 25,
                responsive: true
            });
        }
    }

    initializeCharts() {
        // Initialize admin-specific charts
    }

    async loadAdminData() {
        try {
            APP_UTILS.Notification.showLoading('Loading admin data...');

            const [dashboardData, usersData, casesData] = await Promise.all([
                API_SERVICE.getAdminDashboard(),
                API_SERVICE.getAllUsers(),
                API_SERVICE.getAllAdminCases()
            ]);

            if (dashboardData.success) {
                this.adminData = dashboardData.data;
                this.renderAdminDashboard();
            }

            if (usersData.success) {
                this.usersData = usersData.data;
                this.renderUsersManagement();
            }

            if (casesData.success) {
                this.casesData = casesData.data;
                this.renderCasesManagement();
            }

        } catch (error) {
            console.error('Load admin data error:', error);
            APP_UTILS.Notification.showToast(
                APP_UTILS.API.handleError(error, 'Failed to load admin data.'),
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
        const navItems = document.querySelectorAll('.admin-nav-item');
        navItems.forEach(item => item.classList.remove('active'));
        e.target.classList.add('active');
        
        // Load view-specific data
        this.loadViewData(target);
    }

    async loadViewData(view) {
        try {
            APP_UTILS.Notification.showLoading(`Loading ${view}...`);
            
            switch (view) {
                case 'users':
                    await this.loadUsersData();
                    break;
                case 'cases':
                    await this.loadCasesData();
                    break;
                case 'police':
                    await this.loadPoliceData();
                    break;
                case 'volunteers':
                    await this.loadVolunteersData();
                    break;
                case 'analytics':
                    await this.loadAdminAnalytics();
                    break;
                case 'settings':
                    await this.loadSystemSettings();
                    break;
            }
            
        } catch (error) {
            console.error(`Load ${view} data error:`, error);
            APP_UTILS.Notification.showToast(`Failed to load ${view} data`, 'error');
        } finally {
            APP_UTILS.Notification.hideLoading();
        }
    }

    // User Management
    async loadUsersData() {
        const response = await API_SERVICE.getAllUsers();
        if (response.success) {
            this.usersData = response.data;
            this.renderUsersManagement();
        }
    }

    renderUsersManagement() {
        const container = document.getElementById('usersManagement');
        if (!container) return;

        const users = this.usersData.users || [];
        
        container.innerHTML = `
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="card-title mb-0">User Management</h5>
                    <div class="d-flex gap-2">
                        <input type="text" id="userSearch" class="form-control form-control-sm" 
                               placeholder="Search users...">
                        <button class="btn btn-sm btn-primary" id="exportUsers">
                            <i class="fas fa-download me-1"></i>Export
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped table-hover admin-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Phone</th>
                                    <th>Role</th>
                                    <th>Status</th>
                                    <th>Registered</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${users.map(user => `
                                    <tr>
                                        <td>${user.id}</td>
                                        <td>${user.full_name}</td>
                                        <td>${user.email}</td>
                                        <td>${user.phone || 'N/A'}</td>
                                        <td>
                                            <span class="badge bg-${this.getRoleBadgeColor(user.role)}">
                                                ${formatRole(user.role)}
                                            </span>
                                        </td>
                                        <td>
                                            <span class="badge bg-${user.active ? 'success' : 'secondary'}">
                                                ${user.active ? 'Active' : 'Inactive'}
                                            </span>
                                        </td>
                                        <td>${APP_UTILS.Date.formatDate(user.created_at, 'dd/mm/yyyy')}</td>
                                        <td>
                                            <div class="btn-group btn-group-sm">
                                                <button class="btn btn-outline-primary view-user" 
                                                        data-user-id="${user.id}">
                                                    <i class="fas fa-eye"></i>
                                                </button>
                                                <button class="btn btn-outline-warning edit-user" 
                                                        data-user-id="${user.id}">
                                                    <i class="fas fa-edit"></i>
                                                </button>
                                                <button class="btn btn-outline-danger delete-user" 
                                                        data-user-id="${user.id}">
                                                    <i class="fas fa-trash"></i>
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;

        this.setupUserActions();
    }

    setupUserActions() {
        // View user
        const viewButtons = document.querySelectorAll('.view-user');
        viewButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const userId = e.target.closest('.view-user').getAttribute('data-user-id');
                this.viewUserDetails(userId);
            });
        });

        // Edit user
        const editButtons = document.querySelectorAll('.edit-user');
        editButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const userId = e.target.closest('.edit-user').getAttribute('data-user-id');
                this.editUser(userId);
            });
        });

        // Delete user
        const deleteButtons = document.querySelectorAll('.delete-user');
        deleteButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const userId = e.target.closest('.delete-user').getAttribute('data-user-id');
                this.deleteUser(userId);
            });
        });

        // Export users
        const exportBtn = document.getElementById('exportUsers');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportUsers());
        }
    }

    async viewUserDetails(userId) {
        // Implementation for viewing user details
        APP_UTILS.Notification.showToast(`View user ${userId}`, 'info');
    }

    async editUser(userId) {
        // Implementation for editing user
        APP_UTILS.Notification.showToast(`Edit user ${userId}`, 'info');
    }

    async deleteUser(userId) {
        const confirmed = await APP_UTILS.Notification.showConfirm(
            'Are you sure you want to delete this user? This action cannot be undone.',
            'Delete User'
        );

        if (!confirmed) return;

        try {
            APP_UTILS.Notification.showLoading('Deleting user...');
            
            // Here you would call an API to delete the user
            // For now, we'll simulate the action
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            APP_UTILS.Notification.showToast('User deleted successfully', 'success');
            
            // Reload users data
            this.loadUsersData();
        } catch (error) {
            console.error('Delete user error:', error);
            APP_UTILS.Notification.showToast('Failed to delete user', 'error');
        } finally {
            APP_UTILS.Notification.hideLoading();
        }
    }

    exportUsers() {
        if (this.usersData && this.usersData.users) {
            APP_UTILS.Export.exportToCSV(this.usersData.users, `users_export_${APP_UTILS.Date.formatDate(new Date(), 'yyyy-mm-dd')}.csv`);
        }
    }

    handleUserSearch(e) {
        const searchTerm = e.target.value.toLowerCase();
        const rows = document.querySelectorAll('#usersManagement tbody tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    }

    // Case Management
    async loadCasesData() {
        const response = await API_SERVICE.getAllAdminCases();
        if (response.success) {
            this.casesData = response.data;
            this.renderCasesManagement();
        }
    }

    renderCasesManagement() {
        // Similar structure to users management but for cases
    }

    // Police Officer Management
    async loadPoliceData() {
        const response = await API_SERVICE.getPoliceOfficers();
        if (response.success) {
            this.policeData = response.data;
            this.renderPoliceManagement();
        }
    }

    renderPoliceManagement() {
        // Implementation for police officer management
    }

    async handleCreateOfficer(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = APP_UTILS.Form.serializeForm(form);
        
        try {
            APP_UTILS.Notification.showLoading('Creating police officer...');
            APP_UTILS.Form.disableForm(form, true);

            const response = await API_SERVICE.createPoliceOfficer(formData);
            
            if (response.success) {
                APP_UTILS.Notification.showToast('Police officer created successfully!', 'success');
                form.reset();
                this.loadPoliceData();
            } else {
                throw new Error(response.message || 'Failed to create police officer');
            }
            
        } catch (error) {
            console.error('Create officer error:', error);
            APP_UTILS.Notification.showToast(
                APP_UTILS.API.handleError(error, 'Failed to create police officer.'),
                'error'
            );
        } finally {
            APP_UTILS.Notification.hideLoading();
            APP_UTILS.Form.disableForm(form, false);
        }
    }

    // Volunteer Management
    async loadVolunteersData() {
        const [applicationsResponse, pendingResponse] = await Promise.all([
            API_SERVICE.getVolunteerApplications(),
            API_SERVICE.getPendingVolunteers()
        ]);

        if (applicationsResponse.success && pendingResponse.success) {
            this.volunteersData = {
                applications: applicationsResponse.data,
                pending: pendingResponse.data
            };
            this.renderVolunteersManagement();
        }
    }

    renderVolunteersManagement() {
        // Implementation for volunteer management
    }

    async handleVolunteerAction(e) {
        const action = e.target.getAttribute('data-action');
        const volunteerId = e.target.getAttribute('data-volunteer-id');
        
        switch (action) {
            case 'approve':
                await this.approveVolunteer(volunteerId);
                break;
            case 'reject':
                await this.rejectVolunteer(volunteerId);
                break;
            case 'verify':
                await this.verifyVolunteer(volunteerId);
                break;
        }
    }

    async approveVolunteer(volunteerId) {
        // Implementation for approving volunteer
    }

    async rejectVolunteer(volunteerId) {
        // Implementation for rejecting volunteer
    }

    async verifyVolunteer(volunteerId) {
        // Implementation for verifying volunteer
    }

    // Case Assignment
    async handleAssignCase(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = APP_UTILS.Form.serializeForm(form);
        
        try {
            APP_UTILS.Notification.showLoading('Assigning case...');
            APP_UTILS.Form.disableForm(form, true);

            const response = await API_SERVICE.assignCase(formData);
            
            if (response.success) {
                APP_UTILS.Notification.showToast('Case assigned successfully!', 'success');
                form.reset();
            } else {
                throw new Error(response.message || 'Failed to assign case');
            }
            
        } catch (error) {
            console.error('Assign case error:', error);
            APP_UTILS.Notification.showToast(
                APP_UTILS.API.handleError(error, 'Failed to assign case.'),
                'error'
            );
        } finally {
            APP_UTILS.Notification.hideLoading();
            APP_UTILS.Form.disableForm(form, false);
        }
    }

    // Analytics
    async loadAdminAnalytics() {
        const [overviewResponse, performanceResponse] = await Promise.all([
            API_SERVICE.getAdminAnalyticsOverview(),
            API_SERVICE.getOfficerPerformanceAnalytics()
        ]);

        if (overviewResponse.success && performanceResponse.success) {
            this.analyticsData = {
                overview: overviewResponse.data,
                performance: performanceResponse.data
            };
            this.renderAdminAnalytics();
        }
    }

    renderAdminAnalytics() {
        // Implementation for admin analytics
    }

    // System Settings
    async loadSystemSettings() {
        // Implementation for loading system settings
    }

    async handleSaveSystemSettings(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = APP_UTILS.Form.serializeForm(form);
        
        try {
            APP_UTILS.Notification.showLoading('Saving system settings...');
            APP_UTILS.Form.disableForm(form, true);

            // Here you would call an API to save system settings
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            APP_UTILS.Notification.showToast('System settings saved successfully!', 'success');
            
        } catch (error) {
            console.error('Save settings error:', error);
            APP_UTILS.Notification.showToast('Failed to save system settings', 'error');
        } finally {
            APP_UTILS.Notification.hideLoading();
            APP_UTILS.Form.disableForm(form, false);
        }
    }

    getRoleBadgeColor(role) {
        const colors = {
            'admin': 'danger',
            'police': 'primary',
            'volunteer': 'success',
            'public': 'secondary'
        };
        return colors[role] || 'secondary';
    }

    // Utility methods for admin operations
    async bulkActionUsers(action, userIds) {
        // Implementation for bulk user actions
    }

    async generateSystemReport(type) {
        // Implementation for generating system reports
    }

    async backupSystem() {
        // Implementation for system backup
    }

    async restoreSystem(backupFile) {
        // Implementation for system restore
    }
}

// Initialize Admin Manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (isAdmin()) {
        window.adminManager = new AdminManager();
    }
});