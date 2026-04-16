# website/urls.py

from django.urls import path
from . import views

app_name = "website"

urlpatterns = [

    # ── Página Inicial ────────────────────
    path("", views.IndexView.as_view(), name="index"),

    # ── Sobre ─────────────────────────────
    # TODO: descomentar quando criar a view
    # path("sobre/", views.SobreView.as_view(), name="sobre"),

    # ── Contato ───────────────────────────
    # TODO: descomentar quando criar a view
    # path("contato/", views.ContatoView.as_view(), name="contato"),
]
