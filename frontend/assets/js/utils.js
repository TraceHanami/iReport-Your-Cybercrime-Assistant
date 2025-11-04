// utils.js - Comprehensive utility functions for iReport

// Check if already defined to prevent redeclaration
if (typeof window.APP_UTILS === 'undefined') {

// ========== DOM MANIPULATION UTILITIES ==========

const DOMUtils = {
    // Create element with attributes and children
    createElement(tag, attributes = {}, children = []) {
        const element = document.createElement(tag);
        
        // Set attributes
        Object.keys(attributes).forEach(key => {
            if (key === 'className') {
                element.className = attributes[key];
            } else if (key === 'htmlFor') {
                element.htmlFor = attributes[key];
            } else if (key.startsWith('on') && typeof attributes[key] === 'function') {
                element[key] = attributes[key];
            } else {
                element.setAttribute(key, attributes[key]);
            }
        });
        
        // Append children
        children.forEach(child => {
            if (typeof child === 'string') {
                element.appendChild(document.createTextNode(child));
            } else if (child instanceof Node) {
                element.appendChild(child);
            }
        });
        
        return element;
    },
    
    // Get element by ID with optional default value
    getElement(id, defaultValue = null) {
        const element = document.getElementById(id);
        return element || defaultValue;
    },
    
    // Query selector with optional context
    query(selector, context = document) {
        return context.querySelector(selector);
    },
    
    // Query all elements
    queryAll(selector, context = document) {
        return Array.from(context.querySelectorAll(selector));
    },
    
    // Show element
    show(element) {
        if (typeof element === 'string') element = this.getElement(element);
        if (element) element.style.display = '';
        return element;
    },
    
    // Hide element
    hide(element) {
        if (typeof element === 'string') element = this.getElement(element);
        if (element) element.style.display = 'none';
        return element;
    },
    
    // Toggle element visibility
    toggle(element, force) {
        if (typeof element === 'string') element = this.getElement(element);
        if (element) {
            element.style.display = force !== undefined ? 
                (force ? '' : 'none') : 
                (element.style.display === 'none' ? '' : 'none');
        }
        return element;
    },
    
    // Add multiple event listeners
    addEventListener(element, events, handler, options = {}) {
        if (typeof element === 'string') element = this.getElement(element);
        if (!element) return;
        
        events.split(' ').forEach(event => {
            element.addEventListener(event, handler, options);
        });
    },
    
    // Remove event listeners
    removeEventListener(element, events, handler) {
        if (typeof element === 'string') element = this.getElement(element);
        if (!element) return;
        
        events.split(' ').forEach(event => {
            element.removeEventListener(event, handler);
        });
    },
    
    // Debounced event listener
    debouncedEventListener(element, event, handler, delay = 300) {
        let timeout;
        const debouncedHandler = (e) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => handler(e), delay);
        };
        this.addEventListener(element, event, debouncedHandler);
        return () => clearTimeout(timeout);
    },
    
    // Add loading state to button
    setButtonLoading(button, isLoading, loadingText = 'Loading...') {
        if (typeof button === 'string') button = this.getElement(button);
        if (!button) return;
        
        if (isLoading) {
            button.setAttribute('data-original-text', button.textContent);
            button.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ${loadingText}`;
            button.disabled = true;
        } else {
            const originalText = button.getAttribute('data-original-text');
            if (originalText) {
                button.textContent = originalText;
                button.removeAttribute('data-original-text');
            }
            button.disabled = false;
        }
    },
    
    // Scroll to element smoothly
    scrollToElement(element, offset = 0) {
        if (typeof element === 'string') element = this.getElement(element);
        if (!element) return;
        
        const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
        window.scrollTo({
            top: elementPosition - offset,
            behavior: 'smooth'
        });
    },
    
    // Check if element is in viewport
    isInViewport(element) {
        if (typeof element === 'string') element = this.getElement(element);
        if (!element) return false;
        
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
};

// ========== STRING UTILITIES ==========

const StringUtils = {
    // Capitalize first letter
    capitalize(str) {
        if (!str) return '';
        return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
    },
    
    // Capitalize each word
    capitalizeWords(str) {
        if (!str) return '';
        return str.replace(/\w\S*/g, txt => 
            txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
        );
    },
    
    // Convert camelCase to Title Case
    camelToTitleCase(str) {
        if (!str) return '';
        return str
            .replace(/([A-Z])/g, ' $1')
            .replace(/^./, char => char.toUpperCase())
            .trim();
    },
    
    // Convert snake_case to Title Case
    snakeToTitleCase(str) {
        if (!str) return '';
        return str
            .split('_')
            .map(word => this.capitalize(word))
            .join(' ');
    },
    
    // Truncate text with ellipsis
    truncate(text, maxLength = 100, suffix = '...') {
        if (!text || text.length <= maxLength) return text;
        return text.substr(0, maxLength - suffix.length) + suffix;
    },
    
    // Generate random string
    randomString(length = 8) {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let result = '';
        for (let i = 0; i < length; i++) {
            result += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return result;
    },
    
    // Sanitize HTML
    sanitizeHTML(html) {
        const temp = document.createElement('div');
        temp.textContent = html;
        return temp.innerHTML;
    },
    
    // Format phone number (Indian format)
    formatPhone(phone) {
        if (!phone) return '';
        const cleaned = phone.replace(/\D/g, '');
        if (cleaned.length === 10) {
            return `+91 ${cleaned.substring(0, 5)} ${cleaned.substring(5)}`;
        }
        return phone;
    },
    
    // Format file size
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    // Generate case ID
    generateCaseId(prefix = 'CASE') {
        const timestamp = Date.now().toString(36);
        const random = Math.random().toString(36).substr(2, 5);
        return `${prefix}_${timestamp}_${random}`.toUpperCase();
    }
};

// ========== DATE AND TIME UTILITIES ==========

const DateUtils = {
    // Format date
    formatDate(date, format = 'dd/mm/yyyy') {
        if (!date) return '';
        
        const d = new Date(date);
        if (isNaN(d.getTime())) return '';
        
        const day = d.getDate().toString().padStart(2, '0');
        const month = (d.getMonth() + 1).toString().padStart(2, '0');
        const year = d.getFullYear();
        const hours = d.getHours().toString().padStart(2, '0');
        const minutes = d.getMinutes().toString().padStart(2, '0');
        const seconds = d.getSeconds().toString().padStart(2, '0');
        
        const formats = {
            'dd/mm/yyyy': `${day}/${month}/${year}`,
            'mm/dd/yyyy': `${month}/${day}/${year}`,
            'yyyy-mm-dd': `${year}-${month}-${day}`,
            'dd-mm-yyyy': `${day}-${month}-${year}`,
            'dd/mm/yyyy hh:mm': `${day}/${month}/${year} ${hours}:${minutes}`,
            'dd/mm/yyyy hh:mm:ss': `${day}/${month}/${year} ${hours}:${minutes}:${seconds}`,
            'hh:mm:ss': `${hours}:${minutes}:${seconds}`,
            'hh:mm': `${hours}:${minutes}`,
            'relative': this.getRelativeTime(date)
        };
        
        return formats[format] || formats['dd/mm/yyyy'];
    },
    
    // Get relative time (e.g., "2 hours ago")
    getRelativeTime(date) {
        if (!date) return '';
        
        const now = new Date();
        const diffMs = now - new Date(date);
        const diffSecs = Math.floor(diffMs / 1000);
        const diffMins = Math.floor(diffSecs / 60);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);
        const diffWeeks = Math.floor(diffDays / 7);
        const diffMonths = Math.floor(diffDays / 30);
        const diffYears = Math.floor(diffDays / 365);
        
        if (diffYears > 0) return `${diffYears} year${diffYears > 1 ? 's' : ''} ago`;
        if (diffMonths > 0) return `${diffMonths} month${diffMonths > 1 ? 's' : ''} ago`;
        if (diffWeeks > 0) return `${diffWeeks} week${diffWeeks > 1 ? 's' : ''} ago`;
        if (diffDays > 0) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
        if (diffHours > 0) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        if (diffMins > 0) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
        return 'Just now';
    },
    
    // Check if date is today
    isToday(date) {
        if (!date) return false;
        const today = new Date();
        const checkDate = new Date(date);
        return (
            checkDate.getDate() === today.getDate() &&
            checkDate.getMonth() === today.getMonth() &&
            checkDate.getFullYear() === today.getFullYear()
        );
    },
    
    // Check if date is in the past
    isPast(date) {
        if (!date) return false;
        return new Date(date) < new Date();
    },
    
    // Check if date is in the future
    isFuture(date) {
        if (!date) return false;
        return new Date(date) > new Date();
    },
    
    // Add days to date
    addDays(date, days) {
        const result = new Date(date);
        result.setDate(result.getDate() + days);
        return result;
    },
    
    // Get age from birth date
    getAge(birthDate) {
        if (!birthDate) return null;
        const today = new Date();
        const birth = new Date(birthDate);
        let age = today.getFullYear() - birth.getFullYear();
        const monthDiff = today.getMonth() - birth.getMonth();
        
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
            age--;
        }
        
        return age;
    },
    
    // Get time remaining until date
    getTimeRemaining(targetDate) {
        if (!targetDate) return null;
        
        const now = new Date().getTime();
        const target = new Date(targetDate).getTime();
        const difference = target - now;
        
        if (difference <= 0) return { expired: true };
        
        const days = Math.floor(difference / (1000 * 60 * 60 * 24));
        const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((difference % (1000 * 60)) / 1000);
        
        return {
            days,
            hours,
            minutes,
            seconds,
            total: difference,
            expired: false
        };
    }
};

// ========== VALIDATION UTILITIES ==========

const ValidationUtils = {
    // Validate email
    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },
    
    // Validate phone number (Indian format)
    validatePhone(phone) {
        const phoneRegex = /^[6-9]\d{9}$/;
        return phoneRegex.test(phone.replace(/\D/g, ''));
    },
    
    // Validate Aadhaar number
    validateAadhaar(aadhaar) {
        const aadhaarRegex = /^\d{12}$/;
        return aadhaarRegex.test(aadhaar.replace(/\s/g, ''));
    },
    
    // Validate password strength
    validatePassword(password) {
        const minLength = 8;
        const hasUpperCase = /[A-Z]/.test(password);
        const hasLowerCase = /[a-z]/.test(password);
        const hasNumbers = /\d/.test(password);
        const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
        
        return {
            isValid: password.length >= minLength && hasUpperCase && hasLowerCase && hasNumbers && hasSpecialChar,
            hasMinLength: password.length >= minLength,
            hasUpperCase,
            hasLowerCase,
            hasNumbers,
            hasSpecialChar
        };
    },
    
    // Validate PIN code
    validatePIN(pincode) {
        const pinRegex = /^\d{6}$/;
        return pinRegex.test(pincode);
    },
    
    // Validate required fields
    validateRequired(fields, data) {
        const errors = {};
        fields.forEach(field => {
            if (!data[field] || data[field].toString().trim() === '') {
                errors[field] = `${StringUtils.camelToTitleCase(field)} is required`;
            }
        });
        return {
            isValid: Object.keys(errors).length === 0,
            errors
        };
    },
    
    // Validate file
    validateFile(file, allowedTypes, maxSize) {
        const errors = [];
        
        if (!file) {
            errors.push('File is required');
            return { isValid: false, errors };
        }
        
        if (!allowedTypes.includes(file.type)) {
            errors.push(`File type ${file.type} is not allowed`);
        }
        
        if (file.size > maxSize) {
            errors.push(`File size must be less than ${StringUtils.formatFileSize(maxSize)}`);
        }
        
        return {
            isValid: errors.length === 0,
            errors
        };
    },
    
    // Validate location coordinates
    validateCoordinates(lat, lng) {
        const latValid = lat >= -90 && lat <= 90;
        const lngValid = lng >= -180 && lng <= 180;
        return latValid && lngValid;
    }
};

// ========== STORAGE UTILITIES ==========

const StorageUtils = {
    // Safe localStorage get
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Error reading from localStorage:', error);
            return defaultValue;
        }
    },
    
    // Safe localStorage set
    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error('Error writing to localStorage:', error);
            return false;
        }
    },
    
    // Safe localStorage remove
    remove(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Error removing from localStorage:', error);
            return false;
        }
    },
    
    // Clear all app data
    clearAppData() {
        try {
            Object.values(window.STORAGE_KEYS || {}).forEach(key => {
                localStorage.removeItem(key);
            });
            return true;
        } catch (error) {
            console.error('Error clearing app data:', error);
            return false;
        }
    },
    
    // Check if storage is available
    isAvailable() {
        try {
            const test = 'test';
            localStorage.setItem(test, test);
            localStorage.removeItem(test);
            return true;
        } catch (error) {
            return false;
        }
    },
    
    // Get storage usage info
    getStorageInfo() {
        let totalSize = 0;
        for (let key in localStorage) {
            if (localStorage.hasOwnProperty(key)) {
                totalSize += localStorage[key].length;
            }
        }
        return {
            totalSize: totalSize,
            formattedSize: StringUtils.formatFileSize(totalSize),
            itemCount: localStorage.length
        };
    }
};

// ========== NOTIFICATION AND ALERT UTILITIES ==========

const NotificationUtils = {
    // Show toast notification
    showToast(message, type = 'info', duration = 5000) {
        // Remove existing toasts
        const existingToasts = document.querySelectorAll('.custom-toast');
        existingToasts.forEach(toast => toast.remove());
        
        const toast = DOMUtils.createElement('div', {
            className: `custom-toast toast toast-${type}`,
            style: `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                min-width: 300px;
                background: white;
                border-left: 4px solid ${this.getToastColor(type)};
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                border-radius: 4px;
                padding: 12px 16px;
                animation: slideInRight 0.3s ease-out;
            `
        }, [message]);
        
        document.body.appendChild(toast);
        
        // Auto remove after duration
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.animation = 'slideOutRight 0.3s ease-in';
                setTimeout(() => toast.remove(), 300);
            }
        }, duration);
        
        return toast;
    },
    
    // Get toast color based on type
    getToastColor(type) {
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
        return colors[type] || colors.info;
    },
    
    // Show confirmation dialog
    async showConfirm(message, title = 'Confirm Action') {
        return new Promise((resolve) => {
            const modal = DOMUtils.createElement('div', {
                className: 'confirm-modal',
                style: `
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.5);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 10000;
                `
            });
            
            const content = DOMUtils.createElement('div', {
                className: 'confirm-content',
                style: `
                    background: white;
                    padding: 24px;
                    border-radius: 8px;
                    max-width: 400px;
                    width: 90%;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                `
            }, [
                DOMUtils.createElement('h3', { style: 'margin: 0 0 16px 0; color: #333;' }, [title]),
                DOMUtils.createElement('p', { style: 'margin: 0 0 24px 0; color: #666; line-height: 1.5;' }, [message]),
                DOMUtils.createElement('div', {
                    style: 'display: flex; gap: 12px; justify-content: flex-end;'
                }, [
                    DOMUtils.createElement('button', {
                        className: 'btn btn-outline-secondary',
                        onclick: () => {
                            document.body.removeChild(modal);
                            resolve(false);
                        }
                    }, ['Cancel']),
                    DOMUtils.createElement('button', {
                        className: 'btn btn-primary',
                        onclick: () => {
                            document.body.removeChild(modal);
                            resolve(true);
                        }
                    }, ['Confirm'])
                ])
            ]);
            
            modal.appendChild(content);
            document.body.appendChild(modal);
        });
    },
    
    // Show loading overlay
    showLoading(message = 'Loading...') {
        const overlay = DOMUtils.createElement('div', {
            id: 'loading-overlay',
            style: `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(255,255,255,0.9);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                z-index: 9999;
            `
        }, [
            DOMUtils.createElement('div', {
                className: 'spinner-border text-primary',
                style: 'width: 3rem; height: 3rem; margin-bottom: 16px;'
            }),
            DOMUtils.createElement('p', { style: 'margin: 0; color: #666; font-size: 16px;' }, [message])
        ]);
        
        document.body.appendChild(overlay);
        return overlay;
    },
    
    // Hide loading overlay
    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
};

// ========== FORM UTILITIES ==========

const FormUtils = {
    // Serialize form data to object
    serializeForm(form) {
        if (typeof form === 'string') form = document.getElementById(form);
        if (!form) return {};
        
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            if (data[key]) {
                if (Array.isArray(data[key])) {
                    data[key].push(value);
                } else {
                    data[key] = [data[key], value];
                }
            } else {
                data[key] = value;
            }
        }
        
        return data;
    },
    
    // Populate form with data
    populateForm(form, data) {
        if (typeof form === 'string') form = document.getElementById(form);
        if (!form || !data) return;
        
        Object.keys(data).forEach(key => {
            const element = form.querySelector(`[name="${key}"]`);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = !!data[key];
                } else if (element.type === 'radio') {
                    const radio = form.querySelector(`[name="${key}"][value="${data[key]}"]`);
                    if (radio) radio.checked = true;
                } else {
                    element.value = data[key] || '';
                }
            }
        });
    },
    
    // Clear form
    clearForm(form) {
        if (typeof form === 'string') form = document.getElementById(form);
        if (!form) return;
        
        form.reset();
        
        // Clear any custom data attributes
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.classList.remove('is-invalid');
            const feedback = input.nextElementSibling;
            if (feedback && feedback.classList.contains('invalid-feedback')) {
                feedback.remove();
            }
        });
    },
    
    // Validate form and show errors
    validateForm(form, validationRules) {
        if (typeof form === 'string') form = document.getElementById(form);
        if (!form) return { isValid: false, errors: {} };
        
        const data = this.serializeForm(form);
        const errors = {};
        
        Object.keys(validationRules).forEach(field => {
            const rules = validationRules[field];
            const value = data[field];
            
            // Required validation
            if (rules.required && (!value || value.toString().trim() === '')) {
                errors[field] = rules.requiredMessage || `${StringUtils.camelToTitleCase(field)} is required`;
                return;
            }
            
            // Skip further validation if field is empty and not required
            if (!value || value.toString().trim() === '') return;
            
            // Email validation
            if (rules.email && !ValidationUtils.validateEmail(value)) {
                errors[field] = 'Please enter a valid email address';
                return;
            }
            
            // Phone validation
            if (rules.phone && !ValidationUtils.validatePhone(value)) {
                errors[field] = 'Please enter a valid phone number';
                return;
            }
            
            // Min length validation
            if (rules.minLength && value.length < rules.minLength) {
                errors[field] = `Must be at least ${rules.minLength} characters`;
                return;
            }
            
            // Max length validation
            if (rules.maxLength && value.length > rules.maxLength) {
                errors[field] = `Must be less than ${rules.maxLength} characters`;
                return;
            }
            
            // Custom validation
            if (rules.validate && typeof rules.validate === 'function') {
                const customError = rules.validate(value, data);
                if (customError) {
                    errors[field] = customError;
                }
            }
        });
        
        // Show errors in form
        this.showFormErrors(form, errors);
        
        return {
            isValid: Object.keys(errors).length === 0,
            errors,
            data
        };
    },
    
    // Show form errors
    showFormErrors(form, errors) {
        // Clear previous errors
        const existingErrors = form.querySelectorAll('.is-invalid, .invalid-feedback');
        existingErrors.forEach(element => {
            element.classList.remove('is-invalid');
            if (element.classList.contains('invalid-feedback')) {
                element.remove();
            }
        });
        
        // Show new errors
        Object.keys(errors).forEach(field => {
            const element = form.querySelector(`[name="${field}"]`);
            if (element) {
                element.classList.add('is-invalid');
                
                const feedback = DOMUtils.createElement('div', {
                    className: 'invalid-feedback',
                    style: 'display: block;'
                }, [errors[field]]);
                
                element.parentNode.appendChild(feedback);
            }
        });
    },
    
    // Disable form
    disableForm(form, disabled = true) {
        if (typeof form === 'string') form = document.getElementById(form);
        if (!form) return;
        
        const elements = form.querySelectorAll('input, select, textarea, button');
        elements.forEach(element => {
            element.disabled = disabled;
        });
    }
};

// ========== API RESPONSE HANDLING ==========

const APIUtils = {
    // Handle API response
    async handleResponse(response) {
        if (!response.ok) {
            let errorMessage = `HTTP error! status: ${response.status}`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.message || errorMessage;
            } catch {
                // Use default error message
            }
            throw new Error(errorMessage);
        }
        
        return response.json();
    },
    
    // Handle API error
    handleError(error, defaultMessage = 'An error occurred') {
        console.error('API Error:', error);
        
        if (error.message.includes('NetworkError') || error.message.includes('Failed to fetch')) {
            return 'Network error: Please check your internet connection';
        }
        
        if (error.message.includes('401')) {
            window.clearAuthData();
            window.location.href = 'login.html';
            return 'Session expired. Please login again.';
        }
        
        if (error.message.includes('403')) {
            return 'Access denied. You do not have permission to perform this action.';
        }
        
        return error.message || defaultMessage;
    },
    
    // Retry API call with exponential backoff
    async retryApiCall(apiCall, maxRetries = 3, delay = 1000) {
        let lastError;
        
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                return await apiCall();
            } catch (error) {
                lastError = error;
                
                // Don't retry on 4xx errors (except 429 - too many requests)
                if (error.message.includes('40') && !error.message.includes('429')) {
                    break;
                }
                
                if (attempt < maxRetries) {
                    const waitTime = delay * Math.pow(2, attempt - 1);
                    console.log(`Retry attempt ${attempt} after ${waitTime}ms`);
                    await new Promise(resolve => setTimeout(resolve, waitTime));
                }
            }
        }
        
        throw lastError;
    }
};

// ========== CRIME REPORTING UTILITIES ==========

const CrimeReportUtils = {
    // Get crime type display name
    getCrimeTypeDisplay(crimeType) {
        const crimeTypes = window.APP_CONSTANTS?.CRIME_TYPES || {};
        const displayNames = {
            theft: 'Theft',
            burglary: 'Burglary',
            robbery: 'Robbery',
            assault: 'Assault',
            harassment: 'Harassment',
            fraud: 'Fraud',
            cyber_crime: 'Cyber Crime',
            missing_person: 'Missing Person',
            vandalism: 'Vandalism',
            drug_offense: 'Drug Offense',
            traffic_violation: 'Traffic Violation',
            domestic_violence: 'Domestic Violence',
            other: 'Other'
        };
        
        return displayNames[crimeType] || StringUtils.camelToTitleCase(crimeType);
    },
    
    // Get priority display and color
    getPriorityInfo(priority) {
        const priorities = {
            low: { display: 'Low', color: '#28a745', class: 'badge bg-success' },
            medium: { display: 'Medium', color: '#ffc107', class: 'badge bg-warning' },
            high: { display: 'High', color: '#fd7e14', class: 'badge bg-orange' },
            critical: { display: 'Critical', color: '#dc3545', class: 'badge bg-danger' }
        };
        
        return priorities[priority] || priorities.medium;
    },
    
    // Get status display and color
    getStatusInfo(status) {
        const statuses = {
            pending: { display: 'Pending', color: '#6c757d', class: 'badge bg-secondary' },
            assigned: { display: 'Assigned', color: '#17a2b8', class: 'badge bg-info' },
            in_progress: { display: 'In Progress', color: '#007bff', class: 'badge bg-primary' },
            resolved: { display: 'Resolved', color: '#28a745', class: 'badge bg-success' },
            closed: { display: 'Closed', color: '#6c757d', class: 'badge bg-dark' }
        };
        
        return statuses[status] || statuses.pending;
    },
    
    // Calculate response time in hours
    calculateResponseTime(createdAt, assignedAt) {
        if (!createdAt || !assignedAt) return null;
        
        const created = new Date(createdAt);
        const assigned = new Date(assignedAt);
        const diffHours = (assigned - created) / (1000 * 60 * 60);
        
        return Math.round(diffHours * 100) / 100; // Round to 2 decimal places
    },
    
    // Validate crime report data
    validateCrimeReport(data) {
        const errors = {};
        
        if (!data.title || data.title.trim() === '') {
            errors.title = 'Title is required';
        }
        
        if (!data.description || data.description.trim() === '') {
            errors.description = 'Description is required';
        }
        
        if (!data.crime_type) {
            errors.crime_type = 'Crime type is required';
        }
        
        if (!data.location || data.location.trim() === '') {
            errors.location = 'Location is required';
        }
        
        if (data.latitude && data.longitude) {
            if (!ValidationUtils.validateCoordinates(data.latitude, data.longitude)) {
                errors.location = 'Invalid coordinates';
            }
        }
        
        return {
            isValid: Object.keys(errors).length === 0,
            errors
        };
    },
    
    // Generate case summary
    generateCaseSummary(caseData) {
        const priority = this.getPriorityInfo(caseData.priority);
        const status = this.getStatusInfo(caseData.status);
        const crimeType = this.getCrimeTypeDisplay(caseData.crime_type);
        
        return {
            id: caseData.id,
            title: caseData.title,
            crimeType,
            priority: priority.display,
            priorityClass: priority.class,
            status: status.display,
            statusClass: status.class,
            location: caseData.location,
            createdAt: DateUtils.formatDate(caseData.created_at, 'dd/mm/yyyy hh:mm'),
            relativeTime: DateUtils.getRelativeTime(caseData.created_at),
            assignedOfficer: caseData.assigned_officer,
            responseTime: caseData.assigned_at ? 
                this.calculateResponseTime(caseData.created_at, caseData.assigned_at) : null
        };
    }
};

// ========== EXPORT UTILITIES ==========

const ExportUtils = {
    // Export data to CSV
    exportToCSV(data, filename = 'export.csv') {
        if (!data || data.length === 0) {
            NotificationUtils.showToast('No data to export', 'warning');
            return;
        }
        
        const headers = Object.keys(data[0]);
        const csvContent = [
            headers.join(','),
            ...data.map(row => 
                headers.map(header => 
                    `"${String(row[header] || '').replace(/"/g, '""')}"`
                ).join(',')
            )
        ].join('\n');
        
        this.downloadFile(csvContent, filename, 'text/csv');
    },
    
    // Export data to JSON
    exportToJSON(data, filename = 'export.json') {
        const jsonContent = JSON.stringify(data, null, 2);
        this.downloadFile(jsonContent, filename, 'application/json');
    },
    
    // Download file
    downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    },
    
    // Print element
    printElement(elementId) {
        const element = document.getElementById(elementId);
        if (!element) {
            NotificationUtils.showToast('Element not found', 'error');
            return;
        }
        
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>Print</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; }
                        @media print { 
                            .no-print { display: none !important; }
                            .page-break { page-break-after: always; }
                        }
                    </style>
                </head>
                <body>
                    ${element.innerHTML}
                </body>
            </html>
        `);
        
        printWindow.document.close();
        printWindow.focus();
        printWindow.print();
        printWindow.close();
    }
};

// ========== MAIN UTILS OBJECT ==========

const APP_UTILS = {
    DOM: DOMUtils,
    String: StringUtils,
    Date: DateUtils,
    Validation: ValidationUtils,
    Storage: StorageUtils,
    Notification: NotificationUtils,
    Form: FormUtils,
    API: APIUtils,
    CrimeReport: CrimeReportUtils,
    Export: ExportUtils,
    
    // Common utility functions
    debounce(func, wait, immediate) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    },
    
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    deepClone(obj) {
        if (obj === null || typeof obj !== 'object') return obj;
        if (obj instanceof Date) return new Date(obj.getTime());
        if (obj instanceof Array) return obj.map(item => this.deepClone(item));
        if (obj instanceof Object) {
            const clonedObj = {};
            Object.keys(obj).forEach(key => {
                clonedObj[key] = this.deepClone(obj[key]);
            });
            return clonedObj;
        }
    },
    
    isEmpty(value) {
        if (value === null || value === undefined) return true;
        if (typeof value === 'string') return value.trim() === '';
        if (Array.isArray(value)) return value.length === 0;
        if (typeof value === 'object') return Object.keys(value).length === 0;
        return false;
    },
    
    // Generate unique ID
    generateId(prefix = 'id') {
        return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    },
    
    // Check if running on mobile
    isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    },
    
    // Check if running on touch device
    isTouchDevice() {
        return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    },
    
    // Get browser information
    getBrowserInfo() {
        const ua = navigator.userAgent;
        let browser = 'Unknown';
        
        if (ua.includes('Chrome')) browser = 'Chrome';
        else if (ua.includes('Firefox')) browser = 'Firefox';
        else if (ua.includes('Safari')) browser = 'Safari';
        else if (ua.includes('Edge')) browser = 'Edge';
        
        return {
            browser,
            isMobile: this.isMobile(),
            isTouch: this.isTouchDevice(),
            userAgent: ua
        };
    }
};

// ========== MAKE GLOBALLY AVAILABLE ==========

window.APP_UTILS = APP_UTILS;

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .badge.bg-orange {
        background-color: #fd7e14 !important;
    }
`;
document.head.appendChild(style);

console.log('✅ iReport Utilities v' + (window.APP_CONFIG?.APP_VERSION || '2.0.0') + ' loaded successfully');

} // End of if condition