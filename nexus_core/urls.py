from django.urls import path
from . import views
from . import api_views

app_name = 'nexus_core'

urlpatterns = [
    path('', views.home, name='home'),
    path('activities/', views.activity_list, name='activity_list'),
    path('api/activity/create/', api_views.activity_create, name='activity_create'),
    path('api/activity/<int:pk>/update/', api_views.activity_update, name='activity_update'),
    path('api/activity/<int:pk>/delete/', api_views.activity_delete, name='activity_delete'),
]
