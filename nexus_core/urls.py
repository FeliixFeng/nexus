from django.urls import path
from . import views
from . import api_views
from links import api_views as link_api

app_name = 'nexus_core'

urlpatterns = [
    path('', views.home, name='home'),
    path('status/', views.status_page, name='status_page'),
    path('now/', views.now_page, name='now_page'),
    path('other/', views.other_page, name='other_page'),

    path('api/now/create/', api_views.now_create, name='now_create'),
    path('api/now/<int:pk>/update/', api_views.now_update, name='now_update'),
    path('api/now/<int:pk>/delete/', api_views.now_delete, name='now_delete'),
    path('api/now/<int:pk>/complete/', api_views.now_complete, name='now_complete'),

    path('api/activity/create/', api_views.activity_create, name='activity_create'),
    path('api/activity/<int:pk>/update/', api_views.activity_update, name='activity_update'),
    path('api/activity/<int:pk>/delete/', api_views.activity_delete, name='activity_delete'),

    path('api/links/', link_api.link_list, name='link_list'),
    path('api/links/create/', link_api.link_create, name='link_create'),
    path('api/links/<int:pk>/update/', link_api.link_update, name='link_update'),
    path('api/links/<int:pk>/delete/', link_api.link_delete, name='link_delete'),
]
