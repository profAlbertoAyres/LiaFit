# saas_admin/views/user_view.py
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count, Q

from core.views import BaseDetailView
from core.views.base_view import BaseListView
from saas_admin.filters.user_filter import UserFilter

User = get_user_model()


class SuperuserRequiredMixin(UserPassesTestMixin):
    """Apenas superusuários acessam o painel SaaS Admin."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser


class UserListView(SuperuserRequiredMixin, BaseListView):
    model = User
    template_name = "saas_admin/user/list.html"
    context_object_name = "users"

    require_tenant = False
    permission_required = None  # Acesso controlado pelo SuperuserRequiredMixin

    paginate_by = 20
    filterset_class = UserFilter
    ordering = '-date_joined'

    def get_queryset(self):
        qs = User.objects.all().annotate(
            org_count=Count('memberships__organization', distinct=True),
            active_org_count=Count(
                'memberships__organization',
                filter=Q(memberships__is_active=True),
                distinct=True,
            ),
        )
        self.queryset = qs
        return super().get_queryset()

class UserDetailView(SuperuserRequiredMixin, BaseDetailView):
    model = User
    template_name = "saas_admin/user/detail.html"
    context_object_name = "user_obj"  # evita conflito com request.user

    require_tenant = False
    permission_required = None

    def get_queryset(self):
        return User.objects.prefetch_related(
            'memberships__organization',
            'memberships__roles',
        ).annotate(
            org_count=Count('memberships__organization', distinct=True),
            active_org_count=Count(
                'memberships__organization',
                filter=Q(memberships__is_active=True),
                distinct=True,
            ),
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user_obj = self.object

        ctx['memberships'] = user_obj.memberships.select_related(
            'organization'
        ).prefetch_related('roles').order_by('-is_active', '-created_at')

        # Estatísticas rápidas
        ctx['stats'] = {
            'total_orgs': user_obj.org_count,
            'active_orgs': user_obj.active_org_count,
            'inactive_orgs': user_obj.org_count - user_obj.active_org_count,
        }

        return ctx