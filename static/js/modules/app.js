const LiaApp = {

    modules: [],

    register(module) {
        if (!module || typeof module.init !== 'function') {
            console.warn('[LiaApp] Módulo inválido — precisa ter init():', module);
            return;
        }
        this.modules.push(module);
    },
    initAll(root = document) {
        this.modules.forEach((module) => {
            try {
                module.init(root);
            } catch (err) {
                console.error('[LiaApp] Erro ao inicializar módulo:', module, err);
            }
        });
    },

    findIn(root, selector) {
        const results = [];
        if (root.matches && root.matches(selector)) {
            results.push(root);
        }
        if (root.querySelectorAll) {
            results.push(...root.querySelectorAll(selector));
        }
        return results;
    },
};

document.addEventListener('DOMContentLoaded', () => LiaApp.initAll());

window.LiaApp = LiaApp;
