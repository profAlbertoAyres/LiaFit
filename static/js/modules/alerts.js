

const LiaAlerts = {
    DISMISS_DELAY: 5000,

    init(root = document) {
        LiaApp.findIn(root, '.lia-alert').forEach(alert => {
            // Guarda: evita re-inicializar o mesmo alerta
            if (alert.dataset.liaAlertInit) return;
            alert.dataset.liaAlertInit = '1';

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
    },
};

LiaApp.register(LiaAlerts);
