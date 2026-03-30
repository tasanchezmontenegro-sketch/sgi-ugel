from .models import NotificacionUsuario

def unread_notifications_count(request):
    if request.user.is_authenticated:
        # Cargamos las notificaciones en el contexto global 
        # para que el dropdown funcione al recargar la página.
        recibidas = NotificacionUsuario.objects.filter(usuario=request.user).select_related('notificacion').order_by('-fecha_recibida')
        notifications = recibidas[:10]
        unread_count = recibidas.filter(leido=False).count()
        return {
            "unread_notifications_count": unread_count,
            "notifications": notifications
        }
    return {"unread_notifications_count": 0, "notifications": []}