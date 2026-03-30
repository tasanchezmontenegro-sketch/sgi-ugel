# Business logic for the tickets app will be placed here.

from django.urls import reverse
from .models import Comentario, CustomUser, Estado, Notificacion

def resolver_incidencia_service(incidencia, tecnico, solucion_aplicada, evidencia=None):
    """
    Lógica de negocio centralizada para resolver incidencias.
    """
    # 1. Obtener el estado 'Resuelto'
    estado_resuelto = Estado.objects.filter(name__iexact='Resuelto').first()
    if not estado_resuelto:
        raise Estado.DoesNotExist("El estado 'Resuelto' no está configurado en el sistema.")

    # 2. Actualizar la incidencia
    incidencia.estado = estado_resuelto
    incidencia.solucion_aplicada = solucion_aplicada
    if evidencia:
        incidencia.evidencia_solucion = evidencia
    incidencia.save()

    # 3. Registrar comentario en el historial
    Comentario.objects.create(
        incidencia=incidencia,
        usuario=tecnico,
        tipo_comentario='confirmacion',
        texto=f'Resolución: {solucion_aplicada}',
        evidencia_adjunta=evidencia  # Guardamos la foto también en el comentario
    )

    return incidencia

def cerrar_incidencia_service(incidencia, usuario_que_cierra):
    """
    Cambia el estado a 'Cerrado' y registra la conformidad.
    """
    estado_cerrado = Estado.objects.filter(name__iexact='Cerrado').first()
    if not estado_cerrado:
        estado_cerrado = Estado.objects.create(name='Cerrado')

    incidencia.estado = estado_cerrado
    incidencia.save()

    Comentario.objects.create(
        incidencia=incidencia,
        usuario=usuario_que_cierra,
        tipo_comentario='confirmacion',
        texto='El usuario ha confirmado la solución. Ticket cerrado formalmente.'
    )
    return incidencia