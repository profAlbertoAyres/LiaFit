from django.urls import path

from catalog.views.service_type_view import ServiceTypeListView, ServiceTypeCreateView, ServiceTypeUpdateView

app_name = "catalog"

urlpatterns = [

    path("service-types/", ServiceTypeListView.as_view(), name="service_type_list",),
    path("service-types/create/", ServiceTypeCreateView.as_view(), name="service_type_create",),
    path("service-types/<int:pk>/edit/", ServiceTypeUpdateView.as_view(), name="service_type_update",),

]
