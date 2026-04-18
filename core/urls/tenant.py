from django.urls import path, include
from core.views import DashboardView

app_name = 'tenant'

# Tudo aqui já está dentro de /org/<slug>/
urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    # path('scheduling/', include('scheduling.urls')),
    # path('financial/', include('financial.urls')),
    # path('account/', include('account.urls.management')),
]
