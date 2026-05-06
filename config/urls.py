from django.contrib import admin
from django.urls import path, include

from core.views.space_hub_view import SpaceHubView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('website.urls'), name='home'),
    path('dashboard/', SpaceHubView.as_view(), name='dashboard'),
    path('auth/', include('account.urls.auth_url', namespace='auth')),
    path('org/<slug:org_slug>/', include(('core.urls.tenant_url', 'tenant'), namespace='tenant')),
    path('master/', include(('core.urls.master_url', 'master'), namespace='master')),
    path('painel/', include(('saas_admin.urls', 'saas_admin'), namespace='saas_admin')),]