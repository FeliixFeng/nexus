from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from nexus_core.pin_utils import verify_pin, lock_pin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('nexus_core.urls')),
    path('blog/', include('blog.urls')),
    path('links/', include('links.urls')),
    path('api/verify-pin/', verify_pin, name='verify_pin'),
    path('api/lock-pin/', lock_pin, name='lock_pin'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
