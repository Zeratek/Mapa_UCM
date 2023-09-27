from django.urls import path,include
from . import views
urlpatterns = [
    path('mapa', views.index, name = 'index'),
    path('buildinginfo/<buildingID>',views.building_info, name = 'buildingInfo'),
    path('mapa/<p_lat>/<p_lon>',views.calcularCamino, name = 'rutaCorta'),
]