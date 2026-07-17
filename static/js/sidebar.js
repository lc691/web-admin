// =====================================================
// SIDEBAR NEPAL - Adapted for DramaStream
// =====================================================

document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    // =====================================================
    // DOM Elements
    // =====================================================
    const sidebar = document.getElementById('mainSidebar');
    const sidebarToggleBtns = document.querySelectorAll('.sidebar-toggle');
    const searchForm = document.querySelector('.search-form');
    const themeToggleBtn = document.getElementById('themeToggle');
    const menuLinks = document.querySelectorAll('.menu-link');

    // =====================================================
    // Theme Management
    // =====================================================
    
    /**
     * Update theme icon based on current theme and sidebar state
     */
    function updateThemeIcon() {
        if (!themeToggleBtn) return;
        const themeIcon = themeToggleBtn.querySelector('.theme-icon');
        if (!themeIcon) return;
        
        const isDark = document.body.classList.contains('dark-theme');
        const isCollapsed = sidebar.classList.contains('collapsed');
        
        // Logic: If sidebar is collapsed, show sun/moon accordingly
        if (isCollapsed) {
            themeIcon.textContent = isDark ? 'light_mode' : 'dark_mode';
        } else {
            themeIcon.textContent = 'dark_mode';
        }
    }

    /**
     * Apply dark theme based on saved preference or system preference
     */
    function initTheme() {
        const savedTheme = localStorage.getItem('theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const shouldUseDarkTheme = savedTheme === 'dark' || (!savedTheme && systemPrefersDark);
        
        document.body.classList.toggle('dark-theme', shouldUseDarkTheme);
        updateThemeIcon();
    }

    /**
     * Toggle theme on button click
     */
    function toggleTheme() {
        const isDark = document.body.classList.toggle('dark-theme');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        updateThemeIcon();
    }

    // =====================================================
    // Sidebar Toggle
    // =====================================================
    
    /**
     * Toggle sidebar collapsed state
     */
    function toggleSidebar() {
        sidebar.classList.toggle('collapsed');
        updateThemeIcon();
        
        // Handle mobile overlay
        if (window.innerWidth <= 768) {
            document.body.classList.toggle('sidebar-open', !sidebar.classList.contains('collapsed'));
        }
    }

    /**
     * Expand sidebar when search form is clicked (if collapsed)
     */
    function handleSearchClick() {
        if (sidebar.classList.contains('collapsed')) {
            sidebar.classList.remove('collapsed');
            updateThemeIcon();
            
            // Focus on search input
            const searchInput = searchForm?.querySelector('input');
            if (searchInput) {
                setTimeout(() => searchInput.focus(), 100);
            }
        }
    }

    // =====================================================
    // DROPDOWN TOGGLE - FIXED!
    // =====================================================
    
    const dropdownToggles = document.querySelectorAll('.menu-dropdown-toggle');
    
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Get target submenu
            const targetId = this.getAttribute('data-target');
            if (!targetId) {
                console.warn('Dropdown toggle missing data-target attribute');
                return;
            }
            
            const subMenu = document.querySelector(targetId);
            if (!subMenu) {
                console.warn('Submenu not found:', targetId);
                return;
            }
            
            // Toggle current submenu
            const isOpen = subMenu.classList.contains('open');
            
            // Close all other submenus (optional)
            document.querySelectorAll('.sub-menu.open').forEach(otherMenu => {
                if (otherMenu.id !== targetId.replace('#', '')) {
                    otherMenu.classList.remove('open');
                    const otherToggle = document.querySelector(`[data-target="#${otherMenu.id}"]`);
                    if (otherToggle) {
                        otherToggle.classList.remove('active');
                        // Force icon rotation reset
                        const icon = otherToggle.querySelector('.menu-dropdown-icon');
                        if (icon) {
                            icon.style.transform = 'rotate(0deg)';
                        }
                    }
                }
            });
            
            // Toggle current
            if (isOpen) {
                subMenu.classList.remove('open');
                this.classList.remove('active');
                // Reset icon rotation
                const icon = this.querySelector('.menu-dropdown-icon');
                if (icon) {
                    icon.style.transform = 'rotate(0deg)';
                }
            } else {
                subMenu.classList.add('open');
                this.classList.add('active');
                // Rotate icon 180deg
                const icon = this.querySelector('.menu-dropdown-icon');
                if (icon) {
                    icon.style.transform = 'rotate(180deg)';
                }
            }
            
            // Debug
            console.log('Dropdown toggled:', targetId, 'Open:', !isOpen);
        });
    });

    // =====================================================
    // CLOSE DROPDOWN ON SIDEBAR COLLAPSE
    // =====================================================
    
    // Intercept sidebar toggle to close dropdowns
    sidebarToggleBtns.forEach((btn) => {
        btn.addEventListener('click', function() {
            // Wait for sidebar animation
            setTimeout(() => {
                if (sidebar.classList.contains('collapsed')) {
                    // Close all submenus
                    document.querySelectorAll('.sub-menu.open').forEach(menu => {
                        menu.classList.remove('open');
                    });
                    document.querySelectorAll('.menu-dropdown-toggle.active').forEach(toggle => {
                        toggle.classList.remove('active');
                        // Reset icon
                        const icon = toggle.querySelector('.menu-dropdown-icon');
                        if (icon) {
                            icon.style.transform = 'rotate(0deg)';
                        }
                    });
                }
            }, 100);
        });
    });

    // =====================================================
    // CLOSE DROPDOWN ON CLICK OUTSIDE
    // =====================================================
    
    document.addEventListener('click', function(e) {
        // Jika klik di luar sidebar, close dropdowns
        if (!e.target.closest('.sidebar')) {
            document.querySelectorAll('.sub-menu.open').forEach(menu => {
                menu.classList.remove('open');
            });
            document.querySelectorAll('.menu-dropdown-toggle.active').forEach(toggle => {
                toggle.classList.remove('active');
                const icon = toggle.querySelector('.menu-dropdown-icon');
                if (icon) {
                    icon.style.transform = 'rotate(0deg)';
                }
            });
        }
    });

    // =====================================================
    // SIDEBAR TOGGLE FUNCTION (override)
    // =====================================================
    
    // Simpan fungsi toggle asli
    const originalToggleSidebar = window.toggleSidebar || function() {};
    
    // Override dengan fungsi baru
    window.toggleSidebar = function() {
        sidebar.classList.toggle('collapsed');
        updateThemeIcon();
        
        // Handle mobile overlay
        if (window.innerWidth <= 768) {
            document.body.classList.toggle('sidebar-open', !sidebar.classList.contains('collapsed'));
        }
        
        // Close dropdowns jika collapsed
        if (sidebar.classList.contains('collapsed')) {
            document.querySelectorAll('.sub-menu.open').forEach(menu => {
                menu.classList.remove('open');
            });
            document.querySelectorAll('.menu-dropdown-toggle.active').forEach(toggle => {
                toggle.classList.remove('active');
                const icon = toggle.querySelector('.menu-dropdown-icon');
                if (icon) {
                    icon.style.transform = 'rotate(0deg)';
                }
            });
        }
    };


    // =====================================================
    // Event Listeners
    // =====================================================
    
    // Toggle buttons
    sidebarToggleBtns.forEach((btn) => {
        btn.addEventListener('click', toggleSidebar);
    });

    // Theme toggle
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleTheme);
    }

    // Search form click
    if (searchForm) {
        searchForm.addEventListener('click', handleSearchClick);
    }

    // =====================================================
    // Initialize
    // =====================================================
    
    // Apply theme
    initTheme();

    // Expand sidebar by default on large screens
    if (window.innerWidth > 768) {
        sidebar.classList.remove('collapsed');
    }

    // Close sidebar on mobile when clicking overlay
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            const isClickInsideSidebar = sidebar.contains(e.target);
            const isClickOnToggle = e.target.closest('.sidebar-toggle');
            const isClickOnNavToggle = e.target.closest('.site-nav .sidebar-toggle');
            
            if (!isClickInsideSidebar && !isClickOnToggle && !isClickOnNavToggle) {
                if (!sidebar.classList.contains('collapsed')) {
                    sidebar.classList.add('collapsed');
                    document.body.classList.remove('sidebar-open');
                    updateThemeIcon();
                }
            }
        }
    });

    // Handle resize
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            if (window.innerWidth > 768) {
                sidebar.classList.remove('collapsed');
                document.body.classList.remove('sidebar-open');
                updateThemeIcon();
            }
        }, 250);
    });

    // =====================================================
    // Set active menu link based on current URL
    // =====================================================
    function setActiveMenu() {
        const currentUrl = window.location.pathname;
        menuLinks.forEach(link => {
            link.classList.remove('active');
            const href = link.getAttribute('href');
            if (href && currentUrl.includes(href)) {
                link.classList.add('active');
            }
        });
    }
    setActiveMenu();

    console.log('✅ Sidebar Nepal initialized successfully!');
});