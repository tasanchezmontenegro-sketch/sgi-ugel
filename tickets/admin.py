from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Area, Estado, Incidencia, Comentario, Notificacion, NotificacionUsuario

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'area', 'is_staff', 'is_active')
    list_filter = ('role', 'area', 'is_staff', 'is_active')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Extra', {
            'fields': ('role', 'telefono', 'area', 'foto', 'last_password_change', 'must_change_password')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Extra', {
            'fields': ('role', 'telefono', 'area')
        }),
    )

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'creador', 'area', 'prioridad', 'estado', 'tecnico_asignado', 'fecha_creacion')
    list_filter = ('prioridad', 'estado', 'categoria')
    search_fields = ('descripcion', 'creador__username', 'tecnico_asignado__username')
    readonly_fields = ('fecha_creacion',)

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('incidencia', 'usuario', 'tipo_comentario', 'fecha_creacion')
    list_filter = ('tipo_comentario',)

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'mensaje', 'incidencia', 'fecha_creacion')
    list_filter = ('tipo',)
    search_fields = ('mensaje',)

@admin.register(NotificacionUsuario)
class NotificacionUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'notificacion', 'leido', 'fecha_recibida')
    list_filter = ('leido', 'usuario')
    search_fields = ('usuario__username', 'notificacion__mensaje')