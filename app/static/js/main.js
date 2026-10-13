document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. MULTI-THEME SWITCHER (Light, Dark, iPhone Light, iPhone Midnight, Titanium, Rose) ---
    const themeDropdownBtn = document.getElementById('theme-dropdown-btn');
    const themeMenu = document.getElementById('theme-menu');
    const themeOptions = document.querySelectorAll('.theme-option');
    const themeLabel = document.getElementById('current-theme-label');
    const themeIcon = document.getElementById('current-theme-icon');
    const body = document.body;
    
    // Default to 'theme-iphone-dark' or saved preference
    const savedTheme = localStorage.getItem('saree-factory-theme') || 'theme-iphone-dark';
    applyTheme(savedTheme);
    
    // Toggle dropdown visibility
    if (themeDropdownBtn && themeMenu) {
        themeDropdownBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            themeMenu.classList.toggle('show');
        });
        
        document.addEventListener('click', () => {
            themeMenu.classList.remove('show');
        });
    }
    
    // Theme Option Selection
    themeOptions.forEach(opt => {
        opt.addEventListener('click', (e) => {
            e.stopPropagation();
            const selectedTheme = opt.getAttribute('data-theme');
            localStorage.setItem('saree-factory-theme', selectedTheme);
            applyTheme(selectedTheme);
            if (themeMenu) themeMenu.classList.remove('show');
        });
    });
    
    function applyTheme(theme) {
        // Clear all theme classes
        body.classList.remove('light-theme', 'dark-theme', 'theme-iphone-light', 'theme-iphone-dark', 'theme-iphone-titanium', 'theme-iphone-rose');
        body.classList.add(theme);
        
        // Update active class in menu options
        themeOptions.forEach(opt => {
            if (opt.getAttribute('data-theme') === theme) {
                opt.classList.add('active');
            } else {
                opt.classList.remove('active');
            }
        });
        
        // Update Theme Button Icon & Text
        const themeMap = {
            'light-theme': { label: 'Light', icon: '☀️' },
            'dark-theme': { label: 'Dark', icon: '🌙' },
            'theme-iphone-light': { label: 'iOS Light', icon: '📱' },
            'theme-iphone-dark': { label: 'iOS Midnight', icon: '🌃' },
            'theme-iphone-titanium': { label: 'Titanium Pro', icon: '🪙' },
            'theme-iphone-rose': { label: 'Rose Gold', icon: '🌸' }
        };
        
        const info = themeMap[theme] || themeMap['theme-iphone-dark'];
        if (themeLabel) themeLabel.textContent = info.label;
        if (themeIcon) themeIcon.textContent = info.icon;
    }
    
    // --- 2. MOBILE SIDEBAR NAVIGATION TOGGLE ---
    const mobileSidebarToggleBtn = document.getElementById('mobile-sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const mobileSidebarToggleIcon = mobileSidebarToggleBtn?.querySelector('i');
    const mobileSidebarToggleLabel = mobileSidebarToggleBtn?.querySelector('span');

    function setSidebarOpen(isOpen) {
        if (sidebar) sidebar.classList.toggle('active', isOpen);
        if (sidebarOverlay) sidebarOverlay.classList.toggle('active', isOpen);
        if (mobileSidebarToggleBtn) {
            mobileSidebarToggleBtn.setAttribute('aria-expanded', String(isOpen));
            mobileSidebarToggleBtn.setAttribute('aria-label', isOpen ? 'Close navigation menu' : 'Open navigation menu');
        }
        if (mobileSidebarToggleIcon) {
            mobileSidebarToggleIcon.classList.toggle('fa-bars', !isOpen);
            mobileSidebarToggleIcon.classList.toggle('fa-xmark', isOpen);
        }
        if (mobileSidebarToggleLabel) mobileSidebarToggleLabel.textContent = isOpen ? 'Close' : 'Menu';
    }
    
    function toggleSidebar() {
        setSidebarOpen(!sidebar?.classList.contains('active'));
    }
    
    function closeSidebar() {
        setSidebarOpen(false);
    }
    
    if (mobileSidebarToggleBtn) {
        mobileSidebarToggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleSidebar();
        });
    }
    
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebar);
    }
    
    // Close sidebar if clicked outside of it on mobile
    document.addEventListener('click', (e) => {
        if (sidebar && sidebar.classList.contains('active') && !sidebar.contains(e.target) && e.target !== mobileSidebarToggleBtn) {
            closeSidebar();
        }
    });

    
    // --- 3. AUTO FADING NOTIFICATIONS / ALERTS ---
    const alerts = document.querySelectorAll('.alert-card');
    alerts.forEach(alert => {
        // Auto-close after 5 seconds
        setTimeout(() => {
            fadeAndRemove(alert);
        }, 5000);
        
        // Manual close
        const closeBtn = alert.querySelector('.alert-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                fadeAndRemove(alert);
            });
        }
    });
    
    function fadeAndRemove(element) {
        element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        element.style.opacity = '0';
        element.style.transform = 'translateY(-20px)';
        setTimeout(() => {
            element.remove();
        }, 500);
    }
    
    // --- 4. MODAL DIALOGS TOGGLE UTILITIES ---
    window.openDialog = function(dialogId) {
        const dialog = document.getElementById(dialogId);
        if (dialog) {
            dialog.classList.add('active');
        }
    };
    
    window.closeDialog = function(dialogId) {
        const dialog = document.getElementById(dialogId);
        if (dialog) {
            dialog.classList.remove('active');
        }
    };
});
