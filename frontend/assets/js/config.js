// Secure API call
async function getPoliceCases() {
    try {
        const response = await secureApiCall('/api/police/cases');
        return await response.json();
    } catch (error) {
        console.error('Access denied:', error.message);
    }
}

// Check if user can access feature
if (canUpdateCaseStatus()) {
    // Show case status update controls
}

// Get all endpoints user can access
const myEndpoints = getAccessibleEndpoints();