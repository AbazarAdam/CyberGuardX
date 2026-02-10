/**
 * API Module
 * Handles all HTTP requests to CyberGuardX backend
 */

const API_BASE_URL = 'http://localhost:8000';

export const api = {
    /**
     * Check email for breaches
     */
    async checkEmail(email) {
        const response = await fetch(`${API_BASE_URL}/check-email`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email }),
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        return response.json();
    },

    /**
     * Check URL for phishing
     */
    async checkUrl(url) {
        const response = await fetch(`${API_BASE_URL}/check-url`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url }),
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        return response.json();
    },

    /**
     * Analyze password strength
     */
    async checkPassword(password) {
        const response = await fetch(`${API_BASE_URL}/check-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password }),
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        return response.json();
    },

    /**
     * Generate secure password or passphrase
     */
    async generatePassword(length = 20, mode = 'password') {
        const response = await fetch(`${API_BASE_URL}/generate-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ length, mode }),
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        return response.json();
    },

    /**
     * Scan website for security issues
     */
    async scanWebsite(url, confirmed_permission, owner_confirmation, legal_responsibility) {
        const response = await fetch(`${API_BASE_URL}/scan-website`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url,
                confirmed_permission,
                owner_confirmation,
                legal_responsibility
            }),
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || `Server error: ${response.status}`);
        }
        
        return response.json();
    },

    /**
     * Load scan history
     */
    async loadHistory(limit = 10) {
        const response = await fetch(`${API_BASE_URL}/scan-history?limit=${limit}`);
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        return response.json();
    }
};
