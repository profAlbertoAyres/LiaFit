const LiaImageUpload = {
    SELECTORS: {
        root:    '[data-file-upload]',
        trigger: '[data-fu-trigger]',
        input:   '[data-fu-input]',
        image:   '[data-fu-image]',
        clear:   '[data-fu-clear]',
        remove:  '[data-fu-remove]',
        error:   '[data-fu-error]',
    },
    STATE: {
        hasImage:  'lia-form-file--has-image',
        willClear: 'lia-form-file--will-clear',
        hasError:  'lia-form-file--has-error',
    },

    DEFAULTS: {
        maxSizeMB: 5,
        accept: ['image/jpeg', 'image/png', 'image/webp', 'image/gif'],
    },

    init(root = document) {
        LiaApp.findIn(root, this.SELECTORS.root).forEach((elem) => {
            this.setup(elem);
        });
    },

    setup(root) {
        if (root.dataset.liaImageUploadInit) return;
        root.dataset.liaImageUploadInit = '1';

        const refs = this.getRefs(root);
        if (!refs.input || !refs.image) return;  // HTML incompleto.

        root._liaIURefs = refs;

        const originalSrc = refs.image.dataset.originalSrc || '';
        if (originalSrc) {
            refs.image.src = originalSrc;
            root.classList.add(this.STATE.hasImage);
        }

        // Liga eventos.
        if (refs.trigger) {
            refs.trigger.addEventListener('click', () => refs.input.click());
        }
        refs.input.addEventListener('change', (e) => this.onFileChange(root, e));
        if (refs.remove) {
            refs.remove.addEventListener('click', () => this.onRemove(root));
        }
    },

    /* ===============================================================
       HELPERS — Coleta de referências e configuração
       =============================================================== */

    getRefs(root) {
        // Usa cache se já existir (preenchido no setup).
        if (root._liaIURefs) return root._liaIURefs;

        return {
            trigger: root.querySelector(this.SELECTORS.trigger),
            input:   root.querySelector(this.SELECTORS.input),
            image:   root.querySelector(this.SELECTORS.image),
            clear:   root.querySelector(this.SELECTORS.clear),
            remove:  root.querySelector(this.SELECTORS.remove),
            error:   root.querySelector(this.SELECTORS.error),
        };
    },

    getConfig(root) {
        const maxSize = parseFloat(root.dataset.maxSize) || this.DEFAULTS.maxSizeMB;
        const acceptAttr = root.dataset.accept;
        const accept = acceptAttr
            ? acceptAttr.split(',').map((s) => s.trim())
            : this.DEFAULTS.accept;
        return { maxSize, accept };
    },

    /* ===============================================================
       EVENTO — Usuário selecionou um arquivo
       =============================================================== */

    onFileChange(root, event) {
        const refs = this.getRefs(root);
        const file = event.target.files[0];
        if (!file) return;

        this.clearError(root);

        // Valida antes de mostrar preview.
        const error = this.validate(root, file);
        if (error) {
            this.showError(root, error);
            refs.input.value = '';  // Descarta seleção inválida.
            return;
        }

        // Lê o arquivo como Data URL e renderiza no <img>.
        const reader = new FileReader();
        reader.onload = (e) => {
            refs.image.src = e.target.result;
            root.classList.add(this.STATE.hasImage);
            root.classList.remove(this.STATE.willClear);

            // Se o checkbox de clear estava marcado, desmarca
            // (o usuário trocou de ideia: agora quer subir foto nova).
            if (refs.clear) refs.clear.checked = false;
        };
        reader.readAsDataURL(file);
    },

    /* ===============================================================
       EVENTO — Usuário clicou em "Remover"
       Lógica inteligente: comportamento muda conforme o estado.
       =============================================================== */

    onRemove(root) {
        const refs = this.getRefs(root);
        const originalSrc = refs.image.dataset.originalSrc || '';
        const hasNewFile = refs.input.files && refs.input.files.length > 0;

        this.clearError(root);

        if (hasNewFile) {
            // CASO 1: usuário tinha selecionado arquivo novo → cancela seleção.
            refs.input.value = '';

            if (originalSrc) {
                // Volta pra foto original que estava salva.
                refs.image.src = originalSrc;
                root.classList.add(this.STATE.hasImage);
                root.classList.remove(this.STATE.willClear);
            } else {
                // Não havia foto original → volta pro placeholder.
                refs.image.removeAttribute('src');
                root.classList.remove(this.STATE.hasImage);
            }
        } else if (originalSrc) {
            // CASO 2: sem arquivo novo, mas há foto salva → marca pra apagar.
            // O Django apagará ao salvar (graças ao checkbox -clear).
            if (refs.clear) refs.clear.checked = true;
            root.classList.add(this.STATE.willClear);
            root.classList.remove(this.STATE.hasImage);
            refs.image.removeAttribute('src');
        }
    },

    /* ===============================================================
       VALIDAÇÃO
       =============================================================== */

    /**
     * Retorna mensagem de erro (string) ou null se o arquivo for válido.
     */
    validate(root, file) {
        const { maxSize, accept } = this.getConfig(root);

        // Valida tipo MIME.
        if (!accept.includes(file.type)) {
            const formatos = accept
                .map((t) => t.split('/')[1].toUpperCase())
                .join(', ');
            return `Tipo de arquivo não permitido. Use: ${formatos}.`;
        }

        // Valida tamanho.
        const sizeMB = file.size / (1024 * 1024);
        if (sizeMB > maxSize) {
            return `Arquivo muito grande (${sizeMB.toFixed(1)} MB). Máximo: ${maxSize} MB.`;
        }

        return null;
    },

    showError(root, message) {
        const refs = this.getRefs(root);
        if (refs.error) refs.error.textContent = message;
        root.classList.add(this.STATE.hasError);
    },

    clearError(root) {
        const refs = this.getRefs(root);
        if (refs.error) refs.error.textContent = '';
        root.classList.remove(this.STATE.hasError);
    },
};

LiaApp.register(LiaImageUpload);
