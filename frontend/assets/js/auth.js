// auth.js - Authentication management for iReport
class AuthManager {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    init() {
        this.checkAuthState();
        this.setupEventListeners();
    }

    // Check authentication state on page load
    checkAuthState() {
        if (isAuthenticated()) {
            this.currentUser = getUserData();
            this.updateUIForAuthState(true);
            this.redirectToDashboard();
        } else {
            this.updateUIForAuthState(false);
        }
    }

    // Setup event listeners for auth-related elements
    setupEventListeners() {
        // Login form
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // Register form
        const registerForm = document.getElementById('registerForm');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegister(e));
        }

        // Logout buttons
        const logoutButtons = document.querySelectorAll('.logout-btn');
        logoutButtons.forEach(btn => {
            btn.addEventListener('click', (e) => this.handleLogout(e));
        });

        // Forgot password form
        const forgotPasswordForm = document.getElementById('forgotPasswordForm');
        if (forgotPasswordForm) {
            forgotPasswordForm.addEventListener('submit', (e) => this.handleForgotPassword(e));
        }

        // Reset password form
        const resetPasswordForm = document.getElementById('resetPasswordForm');
        if (resetPasswordForm) {
            resetPasswordForm.addEventListener('submit', (e) => this.handleResetPassword(e));
        }

        // OTP verification form
        const otpForm = document.getElementById('otpForm');
        if (otpForm) {
            otpForm.addEventListener('submit', (e) => this.handleOTPVerification(e));
        }
    }

    // Handle user login
    async handleLogin(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = APP_UTILS.Form.serializeForm(form);
        
        // Validate form
        const validationRules = {
            email: { required: true, email: true },
            password: { required: true }
        };
        
        const validation = APP_UTILS.Form.validateForm(form, validationRules);
        if (!validation.isValid) return;

        try {
            APP_UTILS.Notification.showLoading('Signing in...');
            APP_UTILS.Form.disableForm(form, true);

            const result = await API_SERVICE.login(formData);
            
            if (result.success) {
                APP_UTILS.Notification.showToast('Login successful!', 'success');
                
                // Store auth data
                storeAuthData(result);
                this.currentUser = getUserData();
                
                // Redirect to dashboard
                setTimeout(() => {
                    redirectToDashboard(this.currentUser.role);
                }, 1000);
                
            } else {
                throw new Error(result.message || 'Login failed');
            }
            
        } catch (error) {
            console.error('Login error:', error);
            APP_UTILS.Notification.showToast(
                APP_UTILS.API.handleError(error, 'Login failed. Please try again.'),
                'error'
            );
        } finally {
            APP_UTILS.Notification.hideLoading();
            APP_UTILS.Form.disableForm(form, false);
        }
    }

    // Handle user registration
    async handleRegister(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = APP_UTILS.Form.serializeForm(form);
        
        // Validate form
        const validationRules = {
            full_name: { required: true, minLength: 2 },
            email: { required: true, email: true },
            phone: { required: true, phone: true },
            password: { 
                required: true, 
                validate: (value) => {
                    const passwordValidation = validatePassword(value);
                    if (!passwordValidation.isValid) {
                        return 'Password must be at least 8 characters with uppercase, lowercase, number, and special character';
                    }
                    return null;
                }
            },
            confirm_password: {
                required: true,
                validate: (value, data) => {
                    if (value !== data.password) {
                        return 'Passwords do not match';
                    }
                    return null;
                }
            }
        };
        
        const validation = APP_UTILS.Form.validateForm(form, validationRules);
        if (!validation.isValid) return;

        try {
            APP_UTILS.Notification.showLoading('Creating account...');
            APP_UTILS.Form.disableForm(form, true);

            const result = await API_SERVICE.register(formData);
            
            if (result.success) {
                APP_UTILS.Notification.showToast('Registration successful! Please verify your OTP.', 'success');
                
                // Show OTP verification section
                this.showOTPSection(formData.email);
                
            } else {
                throw new Error(result.message || 'Registration failed');
            }
            
        } catch (error) {
            console.error('Registration error:', error);
            APP_UTILS.Notification.showToast(
                APP_UTILS.API.handleError(error, 'Registration failed. Please try again.'),
                'error'
            );
        } finally {
            APP_UTILS.Notification.hideLoading();
            APP_UTILS.Form.disableForm(form, false);
        }
    }

    // Handle OTP verification
    async handleOTPVerification(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = APP_UTILS.Form.serializeForm(form);
        const email = form.getAttribute('data-email');
        
        if (!email) {
            APP_UTILS.Notification.showToast('Email not found. Please try registering again.', 'error');
            return;
        }

        try {
            APP_UTILS.Notification.showLoading('Verifying OTP...');
            APP_UTILS.Form.disableForm(form, true);

            const result = await API_SERVICE.verifyOTP({
                email: email,
                otp: formData.otp
            });
            
            if (result.success) {
                APP_UTILS.Notification.showToast('OTP verified successfully!', 'success');
                
                // Store auth data and redirect
                storeAuthData(result);
                this.currentUser = getUserData();
                
                setTimeout(() => {
                    redirectToDashboard(this.currentUser.role);
                }, 1000);
                
            } else {
                throw new Error(result.message || 'OTP verification failed');
            }
            
        } catch (error) {
            console.error('OTP verification error:', error);
            APP_UTILS.Notification.showToast(
                APP_UTILS.API.handleError(error, 'OTP verification failed. Please try again.'),
                'error'
            );
        } finally {
            APP_UTILS.Notification.hideLoading();
            APP_UTILS.Form.disableForm(form, false);
        }
    }

    // Handle forgot password
    async handleForgotPassword(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = APP_UTILS.Form.serializeForm(form);
        
        // Validate form
        const validationRules = {
            email: { required: true, email: true }
        };
        
        const validation = APP_UTILS.Form.validateForm(form, validationRules);
        if (!validation.isValid) return;

        try {
            APP_UTILS.Notification.showLoading('Sending reset instructions...');
            APP_UTILS.Form.disableForm(form, true);

            const result = await API_SERVICE.forgotPassword(formData);
            
            if (result.success) {
                APP_UTILS.Notification.showToast('Password reset instructions sent to your email!', 'success');
                form.reset();
                
                // Show back to login link
                const backToLogin = document.getElementById('backToLogin');
                if (backToLogin) APP_UTILS.DOM.show(backToLogin);
                
            } else {
                throw new Error(result.message || 'Failed to send reset instructions');
            }
            
        } catch (error) {
            console.error('Forgot password error:', error);
            APP_UTILS.Notification.showToast(
                APP_UTILS.API.handleError(error, 'Failed to send reset instructions. Please try again.'),
                'error'
            );
        } finally {
            APP_UTILS.Notification.hideLoading();
            APP_UTILS.Form.disableForm(form, false);
        }
    }

    // Handle reset password
    async handleResetPassword(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = APP_UTILS.Form.serializeForm(form);
        const token = new URLSearchParams(window.location.search).get('token');
        
        if (!token) {
            APP_UTILS.Notification.showToast('Invalid reset link', 'error');
            return;
        }

        // Validate form
        const validationRules = {
            password: { 
                required: true, 
                validate: (value) => {
                    const passwordValidation = validatePassword(value);
                    if (!passwordValidation.isValid) {
                        return 'Password must be at least 8 characters with uppercase, lowercase, number, and special character';
                    }
                    return null;
                }
            },
            confirm_password: {
                required: true,
                validate: (value, data) => {
                    if (value !== data.password) {
                        return 'Passwords do not match';
                    }
                    return null;
                }
            }
        };
        
        const validation = APP_UTILS.Form.validateForm(form, validationRules);
        if (!validation.isValid) return;

        try {
            APP_UTILS.Notification.showLoading('Resetting password...');
            APP_UTILS.Form.disableForm(form, true);

            const result = await API_SERVICE.resetPassword({
                token: token,
                password: formData.password
            });
            
            if (result.success) {
                APP_UTILS.Notification.showToast('Password reset successfully!', 'success');
                
                // Redirect to login page
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 2000);
                
            } else {
                throw new Error(result.message || 'Password reset failed');
            }
            
        } catch (error) {
            console.error('Reset password error:', error);
            APP_UTILS.Notification.showToast(
                APP_UTILS.API.handleError(error, 'Password reset failed. Please try again.'),
                'error'
            );
        } finally {
            APP_UTILS.Notification.hideLoading();
            APP_UTILS.Form.disableForm(form, false);
        }
    }

    // Handle user logout
    async handleLogout(e) {
        e.preventDefault();
        
        const confirmed = await APP_UTILS.Notification.showConfirm(
            'Are you sure you want to logout?',
            'Confirm Logout'
        );
        
        if (confirmed) {
            try {
                APP_UTILS.Notification.showLoading('Logging out...');
                
                // Call logout endpoint if available
                await API_SERVICE.logout();
                
            } catch (error) {
                console.error('Logout error:', error);
            } finally {
                // Always clear client-side data
                clearAuthData();
                this.currentUser = null;
                this.updateUIForAuthState(false);
                
                APP_UTILS.Notification.hideLoading();
                APP_UTILS.Notification.showToast('Logged out successfully', 'success');
                
                // Redirect to login page
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 1000);
            }
        }
    }

    // Show OTP verification section
    showOTPSection(email) {
        const registerSection = document.getElementById('registerSection');
        const otpSection = document.getElementById('otpSection');
        const otpForm = document.getElementById('otpForm');
        
        if (registerSection) APP_UTILS.DOM.hide(registerSection);
        if (otpSection) {
            APP_UTILS.DOM.show(otpSection);
            if (otpForm) {
                otpForm.setAttribute('data-email', email);
            }
        }
    }

    // Update UI based on authentication state
    updateUIForAuthState(isAuthenticated) {
        const authElements = document.querySelectorAll('.auth-only');
        const unauthElements = document.querySelectorAll('.unauth-only');
        
        if (isAuthenticated) {
            authElements.forEach(el => APP_UTILS.DOM.show(el));
            unauthElements.forEach(el => APP_UTILS.DOM.hide(el));
            
            // Update user info in navbar
            this.updateUserInfo();
        } else {
            authElements.forEach(el => APP_UTILS.DOM.hide(el));
            unauthElements.forEach(el => APP_UTILS.DOM.show(el));
        }
    }

    // Update user information in UI
    updateUserInfo() {
        const user = this.currentUser;
        if (!user) return;

        // Update user display name
        const userDisplayElements = document.querySelectorAll('.user-display-name');
        userDisplayElements.forEach(el => {
            el.textContent = getUserDisplayName();
        });

        // Update user initials
        const userInitialElements = document.querySelectorAll('.user-initials');
        userInitialElements.forEach(el => {
            el.textContent = getUserInitials();
        });

        // Update user role
        const userRoleElements = document.querySelectorAll('.user-role');
        userRoleElements.forEach(el => {
            el.textContent = formatRole(user.role);
        });

        // Update user avatar
        const userAvatarElements = document.querySelectorAll('.user-avatar');
        userAvatarElements.forEach(el => {
            if (user.profile_picture) {
                el.src = user.profile_picture;
                el.alt = getUserDisplayName();
            } else {
                // Use initials as fallback
                el.style.display = 'none';
                const fallback = el.nextElementSibling;
                if (fallback && fallback.classList.contains('avatar-fallback')) {
                    fallback.textContent = getUserInitials();
                    fallback.style.display = 'flex';
                }
            }
        });
    }

    // Redirect to appropriate dashboard
    redirectToDashboard() {
        const currentPage = window.location.pathname;
        if (currentPage.includes('login.html') || currentPage.includes('register.html')) {
            redirectToDashboard(this.currentUser.role);
        }
    }

    // Check if user has specific permission
    hasPermission(permission) {
        if (!this.currentUser) return false;
        
        const userPermissions = this.currentUser.permissions || [];
        return userPermissions.includes(permission);
    }

    // Get current user
    getCurrentUser() {
        return this.currentUser;
    }

    // Check if user can access feature
    canAccessFeature(feature) {
        if (!this.currentUser) return false;
        
        const featureAccess = {
            'file_complaint': ['public', 'police', 'admin', 'volunteer'],
            'view_analytics': ['police', 'admin'],
            'manage_users': ['admin'],
            'assign_cases': ['admin'],
            'update_case_status': ['police', 'admin']
        };
        
        const allowedRoles = featureAccess[feature] || [];
        return allowedRoles.includes(this.currentUser.role);
    }
}

// Initialize Auth Manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.authManager = new AuthManager();
});