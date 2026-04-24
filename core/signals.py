# core/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def sync_core_after_migrate(sender, **kwargs):
    """
    Sincroniza catálogo + SystemRoles automaticamente após cada 'migrate'.

    Roda apenas quando o app 'core' é migrado (evita disparar N vezes,
    uma por cada app do projeto).
    Pula em testes (verbosity=0) pra acelerar a suíte.
    """
    if sender.name != "core":
        return

    if kwargs.get("verbosity", 1) == 0:
        return

    # Import tardio: evita problema de app ainda não carregado
    from core.bootstrap import sync_system_catalog, sync_system_roles

    # --- 1) Catálogo (Modules / Items / Permissions) ---
    try:
        cat_stats = sync_system_catalog(verbose=False)
        print(
            f"  ✓ Catálogo sincronizado: "
            f"+{cat_stats['modules_created']} módulos, "
            f"+{cat_stats['items_created']} itens, "
            f"+{cat_stats['permissions_created']} permissões"
        )
    except Exception as e:
        print(f"  ⚠️  Falha ao sincronizar catálogo: {e}")
        return  # sem catálogo não adianta tentar roles

    # --- 2) SystemRoles (depende das permissions existirem) ---
    try:
        role_stats = sync_system_roles(verbose=False)
        print(
            f"  ✓ SystemRoles sincronizados: "
            f"+{role_stats['system_roles_created']} criados, "
            f"~{role_stats['system_roles_updated']} atualizados, "
            f"{role_stats['system_role_permissions_set']} permissões vinculadas"
        )
    except Exception as e:
        print(f"  ⚠️  Falha ao sincronizar SystemRoles: {e}")
