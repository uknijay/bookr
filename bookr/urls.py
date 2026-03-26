from django.contrib import admin # URLs for entire project?
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from bookr import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')), # main app urls?
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # ???