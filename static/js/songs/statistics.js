// static/js/songs/statistics.js

$(document).ready(function() {
    async function loadStatistics() {
        try {
            const stats = await SongsAPI.getStatistics();
            
            animateNumber('#stat-total', stats.total || 0);
            animateNumber('#stat-live', stats.live || 0);
            animateNumber('#stat-review', stats.review || 0);
            animateNumber('#stat-approved', stats.approved || 0);
        } catch(e) {
            console.error('Failed to load statistics:', e);
        }
    }
    
    function animateNumber(selector, target) {
        const $el = $(selector);
        const current = parseInt($el.text()) || 0;
        if (current === target) return;
        
        const duration = 500;
        const start = performance.now();
        const startVal = current;
        
        function update(now) {
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            const value = Math.round(startVal + (target - startVal) * eased);
            $el.text(value);
            if (progress < 1) requestAnimationFrame(update);
        }
        requestAnimationFrame(update);
    }
    
    loadStatistics();
    setInterval(loadStatistics, 60000);
});