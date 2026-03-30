from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from .utils.images import process_image
import os


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("usuario", "Usuario (Trabajador)"),
        ("tecnico", "Técnico"),
        ("administrador", "Administrador/Ingeniero TI"),
    )
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default="usuario")
    telefono = models.CharField(max_length=15, null=True, blank=True) 
    area = models.ForeignKey("Area", on_delete=models.SET_NULL, null=True, blank=True)
    foto = models.ImageField(upload_to="perfiles/", null=True, blank=True)
    last_password_change = models.DateTimeField(default=timezone.now)
    must_change_password = models.BooleanField(default=False)
    # Nueva funcionalidad: Presencia Online
    last_seen = models.DateTimeField(null=True, blank=True)

    @property
    def is_online(self):
        if not self.last_seen:
            return False
        # Consideramos online si estuvo activo hace menos de 2 minutos
        return (timezone.now() - self.last_seen).total_seconds() < 120

    @property
    def last_activity_text(self):
        if not self.last_seen:
            return "Nunca"
        diff = timezone.now() - self.last_seen
        seconds = diff.total_seconds()
        if seconds < 60:
            return "Ahora"
        elif seconds < 3600:
            return f"Hace {int(seconds // 60)} min"
        else:
            return f"Hace {int(seconds // 3600)} h"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.foto:
            # Foto de perfil pequeña (300x300)
            process_image(self.foto, size=(300, 300), quality=70)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Area(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Estado(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

def get_default_estado():
    # Busca el objeto "Pendiente" por nombre. Si no existe, lo crea.
    estado, _ = Estado.objects.get_or_create(name="Pendiente")
    return estado.id

class Incidencia(models.Model):
    CATEGORIA_CHOICES = (
        ("hardware", "Hardware"),
        ("software", "Software"),
        ("red", "Red"),
        ("sistema", "Sistema"),
    )

    PRIORIDAD_CHOICES = (
        ("baja", "Baja"),
        ("media", "Media"),
        ("alta", "Alta"),
        ("critica", "Crítica"),
    )

    creador = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name="incidencias_creadas")
    area = models.ForeignKey("Area", on_delete=models.CASCADE)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES)
    descripcion = models.TextField()
    imagen_adjunta = models.ImageField(upload_to="incidencias_imagenes/", null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    estado = models.ForeignKey("Estado", on_delete=models.PROTECT, default=get_default_estado)
    
    tecnico_asignado = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name="incidencias_asignadas")
    fecha_programada_atencion = models.DateField(null=True, blank=True)
    hora_programada_atencion = models.TimeField(null=True, blank=True)
    observaciones_internas = models.TextField(null=True, blank=True)
    
    solucion_aplicada = models.TextField(null=True, blank=True)
    evidencia_solucion = models.ImageField(upload_to="soluciones_evidencias/", null=True, blank=True)

    @property
    def puede_cerrar(self):
        return self.estado.name == "Resuelto"

    @property
    def esta_asignada(self):
        return self.tecnico_asignado is not None

    @property
    def puede_reabrir(self):
        return self.estado.name == "Resuelto"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.imagen_adjunta:
            process_image(self.imagen_adjunta, size=(1024, 1024))
        if self.evidencia_solucion:
            process_image(self.evidencia_solucion, size=(1024, 1024))

    def __str__(self):
        return f"Incidencia #{self.id} - {self.descripcion[:50]}"

class Notificacion(models.Model):
    TIPO_CHOICES = (
        ("asignacion", "Asignación"),
        ("estado", "Cambio de Estado"),
        ("comentario", "Nuevo Comentario"),
        ("nueva_incidencia", "Nueva Incidencia"), 
        ("incidencia_resuelta", "Incidencia Resuelta"), 
        ("desasignacion", "Desasignación"),
    )

    incidencia = models.ForeignKey(Incidencia, on_delete=models.CASCADE, null=True, blank=True)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    link = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"Notificación: {self.tipo} - {self.mensaje[:30]}..."

    class Meta:
        ordering = ["-fecha_creacion"]

class NotificacionUsuario(models.Model):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notificaciones")
    notificacion = models.ForeignKey(Notificacion, on_delete=models.CASCADE, related_name="usuarios")
    leido = models.BooleanField(default=False)
    fecha_recibida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notif para {self.usuario.username} ({'Leído' if self.leido else 'No leído'})"

    class Meta:
        ordering = ["-fecha_recibida"]
        unique_together = ('usuario', 'notificacion')

class Comentario(models.Model):
    TIPO_COMENTARIO_CHOICES = (
        ("tecnico", "Comentario Técnico"),
        ("confirmacion", "Confirmación de Solución"),
        ("persiste", "Problema Persiste"),
        ("observacion", "Observación Interna"),
    )

    incidencia = models.ForeignKey(Incidencia, on_delete=models.CASCADE, related_name="comentarios")
    usuario = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    tipo_comentario = models.CharField(max_length=20, choices=TIPO_COMENTARIO_CHOICES, default="observacion")
    texto = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    evidencia_adjunta = models.ImageField(upload_to="comentarios_evidencias/", null=True, blank=True)

    def __str__(self):
        return f"Comentario en Incidencia #{self.incidencia.id} por {self.usuario.username}"

# --- SEÑALES PARA NOTIFICACIONES REAL-TIME ---
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@receiver(post_save, sender=NotificacionUsuario)
def send_notification_update(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        # El número de no leídos para este usuario en particular (modelo intermedio)
        unread_count = NotificacionUsuario.objects.filter(usuario=instance.usuario, leido=False).count()
        
        async_to_sync(channel_layer.group_send)(
            f"user_{instance.usuario.id}_notifications",
            {
                "type": "send_notification",
                "message": instance.notificacion.mensaje,
                "tipo": instance.notificacion.tipo,
                "unread_count": unread_count
            }
        )