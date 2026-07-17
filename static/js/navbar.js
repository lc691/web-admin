// ================================================================
// NAVBAR - FINAL SCRIPTS
// ================================================================

document.addEventListener('DOMContentLoaded', function() {
    
    // ==========================================================
    // 1. SIDEBAR TOGGLE (Desktop)
    // ==========================================================
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.navbar-vertical');
    
    sidebarToggle?.addEventListener('click', function() {
        sidebar?.classList.toggle('collapsed');
        
        // Simpan status ke localStorage
        const isCollapsed = sidebar?.classList.contains('collapsed');
        localStorage.setItem('sidebar-collapsed', isCollapsed);
    });
    
    // ==========================================================
    // 2. DARK MODE TOGGLE
    // ==========================================================
    const darkModeToggle = document.getElementById('darkModeToggle');
    const darkIcon = darkModeToggle?.querySelector('i');
    
    // Cek status dari localStorage
    const isDark = localStorage.getItem('dark-mode') === 'true';
    
    if (isDark) {
        document.documentElement.setAttribute('data-bs-theme', 'dark');
        darkIcon?.classList.replace('fa-moon', 'fa-sun');
    }
    
    darkModeToggle?.addEventListener('click', function() {
        const isCurrentlyDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
        const newTheme = isCurrentlyDark ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('dark-mode', newTheme === 'dark');
        
        // Toggle icon
        if (isCurrentlyDark) {
            darkIcon?.classList.replace('fa-sun', 'fa-moon');
        } else {
            darkIcon?.classList.replace('fa-moon', 'fa-sun');
        }
    });
    
    // ==========================================================
    // 3. MOBILE SIDEBAR TOGGLE
    // ==========================================================
    const mobileToggle = document.querySelector('.navbar-toggler');
    
    mobileToggle?.addEventListener('click', function(e) {
        e.stopPropagation();
        // Bootstrap akan handle collapse secara otomatis
    });
    
    // ==========================================================
    // 4. TUTUP SIDEBAR SAAT KLIK DI LUAR (Mobile)
    // ==========================================================
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            const sidebar = document.querySelector('.navbar-vertical');
            const isClickInside = sidebar?.contains(e.target);
            const isClickOnToggle = document.querySelector('.navbar-toggler')?.contains(e.target);
            
            if (!isClickInside && !isClickOnToggle) {
                sidebar?.classList.remove('show');
            }
        }
    });
    
    // ==========================================================
    // 5. SEARCH - Enter to Submit
    // ==========================================================
    const searchInput = document.querySelector('.navbar input[type="search"]');
    searchInput?.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            this.closest('form')?.submit();
        }
    });
    
    // ==========================================================
    // 6. SCROLL EFFECT - Add shadow saat scroll
    // ==========================================================
    let lastScroll = 0;
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        const currentScroll = window.pageYOffset || document.documentElement.scrollTop;
        
        if (currentScroll > 10) {
            navbar?.classList.add('shadow-sm');
            navbar?.classList.remove('shadow-none');
        } else {
            navbar?.classList.remove('shadow-sm');
            navbar?.classList.add('shadow-none');
        }
        
        lastScroll = currentScroll;
    });
    
});