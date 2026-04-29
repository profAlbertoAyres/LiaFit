/* =============================================================================
   LIA LINDA — FORMS
   Inicialização automática de Flatpickr, máscaras e validação visual.
   ============================================================================= */

const LiaForms = {

    init() {
        this.initFlatpickr();
        this.initMasks();
        this.initConfirmDelete();
        this.initPasswordToggles();
    },

    /* -----------------------------------------------------------------
       FLATPICKR — Inicializa campos com data-datepicker
       <input type="text" data-datepicker>
       <input type="text" data-datepicker="datetime">
       <input type="text" data-datepicker="time">
       ----------------------------------------------------------------- */
    initFlatpickr() {
        if (typeof flatpickr === 'undefined') return;

        document.querySelectorAll('[data-datepicker]').forEach(input => {
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

    /* -----------------------------------------------------------------
       MÁSCARAS — Inicializa campos com data-mask
       <input type="text" data-mask="cpf">
       <input type="text" data-mask="phone">
       <input type="text" data-mask="cep">
       ----------------------------------------------------------------- */
    initMasks() {
        const maskMap = {
            cpf: LiaUtils.maskCPF,
            phone: LiaUtils.maskPhone,
            cep: LiaUtils.maskCEP,
        };

        document.querySelectorAll('[data-mask]').forEach(input => {
            const maskFn = maskMap[input.dataset.mask];
            if (maskFn) {
                input.addEventListener('input', () => maskFn(input));
            }
        });

        // Auto-busca CEP no blur
        document.querySelectorAll('[data-mask="cep"]').forEach(input => {
            input.addEventListener('blur', () => LiaUtils.fetchCEP(input));
        });
    },

    /* -----------------------------------------------------------------
       CONFIRMAÇÃO DE EXCLUSÃO
       <form data-confirm-delete>
       <a href="..." data-confirm-delete>
       ----------------------------------------------------------------- */
    initConfirmDelete() {
        document.querySelectorAll('[data-confirm-delete]').forEach(el => {
            if (el.tagName === 'FORM') {
                el.addEventListener('submit', (e) => {
                    if (!confirm('Tem certeza que deseja excluir? Esta ação não pode ser desfeita.')) {
                        e.preventDefault();
                    }
                });
            }

            if (el.tagName === 'A') {
                el.addEventListener('click', (e) => {
                    if (!confirm('Tem certeza que deseja excluir? Esta ação não pode ser desfeita.')) {
                        e.preventDefault();
                    }
                });
            }
        });
    },
    /* -----------------------------------------------------------------
       TOGGLE DE SENHA — Inicializa botões com data-toggle-password
       <button type="button" data-toggle-password="id_da_senha">
       ----------------------------------------------------------------- */
    initPasswordToggles() {
        document.querySelectorAll('[data-toggle-password]').forEach(btn => {
            btn.addEventListener('click', () => {
                // Pega o ID do input alvo através do data-attribute
                const targetId = btn.dataset.togglePassword;
                const input = document.getElementById(targetId);

                if (!input) return;

                // Alterna o tipo do input e reinjeta a tag <i> para o Lucide
                if (input.type === 'password') {
                    input.type = 'text';
                    btn.innerHTML = '<i data-lucide="eye"></i>';
                } else {
                    input.type = 'password';
                    btn.innerHTML = '<i data-lucide="eye-off"></i>';
                }

                // Renderiza o novo ícone apenas dentro deste botão
                if (typeof lucide !== 'undefined') {
                    lucide.createIcons({ root: btn });
                }
            });
        });
    }
};

document.addEventListener('DOMContentLoaded', () => LiaForms.init());
