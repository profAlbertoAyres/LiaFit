

const LiaUtils = {
    formatCurrency(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    },

    formatDate(isoString) {
        if (!isoString) return '';
        const [year, month, day] = isoString.split('-');
        return `${day}/${month}/${year}`;
    },

    maskCPF(input) {
        let v = input.value.replace(/\D/g, '').slice(0, 11);
        v = v.replace(/(\d{3})(\d)/, '$1.$2');
        v = v.replace(/(\d{3})(\d)/, '$1.$2');
        v = v.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
        input.value = v;
    },
    maskPhone(input) {
        let v = input.value.replace(/\D/g, '').slice(0, 11);
        if (v.length > 10) {
            v = v.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
        } else if (v.length > 6) {
            v = v.replace(/(\d{2})(\d{4})(\d{0,4})/, '($1) $2-$3');
        } else if (v.length > 2) {
            v = v.replace(/(\d{2})(\d{0,5})/, '($1) $2');
        }
        input.value = v;
    },

    /**
     * Aplica máscara de CEP
     * Uso: <input oninput="LiaUtils.maskCEP(this)">
     */
    maskCEP(input) {
        let v = input.value.replace(/\D/g, '').slice(0, 8);
        v = v.replace(/(\d{5})(\d)/, '$1-$2');
        input.value = v;
    },

    /**
     * Busca CEP via ViaCEP e preenche campos do formulário
     * Uso: <input onblur="LiaUtils.fetchCEP(this)">
     * Espera campos com name: rua, bairro, cidade, uf
     */
    async fetchCEP(input) {
        const cep = input.value.replace(/\D/g, '');
        if (cep.length !== 8) return;

        const originalDisabled = input.disabled;
        input.disabled = true;

        try {
            const res = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
            const data = await res.json();
            if (data.erro) {
                console.warn('CEP não encontrado:', cep);
                return;
            }

            const form = input.closest('form');
            if (!form) return;

            const fill = (name, value) => {
                const field = form.querySelector(`[name="${name}"]`);
                if (!field || !value) return;

                // Funciona tanto em <input> quanto em <select>
                if (field.tagName === 'SELECT') {
                    const opt = Array.from(field.options).find(
                        o => o.value.toUpperCase() === value.toUpperCase()
                    );
                    if (opt) field.value = opt.value;
                } else {
                    field.value = value;
                }
                field.dispatchEvent(new Event('change', {bubbles: true}));
            };

            fill('address', data.logradouro);
            fill('neighborhood', data.bairro);
            fill('city', data.localidade);
            fill('state', data.uf);

            const addressField = form.querySelector('[name="address"]');
            if (addressField && data.logradouro) addressField.focus();

        } catch (err) {
            console.warn('Erro ao buscar CEP:', err);
        } finally {
            input.disabled = originalDisabled;
        }
    },
    /**
     * Debounce — atrasa execução até parar de digitar
     * Uso: input.addEventListener('input', LiaUtils.debounce(fn, 400))
     */
    debounce(fn, delay = 300) {
        let timer;
        return function (...args) {
            clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), delay);
        };
    },

    /**
     * Copia texto para a área de transferência
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch {
            return false;
        }
    }
};
