from django.urls import path
from . import views
from . import api_views
from . import monitor_views
from . import music_views

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
    path('api/now/<int:pk>/complete/', api_views.now_complete, name='now_complete'),

    # Activity API
    path('api/activity/create/', api_views.activity_create, name='activity_create'),
    path('api/activity/<int:pk>/update/', api_views.activity_update, name='activity_update'),
    path('api/activity/<int:pk>/delete/', api_views.activity_delete, name='activity_delete'),

    # Music API
    path('api/music/status/', music_views.music_status, name='music_status'),
    path('api/music/control/', music_views.music_control, name='music_control'),
    path('api/music/lyrics/', music_views.music_lyrics, name='music_lyrics'),

    # Link API
    path('api/links/', api_views.link_list, name='link_list'),
    path('api/links/create/', api_views.link_create, name='link_create'),
    path('api/links/<int:pk>/update/', api_views.link_update, name='link_update'),
    path('api/links/<int:pk>/delete/', api_views.link_delete, name='link_delete'),

    # Note API
    path('api/notes/', api_views.note_list, name='note_list'),
    path('api/notes/create/', api_views.note_create, name='note_create'),
    path('api/notes/import/', api_views.note_import, name='note_import'),
    path('api/notes/<int:pk>/update/', api_views.note_update, name='note_update'),
    path('api/notes/<int:pk>/delete/', api_views.note_delete, name='note_delete'),
]
