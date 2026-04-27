

const LiaAlerts = {
    DISMISS_DELAY: 5000,

    init() {
        const alerts = document.querySelectorAll('.lia-alert');
        alerts.forEach(alert => {
            this.bindClose(alert);
            this.autoDismiss(alert);
        });
    },

    bindClose(alert) {
        const closeBtn = alert.querySelector('.lia-alert__close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.dismiss(alert));
        }
    },

    autoDismiss(alert) {
        setTimeout(() => this.dismiss(alert), this.DISMISS_DELAY);
    },

    dismiss(alert) {
        if (alert.classList.contains('lia-alert--dismissing')) return;
        alert.classList.add('lia-alert--dismissing');
        alert.addEventListener('animationend', () => alert.remove());
    }
};

document.addEventListener('DOMContentLoaded', () => LiaAlerts.init());
