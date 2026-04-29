/* =============================================================================
   LIA LINDA — UTILS
   Funções utilitárias reutilizáveis em todo o projeto.
   ============================================================================= */

const LiaUtils = {

    /**
     * Formata valor para moeda brasileira (R$)
     * LiaUtils.formatCurrency(1500.5) → "R$ 1.500,50"
     */
    formatCurrency(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    },

    /**
     * Formata data ISO para dd/mm/aaaa
     * LiaUtils.formatDate('2026-04-15') → "15/04/2026"
     */
    formatDate(isoString) {
        if (!isoString) return '';
        const [year, month, day] = isoString.split('-');
        return `${day}/${month}/${year}`;
    },

    /**
     * Aplica máscara de CPF enquanto digita
     * Uso: <input oninput="LiaUtils.maskCPF(this)">
     */
    maskCPF(input) {
        let v = input.value.replace(/\D/g, '').slice(0, 11);
        v = v.replace(/(\d{3})(\d)/, '$1.$2');
        v = v.replace(/(\d{3})(\d)/, '$1.$2');
        v = v.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
        input.value = v;
    },

    /**
     * Aplica máscara de telefone (fixo ou celular)
     * Uso: <input oninput="LiaUtils.maskPhone(this)">
     */
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

        try {
            const res = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
            const data = await res.json();
            if (data.erro) return;

            const form = input.closest('form');
            if (!form) return;

            const fill = (name, value) => {
                const field = form.querySelector(`[name="${name}"]`);
                if (field) field.value = value || '';
            };

            fill('rua', data.logradouro);
            fill('bairro', data.bairro);
            fill('cidade', data.localidade);
            fill('uf', data.uf);
        } catch (err) {
            console.warn('Erro ao buscar CEP:', err);
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
