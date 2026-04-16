# core/menu/base.py

"""
Classes base do sistema de menu dinâmico.

O menu é composto por:
- MenuItem: um link individual (ex: "Dashboard", "Clientes")
- MenuGroup: um grupo de links com título (ex: "Financeiro")

Cada item/grupo pode ter uma permissão associada.
Só aparece no menu se o usuário tiver a permissão.
"""

from django.urls import reverse, NoReverseMatch


class MenuItem:
    """
    Representa um único link no menu.

    Parâmetros:
        label (str): texto exibido (será traduzido via i18n)
        url_name (str): nome da URL (ex: 'website:index')
        icon (str): nome do ícone Lucide (ex: 'home')
        permission (str): permissão necessária (ex: 'account.view_client')
                         None = visível para todos os autenticados
    """

    def __init__(self, label, url_name, icon="circle", permission=None):
        self.label = label
        self.url_name = url_name
        self.icon = icon
        self.permission = permission

    def get_url(self):
        """Tenta resolver a URL. Se não existir ainda, retorna '#'."""
        try:
            return reverse(self.url_name)
        except NoReverseMatch:
            return "#"

    def is_visible(self, user):
        """Verifica se o usuário pode ver este item."""
        # Sem permissão definida = todos os autenticados veem
        if not self.permission:
            return True

        # Superusuário vê tudo
        if user.is_superuser:
            return True

        return user.has_perm(self.permission)


class MenuGroup:
    """
    Agrupa vários MenuItems sob um título.

    Parâmetros:
        label (str): título do grupo (ex: 'Financeiro')
        items (list[MenuItem]): lista de itens do grupo
        icon (str): ícone do grupo
        permission (str): permissão para ver o grupo inteiro
                         None = visível se tiver pelo menos 1 item visível
        order (int): ordem de exibição (menor = aparece primeiro)
    """

    def __init__(self, label, items, icon="folder", permission=None, order=0):
        self.label = label
        self.items = items
        self.icon = icon
        self.permission = permission
        self.order = order

    def get_visible_items(self, user):
        """Retorna apenas os itens que o usuário pode ver."""
        return [item for item in self.items if item.is_visible(user)]

    def is_visible(self, user):
        """
        O grupo é visível se:
        1. O usuário tem a permissão do grupo, OU
        2. Tem pelo menos 1 item visível dentro dele
        """
        if self.permission:
            if user.is_superuser:
                return True
            if not user.has_perm(self.permission):
                return False

        # Mesmo sem permissão no grupo, só mostra se tiver itens visíveis
        return len(self.get_visible_items(user)) > 0
