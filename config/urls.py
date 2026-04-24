from django.contrib import admin
from django.urls import path, include

from core.urls.tenant import debug_context
from core.views import DashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('website.urls')),
    path('auth/', include('account.urls.auth', namespace='auth')),
    path('manage/', include('account.urls.management', namespace='management')),
    path('org/<slug:org_slug>/', include(('core.urls.tenant', 'tenant'), namespace='tenant')),
    path('org/<slug:org_slug>/debug/context/', debug_context, name='debug_context_tenant'),
    path('master/', include(('core.urls.master', 'master'), namespace='master')),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
