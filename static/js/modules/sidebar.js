const LiaSidebar = {
    STORAGE_KEY: 'lia-sidebar-collapsed',
    MOBILE_BREAKPOINT: 768,

    sidebar: null,
    overlay: null,
    toggleBtn: null,

    init() {
        this.sidebar = document.getElementById('lia-sidebar');
        this.overlay = document.getElementById('lia-sidebar-overlay');
        this.toggleBtn = document.getElementById('sidebar-toggle');

        if (!this.sidebar || !this.toggleBtn) return;

        this.restoreState();

        this.toggleBtn.addEventListener('click', () => this.toggle());

        if (this.overlay) {
            this.overlay.addEventListener('click', () => this.closeMobile());
        }

        window.addEventListener('resize', () => this.handleResize());
        this.bindAccordionTriggers();
    },

    isMobile() {
        return window.innerWidth <= this.MOBILE_BREAKPOINT;
    },

    toggle() {
        if (this.isMobile()) {
            this.toggleMobile();
        } else {
            this.toggleCollapse();
        }
    },

    toggleCollapse() {
        const isCollapsed = this.sidebar.classList.toggle('lia-sidebar--collapsed');
        localStorage.setItem(this.STORAGE_KEY, isCollapsed ? 'true' : 'false');
        if (isCollapsed) {
            this.closeAllAccordions();
        }
    },

    toggleMobile() {
        const isOpen = this.sidebar.classList.toggle('lia-sidebar--mobile-open');
        if (this.overlay) {
            this.overlay.classList.toggle('lia-sidebar-overlay--active', isOpen);
        }
        document.body.style.overflow = isOpen ? 'hidden' : '';
    },

    closeMobile() {
        this.sidebar.classList.remove('lia-sidebar--mobile-open');
        if (this.overlay) {
            this.overlay.classList.remove('lia-sidebar-overlay--active');
        }
        document.body.style.overflow = '';
    },

    restoreState() {
        if (this.isMobile()) return;
        const saved = localStorage.getItem(this.STORAGE_KEY);
        if (saved === 'true') {
            this.sidebar.classList.add('lia-sidebar--collapsed');
        }
    },

    handleResize() {
        if (!this.isMobile()) {
            this.closeMobile();
        }
    },
    closeAllAccordions() {
        this.sidebar.querySelectorAll('.accordion .collapse.show').forEach(el => {
            bootstrap.Collapse.getOrCreateInstance(el, { toggle: false }).hide();
        });
    },

    bindAccordionTriggers() {
        this.sidebar.querySelectorAll('.accordion [data-bs-toggle="collapse"]').forEach(trigger => {
            trigger.addEventListener('click', () => {
                if (this.sidebar.classList.contains('lia-sidebar--collapsed') && !this.isMobile()) {
                    this.sidebar.classList.remove('lia-sidebar--collapsed');
                    localStorage.setItem(this.STORAGE_KEY, 'false');
                }
            });
        });
    }
};


document.addEventListener('DOMContentLoaded', () => {
    LiaSidebar.init();
});
