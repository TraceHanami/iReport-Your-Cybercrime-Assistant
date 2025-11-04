// api.js - Complete API service layer for iReport

// Check if already defined to prevent redeclaration
if (typeof window.API_SERVICE === 'undefined') {

class ApiService {
    constructor() {
        this.baseURL = window.API_BASE_URL;
        this.config = window.APP_CONFIG;
    }

    // ========== CORE API METHODS ==========

    async request(endpoint, options = {}) {
        try {
            // Use secureApiCall if available, otherwise fallback
            if (window.secureApiCall) {
                return await window.secureApiCall(endpoint, options);
            } else {
                // Fallback to basic fetch with auth
                const url = `${this.baseURL}${endpoint}`;
                const headers = window.getHeaders();
                
                const response = await fetch(url, {
                    ...options,
                    headers: {
                        ...headers,
                        ...options.headers
                    }
                });

                // Handle authentication errors
                if (response.status === 401) {
                    window.clearAuthData();
                    window.location.href = 'login.html';
                    throw new Error('Authentication required');
                }

                if (response.status === 403) {
                    throw new Error('Access denied');
                }

                return response;
            }
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    async get(endpoint, params = {}) {
        let url = endpoint;
        if (Object.keys(params).length > 0) {
            const queryParams = new URLSearchParams(params).toString();
            url += `?${queryParams}`;
        }
        return this.request(url, { method: 'GET' });
    }

    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async patch(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    }

    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    async upload(endpoint, formData) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = window.getUploadHeaders();
        
        const response = await fetch(url, {
            method: 'POST',
            headers: headers,
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }

        return response;
    }

    // ========== AUTHENTICATION API ==========

    async login(credentials) {
        const response = await this.post(this.config.ENDPOINTS.AUTH.LOGIN, credentials);
        const data = await response.json();
        
        if (data.success && data.token) {
            window.storeAuthData(data);
        }
        
        return data;
    }

    async register(userData) {
        const response = await this.post(this.config.ENDPOINTS.AUTH.REGISTER, userData);
        return response.json();
    }

    async verifyOTP(otpData) {
        const response = await this.post(this.config.ENDPOINTS.AUTH.VERIFY_OTP, otpData);
        const data = await response.json();
        
        if (data.success && data.token) {
            window.storeAuthData(data);
        }
        
        return data;
    }

    async forgotPassword(email) {
        return this.post(this.config.ENDPOINTS.AUTH.FORGOT_PASSWORD, { email });
    }

    async resetPassword(resetData) {
        return this.post(this.config.ENDPOINTS.AUTH.RESET_PASSWORD, resetData);
    }

    async getCurrentUser() {
        const response = await this.get(this.config.ENDPOINTS.AUTH.ME);
        return response.json();
    }

    async logout() {
        // Note: Backend might not have logout endpoint, we clear client-side
        window.clearAuthData();
        return { success: true, message: 'Logged out successfully' };
    }

    // ========== COMPLAINTS API ==========

    async fileComplaint(complaintData) {
        const response = await this.post(this.config.ENDPOINTS.COMPLAINTS.FILE, complaintData);
        return response.json();
    }

    async fileAnonymousComplaint(complaintData) {
        const response = await this.post(this.config.ENDPOINTS.COMPLAINTS.FILE_ANONYMOUS, complaintData);
        return response.json();
    }

    async getMyComplaints(params = {}) {
        const response = await this.get(this.config.ENDPOINTS.COMPLAINTS.MY_COMPLAINTS, params);
        return response.json();
    }

    async getAllComplaints(params = {}) {
        const response = await this.get(this.config.ENDPOINTS.COMPLAINTS.ALL_COMPLAINTS, params);
        return response.json();
    }

    async getComplaintDetails(caseId) {
        const endpoint = `${this.config.ENDPOINTS.COMPLAINTS.DETAILS}${caseId}`;
        const response = await this.get(endpoint);
        return response.json();
    }

    async updateComplaintStatus(caseId, statusData) {
        const endpoint = `${this.config.ENDPOINTS.COMPLAINTS.UPDATE_STATUS}${caseId}`;
        const response = await this.put(endpoint, statusData);
        return response.json();
    }

    // ========== TRACKING API ==========

    async trackComplaint(caseId) {
        const endpoint = `${this.config.ENDPOINTS.TRACKING.STATUS}${caseId}`;
        const response = await this.get(endpoint);
        return response.json();
    }

    async getTrackingDetails(caseId) {
        const endpoint = `${this.config.ENDPOINTS.TRACKING.DETAILS}${caseId}`;
        const response = await this.get(endpoint);
        return response.json();
    }

    // ========== POLICE API ==========

    async getPoliceDashboard() {
        const response = await this.get(this.config.ENDPOINTS.POLICE.DASHBOARD);
        return response.json();
    }

    async getPoliceCases(params = {}) {
        const response = await this.get(this.config.ENDPOINTS.POLICE.CASES, params);
        return response.json();
    }

    async getPoliceCaseDetails(caseId) {
        const endpoint = `${this.config.ENDPOINTS.POLICE.CASE_DETAILS}${caseId}`;
        const response = await this.get(endpoint);
        return response.json();
    }

    async updatePoliceCase(caseId, updateData) {
        const endpoint = `${this.config.ENDPOINTS.POLICE.UPDATE_CASE}${caseId}`;
        const response = await this.post(endpoint, updateData);
        return response.json();
    }

    async getOfficerPerformance() {
        const response = await this.get(this.config.ENDPOINTS.POLICE.PERFORMANCE);
        return response.json();
    }

    async getTeamPerformance() {
        const response = await this.get(this.config.ENDPOINTS.POLICE.TEAM_PERFORMANCE);
        return response.json();
    }

    async updateAvailability(availabilityData) {
        const response = await this.put(this.config.ENDPOINTS.POLICE.AVAILABILITY, availabilityData);
        return response.json();
    }

    // ========== ADMIN API ==========

    async getAdminDashboard() {
        const response = await this.get(this.config.ENDPOINTS.ADMIN.DASHBOARD);
        return response.json();
    }

    async getAllUsers(params = {}) {
        const response = await this.get(this.config.ENDPOINTS.ADMIN.USERS, params);
        return response.json();
    }

    async getAllAdminCases(params = {}) {
        const response = await this.get(this.config.ENDPOINTS.ADMIN.CASES, params);
        return response.json();
    }

    async getPoliceOfficers() {
        const response = await this.get(this.config.ENDPOINTS.ADMIN.POLICE_OFFICERS);
        return response.json();
    }

    async createPoliceOfficer(officerData) {
        const response = await this.post(this.config.ENDPOINTS.ADMIN.CREATE_POLICE, officerData);
        return response.json();
    }

    async getVolunteerApplications() {
        const response = await this.get(this.config.ENDPOINTS.ADMIN.VOLUNTEER_APPLICATIONS);
        return response.json();
    }

    async getPendingVolunteers() {
        const response = await this.get(this.config.ENDPOINTS.ADMIN.PENDING_VOLUNTEERS);
        return response.json();
    }

    async reviewVolunteerApplication(applicationId, reviewData) {
        const endpoint = `${this.config.ENDPOINTS.ADMIN.REVIEW_VOLUNTEER}${applicationId}/review`;
        const response = await this.post(endpoint, reviewData);
        return response.json();
    }

    async verifyVolunteer(volunteerId, verifyData) {
        const endpoint = `${this.config.ENDPOINTS.ADMIN.VERIFY_VOLUNTEER}${volunteerId}/verify`;
        const response = await this.post(endpoint, verifyData);
        return response.json();
    }

    async getCaseAssignments() {
        const response = await this.get(this.config.ENDPOINTS.ADMIN.CASE_ASSIGNMENTS);
        return response.json();
    }

    async assignCase(assignmentData) {
        const response = await this.post(this.config.ENDPOINTS.ADMIN.ASSIGN_CASE, assignmentData);
        return response.json();
    }

    async reassignCase(reassignmentData) {
        const response = await this.post(this.config.ENDPOINTS.ADMIN.REASSIGN_CASE, reassignmentData);
        return response.json();
    }

    async unassignCase(unassignmentData) {
        const response = await this.post(this.config.ENDPOINTS.ADMIN.UNASSIGN_CASE, unassignmentData);
        return response.json();
    }

    async getAdminAnalyticsOverview() {
        const response = await this.get(this.config.ENDPOINTS.ADMIN.ANALYTICS_OVERVIEW);
        return response.json();
    }

    async getOfficerPerformanceAnalytics() {
        const response = await this.get(this.config.ENDPOINTS.ADMIN.OFFICER_PERFORMANCE);
        return response.json();
    }

    // ========== ANALYTICS API ==========

    async getTrendAnalytics(params = {}) {
        const response = await this.get(this.config.ENDPOINTS.ANALYTICS.TRENDS, params);
        return response.json();
    }

    async getHeatmapData() {
        const response = await this.get(this.config.ENDPOINTS.ANALYTICS.HEATMAP);
        return response.json();
    }

    async getHighRiskAreas() {
        const response = await this.get(this.config.ENDPOINTS.ANALYTICS.HIGH_RISK_AREAS);
        return response.json();
    }

    async getPatrolRecommendations() {
        const response = await this.get(this.config.ENDPOINTS.ANALYTICS.PATROL_RECOMMENDATIONS);
        return response.json();
    }

    async getPerformanceMetrics() {
        const response = await this.get(this.config.ENDPOINTS.ANALYTICS.PERFORMANCE);
        return response.json();
    }

    async getPredictiveInsights() {
        const response = await this.get(this.config.ENDPOINTS.ANALYTICS.PREDICTIVE_INSIGHTS);
        return response.json();
    }

    // ========== CHATBOT API ==========

    async startChatSession() {
        const response = await this.post(this.config.ENDPOINTS.CHATBOT.START_SESSION);
        return response.json();
    }

    async sendChatMessage(sessionId, message) {
        const response = await this.post(this.config.ENDPOINTS.CHATBOT.SEND_MESSAGE, {
            session_id: sessionId,
            message: message
        });
        return response.json();
    }

    async getChatSessionHistory(sessionId) {
        const endpoint = `${this.config.ENDPOINTS.CHATBOT.SESSION_HISTORY}${sessionId}`;
        const response = await this.get(endpoint);
        return response.json();
    }

    async getUserChatSessions() {
        const response = await this.get(this.config.ENDPOINTS.CHATBOT.USER_SESSIONS);
        return response.json();
    }

    async deleteChatSession(sessionId) {
        const endpoint = `${this.config.ENDPOINTS.CHATBOT.DELETE_SESSION}${sessionId}`;
        const response = await this.delete(endpoint);
        return response.json();
    }

    // ========== NOTIFICATIONS API ==========

    async getUserNotifications() {
        const response = await this.get(this.config.ENDPOINTS.NOTIFICATIONS.USER);
        return response.json();
    }

    async markNotificationRead(notificationId) {
        const endpoint = `${this.config.ENDPOINTS.NOTIFICATIONS.MARK_READ}${notificationId}/read`;
        const response = await this.put(endpoint);
        return response.json();
    }

    async markAllNotificationsRead() {
        const response = await this.put(this.config.ENDPOINTS.NOTIFICATIONS.READ_ALL);
        return response.json();
    }

    async deleteNotification(notificationId) {
        const endpoint = `${this.config.ENDPOINTS.NOTIFICATIONS.MARK_READ}${notificationId}`;
        const response = await this.delete(endpoint);
        return response.json();
    }

    async clearAllNotifications() {
        const response = await this.delete(this.config.ENDPOINTS.NOTIFICATIONS.CLEAR_ALL);
        return response.json();
    }

    async getNotificationStats() {
        const response = await this.get(this.config.ENDPOINTS.NOTIFICATIONS.STATS);
        return response.json();
    }

    // ========== REPORTS API ==========

    async generateCaseReport(caseId, reportData = {}) {
        const endpoint = `${this.config.ENDPOINTS.REPORTS.CASE}${caseId}`;
        const response = await this.post(endpoint, reportData);
        return response.json();
    }

    async generateAnalyticsReport(reportData = {}) {
        const response = await this.post(this.config.ENDPOINTS.REPORTS.ANALYTICS, reportData);
        return response.json();
    }

    async listReports() {
        const response = await this.get(this.config.ENDPOINTS.REPORTS.LIST);
        return response.json();
    }

    async downloadReport(filename) {
        const endpoint = `${this.config.ENDPOINTS.REPORTS.DOWNLOAD}${filename}`;
        const response = await this.get(endpoint);
        
        if (response.ok) {
            // Create download link
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        }
        
        return response;
    }

    async cleanupReports() {
        const response = await this.post(this.config.ENDPOINTS.REPORTS.CLEANUP);
        return response.json();
    }

    async getSystemStatusReport() {
        const response = await this.get(this.config.ENDPOINTS.REPORTS.SYSTEM_STATUS);
        return response.json();
    }

    // ========== SMS API ==========

    async sendOTP(phoneData) {
        const response = await this.post(this.config.ENDPOINTS.SMS.SEND_OTP, phoneData);
        return response.json();
    }

    async getSMSLogs(params = {}) {
        const response = await this.get(this.config.ENDPOINTS.SMS.LOGS, params);
        return response.json();
    }

    async getSMSStatus() {
        const response = await this.get(this.config.ENDPOINTS.SMS.STATUS);
        return response.json();
    }

    async getSMSHealth() {
        const response = await this.get(this.config.ENDPOINTS.SMS.HEALTH);
        return response.json();
    }

    // ========== SYSTEM API ==========

    async getSystemHealth() {
        const response = await this.get(this.config.ENDPOINTS.SYSTEM.HEALTH);
        return response.json();
    }

    async getSystemStatus() {
        const response = await this.get(this.config.ENDPOINTS.SYSTEM.STATUS);
        return response.json();
    }

    async getAPIInfo() {
        const response = await this.get(this.config.ENDPOINTS.SYSTEM.INFO);
        return response.json();
    }

    // ========== UTILITY METHODS ==========

    async handleResponse(response) {
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        return response.json();
    }

    buildQueryString(params) {
        const searchParams = new URLSearchParams();
        Object.keys(params).forEach(key => {
            if (params[key] !== null && params[key] !== undefined) {
                searchParams.append(key, params[key]);
            }
        });
        return searchParams.toString();
    }

    // Check if user can access specific endpoint
    canAccess(endpoint) {
        return window.canAccessEndpoint ? window.canAccessEndpoint(endpoint) : true;
    }
}

// ========== GLOBAL API INSTANCE ==========

// Create global API service instance
window.API_SERVICE = new ApiService();

// Backward compatibility - expose individual functions
window.apiService = window.API_SERVICE;

// ========== USAGE EXAMPLES ==========

/*
// Example usage in your frontend:

// 1. Authentication
async function loginUser() {
    try {
        const result = await API_SERVICE.login({
            email: 'user@example.com',
            password: 'password123'
        });
        console.log('Login successful:', result);
    } catch (error) {
        console.error('Login failed:', error);
    }
}

// 2. File complaint
async function submitComplaint() {
    try {
        const result = await API_SERVICE.fileComplaint({
            title: 'Theft Report',
            description: 'My phone was stolen',
            crime_type: 'theft',
            location: 'Central Park',
            priority: 'high'
        });
        console.log('Complaint filed:', result);
    } catch (error) {
        console.error('Failed to file complaint:', error);
    }
}

// 3. Get police dashboard
async function loadPoliceDashboard() {
    if (!window.isPolice() && !window.isAdmin()) {
        alert('Access denied');
        return;
    }
    
    try {
        const dashboard = await API_SERVICE.getPoliceDashboard();
        console.log('Police dashboard:', dashboard);
    } catch (error) {
        console.error('Failed to load dashboard:', error);
    }
}

// 4. Upload evidence files
async function uploadEvidence(caseId, file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('case_id', caseId);
    formData.append('description', 'Evidence photo');
    
    try {
        const result = await API_SERVICE.upload('/api/complaints/upload-evidence', formData);
        console.log('Upload successful:', result);
    } catch (error) {
        console.error('Upload failed:', error);
    }
}
*/

console.log('✅ iReport API Service loaded successfully');

} // End of if condition