from django.urls import path
from . import views
from . import api_views
from . import monitor_views

app_name = 'nexus_core'

urlpatterns = [
    path('', views.home, name='home'),
    path('now/', views.now_page, name='now_page'),
    path('monitor/', monitor_views.monitor, name='monitor'),
    path('api/monitor/data/', monitor_views.monitor_data, name='monitor_data'),

    # NowItem API
    path('api/now/create/', api_views.now_create, name='now_create'),
    path('api/now/<int:pk>/update/', api_views.now_update, name='now_update'),
    path('api/now/<int:pk>/delete/', api_views.now_delete, name='now_delete'),

    # Activity API
    path('api/activity/create/', api_views.activity_create, name='activity_create'),
    path('api/activity/<int:pk>/update/', api_views.activity_update, name='activity_update'),
    path('api/activity/<int:pk>/delete/', api_views.activity_delete, name='activity_delete'),
]
