class RequestContext:

    def __init__(self):
        self.user = None

        self.organization = None
        self.tenant_id = None

        self.profile = None
        self.professional = None

        self.roles = []
        self.modules = set()
        self.permissions = set()

    # ------------------------
    # HELPERS DE SEGURANÇA
    # ------------------------

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def has_permission(self, perm: str) -> bool:
        return perm in self.permissions

    def is_admin(self) -> bool:
        return "admin" in self.roles

    def has_module(self, module: str) -> bool:
        return module in self.modules

    def is_authenticated(self) -> bool:
        return self.user is not None and self.user.is_authenticated