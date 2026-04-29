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


// ─── 2. CONTROLE DO SELETOR DE CLÍNICAS (HEADER) ─────────────────────────────
const LiaOrgSelector = {
    toggleBtn: null,
    dropdown: null,

    init() {
        this.toggleBtn = document.getElementById('org-selector-toggle');
        this.dropdown = document.getElementById('org-selector-dropdown');

        // Se o usuário não tiver mais de uma clínica, esses elementos não existirão no HTML
        if (!this.toggleBtn || !this.dropdown) return;

        // Botão de abrir/fechar o dropdown
        this.toggleBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Evita que o clique feche imediatamente
            this.toggle();
        });

        // Clicar fora do dropdown faz ele fechar
        document.addEventListener('click', (e) => this.closeIfOutside(e));
    },

    toggle() {
        const isVisible = this.dropdown.style.display === 'block';
        this.dropdown.style.display = isVisible ? 'none' : 'block';
    },

    closeIfOutside(e) {
        // Se o clique não foi no botão nem dentro do dropdown, esconde o dropdown
        if (!this.toggleBtn.contains(e.target) && !this.dropdown.contains(e.target)) {
            this.dropdown.style.display = 'none';
        }
    }
};


// ─── 3. INICIALIZAÇÃO GLOBAL ─────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    LiaSidebar.init();
    LiaOrgSelector.init();
});
