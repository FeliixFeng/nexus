from django.urls import path
from . import views
from . import api_views
from . import monitor_views
from . import rss_views
from . import read_views
from links import api_views as link_api
from blog import api_views as blog_api

app_name = 'nexus_core'

urlpatterns = [
    path('', views.home, name='home'),
    path('now/', views.now_page, name='now_page'),
    path('monitor/', monitor_views.monitor, name='monitor'),
    path('rss/', rss_views.rss_page, name='rss_page'),
    path('read/', read_views.read_page, name='read_page'),
    path('api/monitor/data/', monitor_views.monitor_data, name='monitor_data'),
    path('api/rss/data/', rss_views.rss_data, name='rss_data'),

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

    path('api/notes/', blog_api.note_list, name='note_list'),
    path('api/notes/create/', blog_api.note_create, name='note_create'),
    path('api/notes/import/', blog_api.note_import, name='note_import'),
    path('api/notes/<int:pk>/update/', blog_api.note_update, name='note_update'),
    path('api/notes/<int:pk>/delete/', blog_api.note_delete, name='note_delete'),
]
