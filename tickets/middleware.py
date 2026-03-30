from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

class OnlinePresenceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # 1. Seguridad: Si el usuario fue desactivado por el Admin, lo deslogueamos inmediatamente
            if not request.user.is_active:
                from django.contrib.auth import logout
                logout(request)
                return self.get_response(request)

            # 2. Presencia: Actualizamos last_seen de forma eficiente
            User = request.user.__class__
            User.objects.filter(pk=request.user.pk).update(last_seen=timezone.now())
        
        return self.get_response(request)

class ForzarCambioPasswordMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Si debe cambiar contraseña y no está ya en las páginas permitidas
            if getattr(request.user, 'must_change_password', False):
                
                # Definimos rutas que NO disparan la redirección
                rutas_permitidas = [
                    reverse('password_change_forced'), 
                    reverse('logout'),
                ]

                # Para evitar loops infinitos
                if request.path not in rutas_permitidas:
                    return redirect('password_change_forced')

        return self.get_response(request)