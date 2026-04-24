# core/urls/tenant.py
from django.urls import path

from core.views import DashboardView
from core.views.role import (
    RoleCreateView,
    RoleDetailView,
    RoleListView,
    RoleUpdateView,
)
from core.views.tenant import (
    RolePermissionCreateView,
    RolePermissionListView,
    UserPermissionCreateView,
    UserPermissionListView,
)

app_name = 'tenant'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # # ── MEMBROS ──
    # path('members/', MemberListView.as_view(), name='member_list'),
    # path('members/<int:pk>/', MemberDetailView.as_view(), name='member_detail'),
    #
    # # ── ORGANIZAÇÃO (detalhe único - a própria org do contexto) ──
    # path('organization/', OrganizationDetailView.as_view(), name='organization_detail'),
    # path('organization/update/', OrganizationUpdateView.as_view(), name='organization_update'),
    #
    # # ── ROLE PERMISSIONS ──
    # path('role-permissions/', RolePermissionListView.as_view(), name='role_permission_list'),
    # path('role-permissions/create/', RolePermissionCreateView.as_view(), name='role_permission_create'),
    #
    # # ── USER PERMISSIONS ──
    # path('user-permissions/', UserPermissionListView.as_view(), name='user_permission_list'),
    # path('user-permissions/create/', UserPermissionCreateView.as_view(), name='user_permission_create'),

    # ── ROLES ──
    path('roles/', RoleListView.as_view(), name='role_list'),
    path('roles/create/', RoleCreateView.as_view(), name='role_create'),
    path('roles/<int:pk>/', RoleDetailView.as_view(), name='role_detail'),
    path('roles/<int:pk>/update/', RoleUpdateView.as_view(), name='role_update'),
    path('roles/<int:pk>/permissions/', RoleCreateView.as_view(), name='role_permissions_update'),
]


# ============================================================
# DEBUG VIEW (mover pra core/views/debug.py é mais limpo)
# ============================================================
from django.http import JsonResponse


def debug_context(request, **kwargs):
    ctx = getattr(request, 'context', None)
    data = {
        'url_kwargs': {k: str(v) for k, v in kwargs.items()},
        'user': str(request.user),
        'is_authenticated': request.user.is_authenticated,
        'is_superuser': request.user.is_superuser,
        'has_context': ctx is not None,
    }
    if ctx:
        membership = getattr(ctx, 'membership', None)
        data['context'] = {
            'organization': str(getattr(ctx, 'organization', None)),
            'membership': str(membership),
            'has_permissions_attr': hasattr(ctx, 'permissions'),
            'permissions_count': len(getattr(ctx, 'permissions', []) or []),
            'has_modules_attr': hasattr(ctx, 'modules'),
            'modules_count': len(getattr(ctx, 'modules', []) or []),
        }
        if membership:
            try:
                data['context']['member_roles'] = list(
                    membership.roles.values_list('slug', flat=True)
                )
            except Exception as e:
                data['context']['member_roles_error'] = str(e)

    return JsonResponse(data, json_dumps_params={'indent': 2})
