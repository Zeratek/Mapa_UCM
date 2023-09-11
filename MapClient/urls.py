from django.urls import path,include
from . import views
urlpatterns = [
    path('', views.index, name = 'index'),
    path('buildinginfo/<buildingID>',views.building_info, name = 'buildingInfo'),
]