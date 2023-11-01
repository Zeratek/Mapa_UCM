from django.urls import path,include
from . import views
urlpatterns = [
    path('adminmap/', views.index, name = 'adminIndex'),
    path('adminmap/login', views.login_page, name = 'adminLogin'),
    path('adminmap/logout', views.logout_page, name = 'adminLogout'),
    path('adminmap/save_datas', views.saveData, name = 'saveData'),
    path('adminmap/view_edification', views.viewEdificationPage, name = 'viewEdification'),
    path('adminmap/view_edification/<name>/<option>', views.viewEdificationPageList, name = 'listEdification'),
    path('adminmap/create_edification', views.createEdificationPage, name = 'createEdification'),
    path('adminmap/update_edification/<e_id>', views.updateEdificationPage, name = 'updateEdification'),
    path('adminmap/delete_edification/<e_id>', views.deleteEdificationPage, name = 'deleteEdification'),
]