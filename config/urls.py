from django.contrib import admin
from django.urls import path, include

from core.views.shared.space_hub_view import SpaceHubView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('website.urls'), name='home'),
    path('dashboard/', SpaceHubView.as_view(), name='dashboard'),
    path('auth/', include('account.urls.auth_url', namespace='auth')),
    path('org/<slug:org_slug>/', include(('core.urls.tenant_url', 'tenant'), namespace='tenant')),
    path('personal/', include(('core.urls.personal_url', 'master'), namespace='master')),
    path('painel/', include(('saas_admin.urls', 'saas_admin'), namespace='saas_admin')),]