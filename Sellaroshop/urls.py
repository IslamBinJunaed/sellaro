from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('store/', include('store.urls')),
    path('products/', include('products.urls')),
    path('', include('shop_app.urls')),  # homepage
    path('accounts/', include('django.contrib.auth.urls')),  # adds login/logout/password URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
