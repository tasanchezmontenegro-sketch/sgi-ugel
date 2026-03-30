# Metodología Kanban y Ciclo de Vida del Software
## Proyecto: Gestión de Incidencias v2 (Soporte TI)

Este documento detalla el análisis del desarrollo del sistema utilizando la metodología Kanban, extrayendo los componentes directly desde la infraestructura del código fuente.

---

### 1. BACKLOG DE FUNCIONALIDADES (Tareas Implementadas)

A continuación se listan las tareas detectadas en la arquitectura MVT (Modelo-Vista-Template), clasificadas por su implementación en el backend y rutas de acceso.

| Componente | Tarea / Funcionalidad | Módulo de Origen |
| :--- | :--- | :--- |
| **Módulos de Negocio** | Gestión de Usuarios (Customized User Model) | `tickets/models.py` |
| | Gestión de Áreas Organizacionales | `tickets/models.py` |
| | Gestión de Estados de Incidencia | `tickets/models.py` |
| | Registro y Seguimiento de Incidencias | `tickets/models.py` |
| | Sistema de Notificaciones Persistentes | `tickets/models.py` |
| | Hilos de Comentarios y Evidencias | `tickets/models.py` |
| **Vistas y Lógica** | Autenticación y Control de Acceso | `tickets/views.py` |
| | Dashboard Administrativo con KPIs | `tickets/views.py` |
| | Dashboard de Productividad Técnica | `tickets/views.py` |
| | Filtrado Avanzado de Incidencias | `tickets/views.py` |
| | Formulario de Registro de Tickets con Imágenes | `tickets/views.py` |
| | Sistema de Gestión y Asignación de TI | `tickets/views.py` |
| | Resolución de Casos y Carga de Evidencias | `tickets/views.py` |
| | Confirmación de Cierre y Reapertura de Tickets | `tickets/views.py` |
| | Administración de Cuentas (CRUD Usuarios) | `tickets/views.py` |
| | Restablecimiento Seguro de Contraseñas | `tickets/views.py` |
| | Centro de Notificaciones en Tiempo Real (HTMX) | `tickets/views.py` |
| | Generación de Reportes PDF (General/Detalle) | `tickets/views.py` |
| **Rutas (Endpoints)** | Endpoint: `/incidencias/admin/` | `tickets/urls.py` |
| | Endpoint: `/incidencias/asignadas/` | `tickets/urls.py` |
| | Endpoint: `/incidencias/crear/` | `tickets/urls.py` |
| | Endpoint: `/usuarios/crear/` | `tickets/urls.py` |
| | Endpoint: `/notificaciones/list/` | `tickets/urls.py` |
| | Endpoint: `/reportes/pdf/` | `tickets/urls.py` |

---

### 2. HISTORIAS DE USUARIO

Basado en la estructura de modelos y los privilegios detectados (`administrador`, `tecnico`, `usuario`), se han redactado las siguientes historias de usuario que sustentan el sistema:

#### Rol: Administrador (Ingeniero TI)
1. **Alta de Usuarios:** "Como **administrador**, quiero **crear nuevas cuentas de usuario**, para **habilitar el acceso al sistema al personal de nuevas áreas**."
2. **Asignación de Cargas:** "Como **administrador**, quiero **asignar incidencias a los técnicos disponibles**, para **garantizar que cada problema sea atendido por un experto**."
3. **Reportes de Gestión:** "Como **administrador**, quiero **exportar reportes generales en PDF**, para **presentar métricas de desempeño a la gerencia**."

#### Rol: Técnico (Soporte TI)
1. **Gestión de Pendientes:** "Como **tecnico**, quiero **ver una lista de mis incidencias asignadas**, para **organizar mi jornada de trabajo eficientemente**."
2. **Documentar Solución:** "Como **tecnico**, quiero **registrar la solución aplicada y subir una foto de evidencia**, para **validar la resolución del ticket de manera formal**."
3. **Notificaciones:** "Como **tecnico**, quiero **recibir alertas en tiempo real**, para **atender incidencias críticas de manera inmediata**."

#### Rol: Usuario (Trabajador)
1. **Reporte de Problema:** "Como **usuario**, quiero **crear un ticket de incidencia con fotos adjuntas**, para **solicitar soporte técnico sobre herramientas de mi área**."
2. **Confirmación de Servicio:** "Como **usuario**, quiero **cerrar los tickets cuando el problema ha sido resuelto**, para **mantener mi historial de soporte actualizado**."
3. **Transparencia:** "Como **usuario**, quiero **ver el estado y comentarios de mi incidencia**, para **saber cuándo será atendido mi requerimiento**."

---

### 3. CLASIFICACIÓN KANBAN (Estado del Desarrollo)

Siguiendo el flujo de trabajo configurado, las tareas se clasifican según su nivel de implementación (Vistas + URLs + Templates).

| COLUMNA: POR HACER | COLUMNA: EN PROGRESO | COLUMNA: COMPLETADO |
| :--- | :--- | :--- |
| Integración con servicios de correo externo (SMTP) | Refinamiento de la lógica de reapertura de tickets | Sistema de Autenticación y Logout |
| Módulo de inventario de hardware relacionado | Implementación de búsquedas avanzadas por rango de IP | Dashboard de Administración y Técnicos |
| API REST para integración con Apps Móviles | Optimización de tiempos de carga de imágenes masivas | CRUD completo de Usuarios y Áreas |
| Sistema de SLA (Tiempos de respuesta esperados) | | Listado y Filtrado de Incidencias (MVT) |
| | | Generación de Reportes PDF Dinámicos |
| | | Sistema de Notificaciones via WebSockets/HTMX |
| | | Perfil de Usuario con carga de foto (AJAX) |

---

### 4. ITERACIONES / FASES DEL DESARROLLO

Se detectaron las siguientes fases de desarrollo basadas en el histórico de migraciones del sistema (`tickets/migrations/`):

#### **Fase 1: Cimiento Estructural (Migración 0001)**
*   **Logros:** Creación de las tablas base: `CustomUser`, `Area`, `Estado`, `Incidencia`, `Comentario`.
*   **Enfoque:** Establecer el core funcional de la base de datos y la arquitectura inicial del proyecto Django.

#### **Fase 2: Perfilamiento y UX (Migraciones 0002 - 0003)**
*   **Logros:** Extensión del modelo de usuario con campos de contacto (`telefono`), pertenencia a `area` y `foto` de perfil.
*   **Enfoque:** Personalizar la experiencia del usuario y fortalecer la identificación del personal.

#### **Fase 3: Seguridad y Gobernanza (Migraciones 0004 - 0006)**
*   **Logros:** Implementación de cambios de contraseña obligatorios y refinamiento de llaves foráneas en los estados de incidencias.
*   **Enfoque:** Robustecer la seguridad de acceso y la integridad referencial del flujo de estados.

#### **Fase 4: Comunicación y Tiempo Real (Migraciones 0007 - 0008)**
*   **Logros:** Rediseño del sistema de notificaciones (leídos/no leídos) y tracking de `last_seen` para presencia online.
*   **Enfoque:** Mejorar la interactividad y proporcionar monitoreo de actividad en vivo.

---

### 5. MÉTRICAS BÁSICAS DEL PROYECTO

Estadísticas extraídas directamente de la auditoría del código fuente:

| Métrica | Valor Detectado |
| :--- | :--- |
| **Total de Vistas (Logic Functions)** | 29 |
| **Total de Modelos (Entidades)** | 6 |
| **Total de Rutas URL (Endpoints)** | 29 |
| **Total de Templates (UI Componentes)** | 19 |
| **Total de Migraciones (Iteraciones)** | 8 |
| **Lenguaje Dominante** | Python (Django Framework) |
| **Interactividad Frontend** | HTMX / CSS Vanilla / JavaScript |

> **Nota:** Este informe ha sido generado automáticamente mediante el análisis de la base de código del proyecto `gestion_incidencias_v2`.
