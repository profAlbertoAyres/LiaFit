/* =============================================================================
   LIA LINDA — SIDEBAR & HEADER COMPONENTS
   Controle de colapso da sidebar (desktop/mobile) e dropdown do header.
   ============================================================================= */

// ─── 1. CONTROLE DA SIDEBAR ──────────────────────────────────────────────────
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
    }
};


// ─── 2. INICIALIZAÇÃO GLOBAL ─────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    LiaSidebar.init();
});
