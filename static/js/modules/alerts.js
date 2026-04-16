/* =============================================================================
   LIAFIT — ALERTS
   Auto-dismiss dos alertas do Django Messages + fechar manual.
   ============================================================================= */

const LiaAlerts = {
    /** Tempo padrão para sumir (ms) */
    DISMISS_DELAY: 5000,

    /** Inicializa todos os alertas presentes na página */
    init() {
        const alerts = document.querySelectorAll('.lia-alert');
        alerts.forEach(alert => {
            this.bindClose(alert);
            this.autoDismiss(alert);
        });
    },

    /** Botão de fechar */
    bindClose(alert) {
        const closeBtn = alert.querySelector('.lia-alert__close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.dismiss(alert));
        }
    },

    /** Auto-dismiss após X segundos */
    autoDismiss(alert) {
        setTimeout(() => this.dismiss(alert), this.DISMISS_DELAY);
    },

    /** Animação de saída + remoção do DOM */
    dismiss(alert) {
        if (alert.classList.contains('lia-alert--dismissing')) return;
        alert.classList.add('lia-alert--dismissing');
        alert.addEventListener('animationend', () => alert.remove());
    }
};

document.addEventListener('DOMContentLoaded', () => LiaAlerts.init());
