from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

handler404 = 'tickets.views.error_404_view'
handler500 = 'tickets.views.error_500_view'

urlpatterns = [
    path('admin/', admin.site.admin_url if hasattr(admin.site, 'admin_url') else admin.site.urls),
    path('', include('tickets.urls')),  # Las URLs de tu app tickets
]

# Vista extra solo para probar el diseño del 404 en modo desarrollo:
if settings.DEBUG:
    from django.shortcuts import render
    urlpatterns.append(path('404/', lambda request: render(request, 'tickets/404.html', status=404)))


# ESTA ES LA PARTE CLAVE PARA LAS IMÁGENES Y ESTÁTICOS EN DESARROLLO Y DOCKER(DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
