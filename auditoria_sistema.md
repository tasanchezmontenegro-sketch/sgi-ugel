# Auditoría de Arquitectura de Software - SGI-UGEL

## 🚨 [Crítico] Todo lo que romperá el sistema en producción

### 1. Efimeridad de los archivos MEDIA en Render (Pérdida de datos)
Render utiliza almacenamiento efímero (a menos que pagues por un *Disk* extra). En tu `models.py` tienes campos como `foto`, `imagen_adjunta` y `evidencia_solucion`. Actualmente se guardan en el volumen de Docker local, pero en Render Cloud, **cada vez que tu app se reinicie o despliegues un cambio, todas las imágenes y evidencias se borrarán**.
**👉 Solución:** Tienes que integrar un gestor en la nube como **Cloudinary** (es gratis y fácil de configurar) o AWS S3 utilizando la librería `django-storages`.

### 2. Conflicto en `ALLOWED_HOSTS` y Host de Render
En tu `settings.py`, en la línea 22 defines `ALLOWED_HOSTS = ['*']`, pero luego al final del archivo lo sobrescribes: `ALLOWED_HOSTS = ['192.168.1.8', 'localhost', '127.0.0.1']`. Cuando Render intente levantar el proyecto bajo el dominio `https://tu-app.onrender.com`, Django arrojará un error `400 Bad Request` porque ese dominio no está en la lista.
**👉 Solución:** Deberías alimentarlo mediante el archivo `.env`: `ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])`.

### 3. Ausencia de `CSRF_TRUSTED_ORIGINS`
Django requiere obligatoriamente que confíes explícitamente en el origen para solicitudes por HTTPS (el cual Render usa por defecto). Sin esto, **los usuarios no podrán iniciar sesión ni crear tickets** (todo formulario POST devolverá un error `403 Forbidden`).
**👉 Solución:** Agrega en tu `settings.py`: `CSRF_TRUSTED_ORIGINS = ['https://tu-app.onrender.com']` (y ponlo como variable de entorno).

### 4. Variables de Entorno y `DEBUG` Riesgoso
El fallback de `DEBUG` en `settings.py` es sumamente arriesgado: `DEBUG = env('DEBUG', default=True)`. Si el entorno falla al leer las variables, dejarás el modo depuración abierto, lo que revelaría código e información sensible de tu servidor a cualquier persona.
**👉 Solución:** Cámbialo a `DEBUG = env('DEBUG', default=False)`.

---

## 🛠️ [Mejora] Para hacerlo más profesional y robusto

### 1. Vulnerabilidad de los "Magic Strings" en Modelos
Has definido `Estado` como un modelo independiente (tabla), lo cual es ideal para agregar estados sin tocar código. Sin embargo, en tus propiedades de validación revisas los estados por su nombre de texto de manera estricta: `self.estado.name == "Resuelto"`. Si un administrador cambia en la BD el nombre a "RESUELTO" o lo renombra a "Terminado", **la lógica del programa entero se rompe silenciosamente**.
**👉 Solución:** Es mejor usar un campo interno tipo alias genérico en el modelo `Estado` (ej. `codigo_interno="resuel"`), o manejarlo a través de un `Enum/Choices` estándar, validando siempre ese campo invariable y no el nombre que ven los usuarios.

### 2. Falta de Campos de Auditoría Críticos
El modelo `Incidencia` tiene fecha de creación (`fecha_creacion`), pero carece de algo indispensable en cualquier mesa de tickets moderna: **Trazabilidad de actualizaciones**.
**👉 Solución:** Te urjo a agregar el campo `fecha_actualizacion = models.DateTimeField(auto_now=True)` en tu modelo para poder medir Tiempos Reales de Resolución.

### 3. Inminente "N+1 Queries Problem" en Detalle de Incidencias
Has sido muy precavido usando `select_related` en tus dashboards, ¡gran trabajo ahí! Pero, en tu vista `detalle_incidencia` has puesto: `comentarios = incidencia.comentarios.all()`. 
Cuando la plantilla HTML del ticket cargue y consulte `{{ comentario.usuario.username }}` (para saber quién escribió el comentario), Django hará un Hit extra a la base de datos **por cada comentario individual**, arruinando el rendimiento en tickets largos.
**👉 Solución:** Usar `incidencia.comentarios.select_related('usuario').all()`.

### 4. Mejorar Seguridad para Sesiones (Cookies)
Aprovechando que Render te da HTTPS automático, debes proteger las credenciales al máximo. Agrega estas líneas a tu `settings.py` de producción:
```python
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
```

---

## 🔄 [Actualización] Componentes por quedar obsoletos o deuda técnica

### 1. Uso de `psycopg2-binary` en Producción
De acuerdo con tu `requirements.txt` usas `psycopg2-binary`. Los mismos creadores de esta librería indican en su documentación que la versión "binary" es excelente para entornos de desarrollo local, pero puede ocasionar comportamientos imprevistos bajo alto nivel de concurrencia en producción.
**👉 Solución:** Idealmente, usa `psycopg2` (lo que exigirá dependencias del sistema de compilación `libpq-dev`, que ya tienes en tu Dockerfile), o mucho mejor, actualízate a la nueva generación `psycopg` (v3).

### 2. Refinamiento de la Imagen Docker
Actualmente utilizas `python:3.12-slim` lo cual es una decisión muy sólida y tu `COPY` maneja excelente la caché de Docker. No obstante, obligas la instalación de un bloque gigantesco de librerías en sistema (`libcairo2-dev`, `libpango`, `weasyprint`, etc.) por tu exportador de PDF central.
**👉 Solución Futura:** Para entornos escalables en la nube, es altamente recomendable usar ***Multi-stage builds*** en Docker. Esto te permitiría compilar las dependencias en una fase y transferir sólo lo funcional al contenedor que corre en Render, manteniendo la imagen del Web Service súper ligera.
