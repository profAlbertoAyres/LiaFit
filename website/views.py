# website/dashboard.py

from django.views.generic import TemplateView


# ── Página Inicial ────────────────────────
# Primeira página que o usuário vê ao acessar o sistema
# Apresenta o sistema e direciona para login ou registro
class IndexView(TemplateView):
    template_name = "website/index.html"


# ── Sobre ─────────────────────────────────
# Página institucional sobre o sistema
# TODO: criar quando avançarmos no projeto
# class SobreView(TemplateView):
#     template_name = "website/sobre.html"


# ── Contato ───────────────────────────────
# Página de contato / suporte
# TODO: criar quando avançarmos no projeto
# class ContatoView(TemplateView):
#     template_name = "website/contato.html"
