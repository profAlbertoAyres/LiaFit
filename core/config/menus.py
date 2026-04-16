# core/config/menus.py

"""
Definição de TODOS os menus do sistema.

Aqui é onde você configura o que aparece na sidebar.
Cada app pode ter seu próprio grupo.

Este arquivo é carregado uma vez pelo AppConfig do core.
"""

from django.utils.translation import gettext_lazy as _
from core.menu import MenuItem, MenuGroup, menu_registry


def register_menus():
    """Registra todos os menus do sistema."""

    # ── Dashboard (sempre visível para logados) ──────
    menu_registry.register(
        MenuGroup(
            label=_("Geral"),
            icon="layout-dashboard",
            order=0,
            items=[
                MenuItem(
                    label=_("Dashboard"),
                    url_name="dashboard:index",
                    icon="home",
                ),
            ],
        )
    )

    # ── Pacientes / Clientes ─────────────────────────
    # TODO: descomentar quando criar o app
    # menu_registry.register(
    #     MenuGroup(
    #         label=_("Atendimento"),
    #         icon="users",
    #         order=10,
    #         items=[
    #             MenuItem(
    #                 label=_("Pacientes"),
    #                 url_name="patient:list",
    #                 icon="user",
    #                 permission="patient.view_patient",
    #             ),
    #             MenuItem(
    #                 label=_("Consultas"),
    #                 url_name="appointment:list",
    #                 icon="calendar",
    #                 permission="appointment.view_appointment",
    #             ),
    #         ],
    #     )
    # )

    # ── Financeiro ───────────────────────────────────
    # TODO: descomentar quando criar o app
    # menu_registry.register(
    #     MenuGroup(
    #         label=_("Financeiro"),
    #         icon="wallet",
    #         order=20,
    #         items=[
    #             MenuItem(
    #                 label=_("Lançamentos"),
    #                 url_name="financial:list",
    #                 icon="receipt",
    #                 permission="financial.view_record",
    #             ),
    #         ],
    #     )
    # )

    # ── Administração ────────────────────────────────
    # TODO: descomentar quando criar o app
    # menu_registry.register(
    #     MenuGroup(
    #         label=_("Administração"),
    #         icon="settings",
    #         order=100,
    #         items=[
    #             MenuItem(
    #                 label=_("Profissionais"),
    #                 url_name="account:professional_list",
    #                 icon="briefcase",
    #                 permission="account.view_professional",
    #             ),
    #             MenuItem(
    #                 label=_("Permissões"),
    #                 url_name="account:group_list",
    #                 icon="shield",
    #                 permission="auth.view_group",
    #             ),
    #         ],
    #     )
    # )
