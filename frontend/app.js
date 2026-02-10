/**
 * CyberGuardX Frontend Application
 * Professional-grade security assessment platform
 * Features: Email breach detection, URL phishing, Password analysis, Website security scanning
 * 
 * Modern modular architecture with feature-based organization
 */

import { initPasswordAnalyzer } from './features/passwordAnalyzer.js';
import { initEmailChecker } from './features/emailChecker.js';
import { initURLChecker } from './features/urlChecker.js';
import { initWebsiteScanner } from './features/websiteScanner.js';
import { initHistoryLoader } from './features/historyLoader.js';

const API_BASE_URL = 'http://localhost:8000';

// Gather all DOM element references
const elements = {
    emailInput: document.getElementById('emailInput'),
    urlInput: document.getElementById('urlInput'),
    websiteInput: document.getElementById('websiteInput'),
    passwordInput: document.getElementById('passwordInput'),
    checkEmailBtn: document.getElementById('checkEmailBtn'),
    checkUrlBtn: document.getElementById('checkUrlBtn'),
    scanWebsiteBtn: document.getElementById('scanWebsiteBtn'),
    checkPasswordBtn: document.getElementById('checkPasswordBtn'),
    generatePasswordBtn: document.getElementById('generatePasswordBtn'),
    generatePassphraseBtn: document.getElementById('generatePassphraseBtn'),
    showPasswordCheckbox: document.getElementById('showPassword'),
    loadHistoryBtn: document.getElementById('loadHistoryBtn'),
    emailResult: document.getElementById('emailResult'),
    urlResult: document.getElementById('urlResult'),
    websiteResult: document.getElementById('websiteResult'),
    passwordResult: document.getElementById('passwordResult'),
    historyResult: document.getElementById('historyResult'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    confirmPermission: document.getElementById('confirmPermission'),
    confirmOwner: document.getElementById('confirmOwner'),
    confirmLegal: document.getElementById('confirmLegal'),
};

// UI helper functions
const uiHelpers = {
    showLoading: () => elements.loadingOverlay.classList.add('show'),
    hideLoading: () => elements.loadingOverlay.classList.remove('show'),
};

// Initialize all features
initPasswordAnalyzer(elements, uiHelpers);
initEmailChecker(elements, uiHelpers);
initURLChecker(elements, uiHelpers);
initWebsiteScanner(elements, uiHelpers);
initHistoryLoader(elements, uiHelpers);

console.log('CyberGuardX Frontend Loaded (Modular v3.0)');
console.log('Backend API:', API_BASE_URL);
console.log('Features: Password Analyzer, Email Checker, URL Checker, Website Scanner, History Loader');
