// script.js - Main application script for iReport

class iReportApp {
    constructor() {
        this.version = APP_CONFIG.APP_VERSION;
        this.modules = {};
        this.init();
    }

    init() {
        this.initializeApp();
        this.setupGlobalEventListeners();
        this.setupServiceWorker();
        this.setupErrorHandling();
    }

    // Initialize the application
    initializeApp() {
        console.log(`🚀 iReport v${this.version} initializing...`);
        
        // Check authentication state
        this.checkAuthState();
        
        // Initialize theme
        this.initializeTheme();
        
        // Initialize language
        this.initializeLanguage();
        
        // Setup navigation
        this.setupNavigation();
        
        // Setup notifications
        this.setupNotifications();
        
        // Mark app as initialized
        document.body.setAttribute('data-app-initialized', 'true');
        
        console.log('✅ iReport app initialized successfully');
    }

    // Check authentication state and redirect if needed
    checkAuthState() {
        const currentPage = window.location.pathname;
        const publicPages = ['/login.html', '/register.html', '/forgot-password.html'];
        const isPublicPage = publicPages.some(page => currentPage.includes(page));
        
        if (isAuthenticated() && isPublicPage) {
            // Redirect authenticated users away from auth pages
            redirectToDashboard(getUserRole());
        } else if (!isAuthenticated() && !isPublicPage) {
            // Redirect unauthenticated users to login
            window.location.href = 'login.html';
        }
    }

    // Initialize theme from user preference
    initializeTheme() {
        const savedTheme = localStorage.getItem(STORAGE_KEYS.THEME) || 'light';
        this.setTheme(savedTheme);
    }

    // Set application theme
    setTheme(theme) {
        const validThemes = ['light', 'dark', 'auto'];
        const selectedTheme = validThemes.includes(theme) ? theme : 'light';
        
        document.documentElement.setAttribute('data-bs-theme', selectedTheme);
        localStorage.setItem(STORAGE_KEYS.THEME, selectedTheme);
        
        // Update theme toggle button if exists
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            if (icon) {
                icon.className = selectedTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            }
        }
    }

    // Toggle between light and dark themes
    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-bs-theme') || 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    }

    // Initialize language from user preference
    initializeLanguage() {
        const savedLanguage = localStorage.getItem(STORAGE_KEYS.LANGUAGE) || 'en';
        this.setLanguage(savedLanguage);
    }

    // Set application language
    setLanguage(language) {
        const validLanguages = ['en', 'hi', 'ta', 'te'];
        const selectedLanguage = validLanguages.includes(language) ? language : 'en';
        
        document.documentElement.setAttribute('lang', selectedLanguage);
        localStorage.setItem(STORAGE_KEYS.LANGUAGE, selectedLanguage);
        
        // Update UI texts (you would need translation files for this)
        this.updateUITexts(selectedLanguage);
    }

    // Update UI texts based on language
    updateUITexts(language) {
        // This would load translation files and update all texts
        // For now, we'll just update the language selector
        const languageSelect = document.getElementById('languageSelect');
        if (languageSelect) {
            languageSelect.value = language;
        }
    }

    // Setup global event listeners
    setupGlobalEventListeners() {
        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }

        // Language selector
        const languageSelect = document.getElementById('languageSelect');
        if (languageSelect) {
            languageSelect.addEventListener('change', (e) => {
                this.setLanguage(e.target.value);
            });
        }

        // Mobile menu toggle
        const mobileMenuToggle = document.getElementById('mobileMenuToggle');
        if (mobileMenuToggle) {
            mobileMenuToggle.addEventListener('click', () => this.toggleMobileMenu());
        }

        // Search functionality
        const globalSearch = document.getElementById('globalSearch');
        if (globalSearch) {
            APP_UTILS.DOM.debouncedEventListener(globalSearch, 'input', 
                (e) => this.handleGlobalSearch(e), 500);
        }

        // Notifications bell
        const notificationsBell = document.getElementById('notificationsBell');
        if (notificationsBell) {
            notificationsBell.addEventListener('click', (e) => this.showNotificationsDropdown(e));
        }

        // User profile dropdown
        const userAvatar = document.getElementById('userAvatar');
        if (userAvatar) {
            userAvatar.addEventListener('click', (e) => this.showUserDropdown(e));
        }

        // Handle clicks outside dropdowns
        document.addEventListener('click', (e) => this.handleOutsideClick(e));

        // Handle keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));

        // Handle online/offline status
        window.addEventListener('online', () => this.handleOnlineStatus());
        window.addEventListener('offline', () => this.handleOfflineStatus());

        // Handle page visibility
        document.addEventListener('visibilitychange', () => this.handleVisibilityChange());
    }

    // Setup service worker for PWA
    setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker
                .register('/sw.js')
                .then(registration => {
                    console.log('✅ Service Worker registered:', registration);
                })
                .catch(error => {
                    console.log('❌ Service Worker registration failed:', error);
                });
        }
    }

    // Setup global error handling
    setupErrorHandling() {
        window.addEventListener('error', (e) => {
            console.error('Global error:', e.error);
            this.handleError(e.error);
        });

        window.addEventListener('unhandledrejection', (e) => {
            console.error('Unhandled promise rejection:', e.reason);
            this.handleError(e.reason);
            e.preventDefault();
        });
    }

    // Handle global errors
    handleError(error) {
        const errorMessage = APP_UTILS.API.handleError(error);
        
        // Don't show toast for network errors that are already handled
        if (!errorMessage.includes('Network error')) {
            APP_UTILS.Notification.showToast(errorMessage, 'error');
        }

        // Log to error reporting service
        this.logError(error);
    }

    // Log error to reporting service
    logError(error) {
        const errorData = {
            message: error.message,
            stack: error.stack,
            url: window.location.href,
            user: getUserData() ? getUserDisplayName() : 'anonymous',
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent
        };

        // In a real app, you'd send this to an error reporting service
        console.log('Error logged:', errorData);
    }

    // Setup navigation
    setupNavigation() {
        // Highlight current page in navigation
        this.highlightCurrentPage();

        // Setup sidebar toggle for mobile
        this.setupSidebarToggle();

        // Setup role-based navigation
        this.setupRoleBasedNavigation();
    }

    // Highlight current page in navigation
    highlightCurrentPage() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && currentPath.includes(href.replace('.html', ''))) {
                link.classList.add('active');
                link.setAttribute('aria-current', 'page');
            } else {
                link.classList.remove('active');
                link.removeAttribute('aria-current');
            }
        });
    }

    // Setup sidebar toggle for mobile
    setupSidebarToggle() {
        const sidebarToggle = document.getElementById('sidebarToggle');
        const sidebar = document.getElementById('sidebar');
        
        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener('click', () => {
                sidebar.classList.toggle('collapsed');
                
                // Update toggle icon
                const icon = sidebarToggle.querySelector('i');
                if (icon) {
                    icon.className = sidebar.classList.contains('collapsed') ? 
                        'fas fa-bars' : 'fas fa-times';
                }
            });
        }
    }

    // Setup role-based navigation
    setupRoleBasedNavigation() {
        const userRole = getUserRole();
        const navItems = document.querySelectorAll('.nav-item[data-role]');
        
        navItems.forEach(item => {
            const allowedRoles = item.getAttribute('data-role').split(' ');
            if (!allowedRoles.includes(userRole)) {
                item.style.display = 'none';
            }
        });
    }

    // Setup notifications
    setupNotifications() {
        if (isAuthenticated()) {
            this.loadNotifications();
            this.setupNotificationPolling();
        }
    }

    // Load user notifications
    async loadNotifications() {
        try {
            const response = await API_SERVICE.getUserNotifications();
            if (response.success) {
                this.renderNotifications(response.data);
            }
        } catch (error) {
            console.error('Failed to load notifications:', error);
        }
    }

    // Render notifications
    renderNotifications(notifications) {
        const notificationsContainer = document.getElementById('notificationsDropdown');
        if (!notificationsContainer) return;

        const unreadCount = notifications.unread_count || 0;
        const notificationItems = notifications.notifications || [];

        // Update notification badge
        const notificationBadge = document.getElementById('notificationBadge');
        if (notificationBadge) {
            notificationBadge.textContent = unreadCount;
            notificationBadge.style.display = unreadCount > 0 ? 'block' : 'none';
        }

        // Render notifications dropdown
        let notificationsHTML = '';
        
        if (notificationItems.length === 0) {
            notificationsHTML = '<div class="dropdown-item text-muted text-center">No notifications</div>';
        } else {
            notificationItems.slice(0, 5).forEach(notification => {
                notificationsHTML += `
                    <div class="dropdown-item notification-item ${notification.read ? '' : 'unread'}" 
                         data-notification-id="${notification.id}">
                        <div class="d-flex align-items-start">
                            <i class="fas ${this.getNotificationIcon(notification.type)} text-${this.getNotificationColor(notification.type)} me-2 mt-1"></i>
                            <div class="flex-grow-1">
                                <p class="mb-1">${notification.message}</p>
                                <small class="text-muted">${APP_UTILS.Date.getRelativeTime(notification.created_at)}</small>
                            </div>
                            ${!notification.read ? '<span class="badge bg-primary ms-2">New</span>' : ''}
                        </div>
                    </div>
                `;
            });
            
            if (notificationItems.length > 5) {
                notificationsHTML += `
                    <div class="dropdown-divider"></div>
                    <a class="dropdown-item text-center" href="notifications.html">
                        View all notifications
                    </a>
                `;
            }
        }

        notificationsContainer.innerHTML = notificationsHTML;

        // Add click handlers for notification items
        const notificationItemsElements = notificationsContainer.querySelectorAll('.notification-item');
        notificationItemsElements.forEach(item => {
            item.addEventListener('click', (e) => this.handleNotificationClick(e));
        });
    }

    // Setup notification polling
    setupNotificationPolling() {
        // Poll for new notifications every 30 seconds
        setInterval(() => {
            this.loadNotifications();
        }, 30000);
    }

    // Get notification icon
    getNotificationIcon(type) {
        const icons = {
            'case_update': 'fa-sync-alt',
            'new_case': 'fa-clipboard-list',
            'assignment': 'fa-user-plus',
            'system': 'fa-cog',
            'alert': 'fa-bell',
            'info': 'fa-info-circle'
        };
        return icons[type] || 'fa-bell';
    }

    // Get notification color
    getNotificationColor(type) {
        const colors = {
            'case_update': 'info',
            'new_case': 'primary',
            'assignment': 'success',
            'system': 'secondary',
            'alert': 'warning',
            'info': 'info'
        };
        return colors[type] || 'primary';
    }

    // Handle notification click
    async handleNotificationClick(e) {
        const notificationItem = e.currentTarget;
        const notificationId = notificationItem.getAttribute('data-notification-id');
        
        // Mark as read
        try {
            await API_SERVICE.markNotificationRead(notificationId);
            notificationItem.classList.remove('unread');
            
            // Update badge count
            const notificationBadge = document.getElementById('notificationBadge');
            if (notificationBadge) {
                const currentCount = parseInt(notificationBadge.textContent) || 0;
                if (currentCount > 0) {
                    notificationBadge.textContent = currentCount - 1;
                    if (currentCount - 1 === 0) {
                        notificationBadge.style.display = 'none';
                    }
                }
            }
        } catch (error) {
            console.error('Failed to mark notification as read:', error);
        }
        
        // TODO: Handle notification action based on type
    }

    // Toggle mobile menu
    toggleMobileMenu() {
        const navbarCollapse = document.getElementById('navbarCollapse');
        if (navbarCollapse) {
            navbarCollapse.classList.toggle('show');
        }
    }

    // Handle global search
    handleGlobalSearch(e) {
        const searchTerm = e.target.value.trim();
        
        if (searchTerm.length < 2) return;
        
        // You can implement global search functionality here
        console.log('Global search:', searchTerm);
        
        // For now, just show a toast
        APP_UTILS.Notification.showToast(`Searching for: ${searchTerm}`, 'info');
    }

    // Show notifications dropdown
    showNotificationsDropdown(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const dropdown = e.target.closest('.dropdown').querySelector('.dropdown-menu');
        dropdown.classList.toggle('show');
    }

    // Show user dropdown
    showUserDropdown(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const dropdown = e.target.closest('.dropdown').querySelector('.dropdown-menu');
        dropdown.classList.toggle('show');
    }

    // Handle clicks outside dropdowns
    handleOutsideClick(e) {
        // Close all dropdowns when clicking outside
        if (!e.target.closest('.dropdown')) {
            const dropdowns = document.querySelectorAll('.dropdown-menu.show');
            dropdowns.forEach(dropdown => {
                dropdown.classList.remove('show');
            });
        }
    }

    // Handle keyboard shortcuts
    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('globalSearch');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to close modals and dropdowns
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal.show');
            if (openModals.length > 0) {
                const modal = bootstrap.Modal.getInstance(openModals[0]);
                if (modal) modal.hide();
            }
            
            const openDropdowns = document.querySelectorAll('.dropdown-menu.show');
            openDropdowns.forEach(dropdown => {
                dropdown.classList.remove('show');
            });
        }
    }

    // Handle online status
    handleOnlineStatus() {
        APP_UTILS.Notification.showToast('You are back online', 'success');
        document.body.classList.remove('offline');
    }

    // Handle offline status
    handleOfflineStatus() {
        APP_UTILS.Notification.showToast('You are offline. Some features may not work.', 'warning');
        document.body.classList.add('offline');
    }

    // Handle page visibility change
    handleVisibilityChange() {
        if (document.hidden) {
            // Page is hidden
            console.log('Page hidden');
        } else {
            // Page is visible
            console.log('Page visible');
            // Refresh data if needed
            if (isAuthenticated()) {
                this.loadNotifications();
            }
        }
    }

    // Register module
    registerModule(name, module) {
        this.modules[name] = module;
    }

    // Get module
    getModule(name) {
        return this.modules[name];
    }

    // Show loading state
    showLoading(message = 'Loading...') {
        APP_UTILS.Notification.showLoading(message);
    }

    // Hide loading state
    hideLoading() {
        APP_UTILS.Notification.hideLoading();
    }

    // Show success message
    showSuccess(message) {
        APP_UTILS.Notification.showToast(message, 'success');
    }

    // Show error message
    showError(message) {
        APP_UTILS.Notification.showToast(message, 'error');
    }

    // Show warning message
    showWarning(message) {
        APP_UTILS.Notification.showToast(message, 'warning');
    }

    // Show info message
    showInfo(message) {
        APP_UTILS.Notification.showToast(message, 'info');
    }

    // Confirm action
    async confirmAction(message, title = 'Confirm Action') {
        return await APP_UTILS.Notification.showConfirm(message, title);
    }

    // Format date
    formatDate(date, format = 'dd/mm/yyyy') {
        return APP_UTILS.Date.formatDate(date, format);
    }

    // Format file size
    formatFileSize(bytes) {
        return APP_UTILS.String.formatFileSize(bytes);
    }

    // Validate email
    validateEmail(email) {
        return APP_UTILS.Validation.validateEmail(email);
    }

    // Validate phone
    validatePhone(phone) {
        return APP_UTILS.Validation.validatePhone(phone);
    }

    // Get user display name
    getUserDisplayName() {
        return getUserDisplayName();
    }

    // Get user role
    getUserRole() {
        return getUserRole();
    }

    // Check if user has role
    hasRole(role) {
        return hasRole(role);
    }

    // Check if user can access feature
    canAccessFeature(feature) {
        return window.authManager ? window.authManager.canAccessFeature(feature) : false;
    }

    // Logout user
    logout() {
        if (window.authManager) {
            window.authManager.handleLogout(new Event('click'));
        } else {
            clearAuthData();
            window.location.href = 'login.html';
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.iReportApp = new iReportApp();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = iReportApp;
}