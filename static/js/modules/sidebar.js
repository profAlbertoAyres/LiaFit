/* =============================================================================
   LIAFIT — SIDEBAR
   Controle de colapso (desktop) e abertura/fechamento (mobile).
   ============================================================================= */

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

        // Restaura estado salvo (desktop)
        this.restoreState();

        // Botão toggle
        this.toggleBtn.addEventListener('click', () => this.toggle());

        // Overlay fecha sidebar no mobile
        if (this.overlay) {
            this.overlay.addEventListener('click', () => this.closeMobile());
        }

        // Redimensionamento da janela
        window.addEventListener('resize', () => this.handleResize());
    },

    /** Verifica se é mobile */
    isMobile() {
        return window.innerWidth <= this.MOBILE_BREAKPOINT;
    },

    /** Toggle geral */
    toggle() {
        if (this.isMobile()) {
            this.toggleMobile();
        } else {
            this.toggleCollapse();
        }
    },

    /** Desktop: colapsa / expande */
    toggleCollapse() {
        const isCollapsed = this.sidebar.classList.toggle('lia-sidebar--collapsed');
        localStorage.setItem(this.STORAGE_KEY, isCollapsed ? 'true' : 'false');
    },

    /** Mobile: abre */
    toggleMobile() {
        const isOpen = this.sidebar.classList.toggle('lia-sidebar--mobile-open');
        if (this.overlay) {
            this.overlay.classList.toggle('lia-sidebar-overlay--active', isOpen);
        }
        document.body.style.overflow = isOpen ? 'hidden' : '';
    },

    /** Mobile: fecha */
    closeMobile() {
        this.sidebar.classList.remove('lia-sidebar--mobile-open');
        if (this.overlay) {
            this.overlay.classList.remove('lia-sidebar-overlay--active');
        }
        document.body.style.overflow = '';
    },

    /** Restaura estado do localStorage */
    restoreState() {
        if (this.isMobile()) return;
        const saved = localStorage.getItem(this.STORAGE_KEY);
        if (saved === 'true') {
            this.sidebar.classList.add('lia-sidebar--collapsed');
        }
    },

    /** Ao redimensionar, limpa estados inconsistentes */
    handleResize() {
        if (!this.isMobile()) {
            // Saiu do mobile → fecha overlay, restaura collapse
            this.closeMobile();
        }
    }
};

document.addEventListener('DOMContentLoaded', () => LiaSidebar.init());
