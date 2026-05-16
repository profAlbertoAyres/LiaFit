const LiaForms = {

    init(root = document) {
        this.initFlatpickr(root);
        this.initMasks(root);
        this.initConfirmDelete(root);
        this.initPasswordToggles(root);
    },

    initFlatpickr(root) {
        if (typeof flatpickr === 'undefined') return;

        LiaApp.findIn(root, '[data-datepicker]').forEach(input => {
            if (input._flatpickr) return;

            const mode = input.dataset.datepicker;
            const config = {
                locale: 'pt',
                dateFormat: 'd/m/Y',
                allowInput: true,
            };

            if (mode === 'datetime') {
                config.enableTime = true;
                config.dateFormat = 'd/m/Y H:i';
                config.time_24hr = true;
            }

            if (mode === 'time') {
                config.enableTime = true;
                config.noCalendar = true;
                config.dateFormat = 'H:i';
                config.time_24hr = true;
            }

            flatpickr(input, config);
        });
    },

    initMasks(root) {
        const maskMap = {
            cpf: LiaUtils.maskCPF,
            phone: LiaUtils.maskPhone,
            cep: LiaUtils.maskCEP,
        };

        LiaApp.findIn(root, '[data-mask]').forEach(input => {
            if (input.dataset.liaMaskInit) return;
            input.dataset.liaMaskInit = '1';

            const maskFn = maskMap[input.dataset.mask];
            if (maskFn) {
                input.addEventListener('input', () => maskFn(input));
            }

            if (input.dataset.mask === 'cep') {
                input.addEventListener('blur', () => LiaUtils.fetchCEP(input));
            }
        });
    },

    initConfirmDelete(root) {
        const message = 'Tem certeza que deseja excluir? Esta ação não pode ser desfeita.';

        LiaApp.findIn(root, '[data-confirm-delete]').forEach(el => {
            // Guarda
            if (el.dataset.liaConfirmInit) return;
            el.dataset.liaConfirmInit = '1';

            const eventName = el.tagName === 'FORM' ? 'submit' : 'click';

            el.addEventListener(eventName, (e) => {
                if (!confirm(message)) e.preventDefault();
            });
        });
    },

    initPasswordToggles(root) {
        LiaApp.findIn(root, '[data-toggle-password]').forEach(btn => {
            if (btn.dataset.liaToggleInit) return;
            btn.dataset.liaToggleInit = '1';

            btn.addEventListener('click', () => {
                const targetId = btn.dataset.togglePassword;
                const input = document.getElementById(targetId);
                if (!input) return;

                if (input.type === 'password') {
                    input.type = 'text';
                    btn.innerHTML = '<i data-lucide="eye"></i>';
                } else {
                    input.type = 'password';
                    btn.innerHTML = '<i data-lucide="eye-off"></i>';
                }

                if (typeof lucide !== 'undefined') {
                    lucide.createIcons({ root: btn });
                }
            });
        });
    },
};

LiaApp.register(LiaForms);
