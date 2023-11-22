from django.urls import path,include
from . import views
urlpatterns = [
    path('mapa', views.index, name = 'index'),
    path('mapa/<p_lat>/<p_lon>/<e_id>',views.calcularCamino, name = 'rutaCorta'),
]