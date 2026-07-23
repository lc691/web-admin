/**
 * Error Handling Utilities
 * 
 * Global error handling for the application
 */

// =====================================================
// GLOBAL ERROR HANDLER
// =====================================================

window.addEventListener('error', function(event) {
    console.error('Global error:', event.error || event.message);
    
    // Log to server if needed
    if (window.logError) {
        window.logError({
            message: event.message || 'Unknown error',
            filename: event.filename || 'unknown',
            lineno: event.lineno || 0,
            colno: event.colno || 0,
            stack: event.error?.stack || 'No stack trace'
        });
    }
    
    // Show user-friendly error message
    if (event.error && !event.error.handled) {
        showToast('Terjadi kesalahan: ' + (event.error.message || 'Unknown error'), 'error');
    }
    
    return false;
});

// =====================================================
// API ERROR HANDLER
// =====================================================

function handleApiError(error, fallbackMessage = 'Terjadi kesalahan pada server') {
    console.error('API Error:', error);
    
    let message = fallbackMessage;
    
    if (error.response) {
        // The request was made and the server responded with a status code
        const status = error.response.status;
        const data = error.response.data;
        
        if (data && data.detail) {
            message = data.detail;
        } else if (data && data.error) {
            message = data.error;
        } else if (data && data.message) {
            message = data.message;
        }
        
        switch (status) {
            case 400:
                message = 'Data tidak valid: ' + message;
                break;
            case 401:
                message = 'Sesi telah berakhir. Silakan login kembali.';
                window.location.href = '/login';
                break;
            case 403:
                message = 'Anda tidak memiliki izin untuk melakukan tindakan ini.';
                break;
            case 404:
                message = 'Resource tidak ditemukan.';
                break;
            case 409:
                message = 'Konflik data: ' + message;
                break;
            case 429:
                message = 'Terlalu banyak permintaan. Silakan tunggu beberapa saat.';
                break;
            case 500:
                message = 'Kesalahan server internal. Tim kami telah diberitahu.';
                break;
            default:
                message = message || fallbackMessage;
        }
    } else if (error.request) {
        // The request was made but no response was received
        message = 'Tidak ada respons dari server. Periksa koneksi internet Anda.';
    } else {
        // Something happened in setting up the request
        message = error.message || fallbackMessage;
    }
    
    showToast(message, 'error');
    return message;
}

// =====================================================
// NETWORK ERROR HANDLER
// =====================================================

function handleNetworkError(error) {
    console.warn('Network error:', error);
    
    if (!navigator.onLine) {
        showToast('Tidak ada koneksi internet. Periksa koneksi Anda.', 'warning');
        return 'Tidak ada koneksi internet';
    }
    
    return handleApiError(error, 'Gagal terhubung ke server');
}

// =====================================================
// FORM ERROR HANDLER
// =====================================================

function handleFormErrors(errors, formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    // Clear previous errors
    form.querySelectorAll('.is-invalid').forEach(el => {
        el.classList.remove('is-invalid');
    });
    form.querySelectorAll('.invalid-feedback').forEach(el => {
        el.remove();
    });
    
    // Show new errors
    if (typeof errors === 'object') {
        Object.entries(errors).forEach(([field, messages]) => {
            const input = form.querySelector(`[name="${field}"]`);
            if (input) {
                input.classList.add('is-invalid');
                
                const feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                feedback.textContent = Array.isArray(messages) ? messages.join(', ') : messages;
                input.parentNode.appendChild(feedback);
            }
        });
    }
}

// =====================================================
// TOAST CONFIGURATION
// =====================================================

// Toast container is created in utils.html
function showToast(message, type = 'success') {
    const colors = {
        success: 'bg-success text-white',
        error: 'bg-danger text-white',
        warning: 'bg-warning text-dark',
        info: 'bg-info text-white'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center ${colors[type] || colors.info} border-0`;
    toast.role = 'alert';
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    const container = document.getElementById('toast-container') || createToastContainer();
    container.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, { delay: 5000 });
    bsToast.show();
    
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 5500);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '1050';
    document.body.appendChild(container);
    return container;
}

// =====================================================
// ERROR LOGGING
// =====================================================

function logError(errorData) {
    // Send error to server for logging
    try {
        fetch('/api/logs/error', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ...errorData,
                url: window.location.href,
                userAgent: navigator.userAgent,
                timestamp: new Date().toISOString()
            })
        }).catch(() => {
            // Silently fail - don't create infinite loop
        });
    } catch (e) {
        // Silently fail
    }
}

// =====================================================
// EXPORT
// =====================================================

window.errorHandlers = {
    handleApiError,
    handleNetworkError,
    handleFormErrors,
    showToast,
    logError
};