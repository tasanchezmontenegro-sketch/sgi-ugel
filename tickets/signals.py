from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from .models import Incidencia, Comentario, CustomUser, Notificacion, NotificacionUsuario

# ============================================================
# HELPERS
# ============================================================
def _link(view_name, pk):
    try:
        return reverse(view_name, args=[pk])
    except Exception:
        return None

def notify_users(users, mensaje, tipo, incidencia=None, link=None):
    """
    Crea una sola Notificacion (contenido) y la vincula a múltiples usuarios
    mediante NotificacionUsuario.
    """
    if not users:
        return
    
    # Si viene un solo usuario, lo metemos en lista
    if not isinstance(users, (list, set, tuple)) and hasattr(users, 'pk'):
        users = [users]
    elif hasattr(users, 'exists'): # Queryset
        users = list(users)

    # Crear el objeto de contenido una vez
    notif = Notificacion.objects.create(
        incidencia=incidencia,
        mensaje=mensaje,
        tipo=tipo,
        link=link
    )

    # Crear el vínculo para cada destinatario
    for user in users:
        NotificacionUsuario.objects.get_or_create(
            usuario=user,
            notificacion=notif
        )

# ============================================================
# SEÑALES DE INCIDENCIA
# ============================================================

@receiver(pre_save, sender=Incidencia)
def incidencia_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            anterior = sender.objects.get(pk=instance.pk)
            instance._estado_anterior = anterior.estado
            instance._tecnico_anterior = anterior.tecnico_asignado
        except sender.DoesNotExist:
            instance._estado_anterior = None
            instance._tecnico_anterior = None

@receiver(post_save, sender=Incidencia)
def incidencia_post_save(sender, instance, created, **kwargs):
    link = _link("detalle_incidencia", instance.pk)

    if created:
        # 1. Notificar a administradores (si el creador no es admin)
        if instance.creador and instance.creador.role != 'administrador':
            admins = CustomUser.objects.filter(role='administrador', is_active=True)
            notify_users(
                admins, 
                f"🚩 Nuevo reporte de {instance.creador.get_full_name() or instance.creador.username} (#{instance.id:04d})",
                "nueva_incidencia",
                incidencia=instance,
                link=link
            )

        # 2. Notificar al técnico si se asigna desde el inicio
        if instance.tecnico_asignado:
            notify_users(
                instance.tecnico_asignado,
                f"🆕 Se te asignó el ticket #{instance.id:04d}",
                "asignacion",
                incidencia=instance,
                link=link
            )
    else:
        tecnico_anterior = getattr(instance, '_tecnico_anterior', None)
        id_anterior = tecnico_anterior.id if tecnico_anterior else None
        id_actual = instance.tecnico_asignado.id if instance.tecnico_asignado else None

        if id_actual != id_anterior:
            if id_anterior:
                notify_users(tecnico_anterior, f"🚫 Se retiró tu asignación del ticket #{instance.id:04d}", "desasignacion", incidencia=instance, link=link)
            if id_actual:
                notify_users(instance.tecnico_asignado, f"🆕 Se te ha asignado el ticket #{instance.id:04d}", "asignacion", incidencia=instance, link=link)

        estado_anterior = getattr(instance, '_estado_anterior', None)
        if estado_anterior and estado_anterior != instance.estado:
            msg = f"🔄 Ticket #{instance.id:04d} cambió a: {instance.estado.name}"
            destinatarios = []
            if instance.creador: destinatarios.append(instance.creador)
            if id_actual and id_actual == id_anterior: destinatarios.append(instance.tecnico_asignado)
            notify_users(destinatarios, msg, "estado", incidencia=instance, link=link)

@receiver(post_save, sender=Comentario)
def comentario_post_save(sender, instance, created, **kwargs):
    if not created: return
    incidencia = instance.incidencia
    autor = instance.usuario
    link = _link("detalle_incidencia", incidencia.pk)
    msg = f"💬 {autor.get_full_name() or autor.username} comentó en #{incidencia.id:04d}"

    destinatarios = set()
    if incidencia.creador and incidencia.creador != autor:
        destinatarios.add(incidencia.creador)
    if incidencia.tecnico_asignado and incidencia.tecnico_asignado != autor:
        destinatarios.add(incidencia.tecnico_asignado)
    if autor.role != 'administrador':
        admins = CustomUser.objects.filter(role='administrador', is_active=True)
        for admin in admins:
            if admin != autor: destinatarios.add(admin)

    notify_users(list(destinatarios), msg, "comentario", incidencia=incidencia, link=link)