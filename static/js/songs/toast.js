// static/js/songs/toast.js

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    if (!toast) {
        const prefix = type === 'error' ? '❌ ' : type === 'warning' ? '⚠️ ' : '✅ ';
        alert(prefix + message);
        return;
    }
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    clearTimeout(toast.timer);
    toast.timer = setTimeout(() => toast.classList.remove('show'), 3000);
}

window.showToast = showToast;