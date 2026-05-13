from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from config import settings
from core.views.shared.space_hub_view import SpaceHubView
from core.views.shared.space_switch_view import SpaceSwitchView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('website.urls'), name='home'),
    path('dashboard/', SpaceHubView.as_view(), name='dashboard'),
    path('space/switch/', SpaceSwitchView.as_view(), name='space_switch',),
    path('auth/', include('account.urls.auth_url', namespace='auth')),
    path('org/<slug:org_slug>/', include(('core.urls.tenant_url', 'tenant'), namespace='tenant')),
    path('personal/', include(('core.urls.personal_url', 'personal'), namespace='personal')),
    path('painel/', include(('saas_admin.urls', 'saas_admin'), namespace='saas_admin')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)