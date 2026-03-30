# Documentación Técnica Visual - Gestión de Incidencias V2 🏛️

Este documento contiene la arquitectura visual completa del sistema en formato **Mermaid.js**. Puedes visualizar estos diagramas instalando la extensión recomendada al final de este archivo.

---

## 📊 1. Diagrama Entidad-Relación (DER / MER)
*Diseñado para una arquitectura futura en producción con PostgreSQL.*

```mermaid
erDiagram
    CUSTOM_USER {
        int id PK
        string username
        string role "usuario, tecnico, administrador"
        string email
        string password
        string telefono
        int area_id FK
        string foto
        datetime last_seen
        datetime date_joined
        boolean is_active
        boolean must_change_password
        datetime last_password_change
    }

    AREA {
        int id PK
        string name
    }

    ESTADO {
        int id PK
        string name "Pendiente, En Proceso, Resuelto, Cerrado"
    }

    INCIDENCIA {
        int id PK
        int creador_id FK "CustomUser"
        int area_id FK "Area"
        string categoria "hardware, software, red, sistema"
        string prioridad "baja, media, alta, critica"
        text descripcion
        string imagen_adjunta
        datetime fecha_creacion
        int estado_id FK "Estado"
        int tecnico_asignado_id FK "CustomUser"
        date fecha_programada_atencion
        time hora_programada_atencion
        text observaciones_internas
        text solucion_aplicada
        string evidencia_solucion
    }

    COMENTARIO {
        int id PK
        int incidencia_id FK "Incidencia"
        int usuario_id FK "CustomUser"
        string tipo_comentario "tecnico, confirmacion, persiste, observacion"
        text texto
        datetime fecha_creacion
        string evidencia_adjunta
    }

    NOTIFICACION {
        int id PK
        int incidencia_id FK "Incidencia"
        text mensaje
        string tipo "asignacion, estado, comentario, etc."
        datetime fecha_creacion
        string link
    }

    NOTIFICACION_USUARIO {
        int id PK
        int usuario_id FK "CustomUser"
        int notificacion_id FK "Notificacion"
        boolean leido
        datetime fecha_recibida
    }

    AREA ||--o{ CUSTOM_USER : "pertenece"
    AREA ||--o{ INCIDENCIA : "afecta a"
    CUSTOM_USER ||--o{ INCIDENCIA : "crea (trabajador)"
    CUSTOM_USER ||--o{ INCIDENCIA : "atiende (tecnico)"
    ESTADO ||--o{ INCIDENCIA : "define"
    INCIDENCIA ||--o{ COMENTARIO : "tiene"
    CUSTOM_USER ||--o{ COMENTARIO : "escribe"
    INCIDENCIA ||--o{ NOTIFICACION : "genera"
    NOTIFICACION ||--o{ NOTIFICACION_USUARIO : "distribuida a"
    CUSTOM_USER ||--o{ NOTIFICACION_USUARIO : "recibe"
```

---

## 🔄 2. Diagrama de Flujo de Estados (Incidencias)
*Lógica real de transiciones del sistema.*

```mermaid
stateDiagram-v2
    [*] --> Pendiente : Registro de Incidencia
    
    Pendiente --> En_Proceso : Admin asigna técnico
    Pendiente --> En_Proceso : Técnico auto-asigna
    
    En_Proceso --> Resuelto : Técnico registra solución
    
    Resuelto --> Cerrado : Usuario confirma solución
    Resuelto --> En_Proceso : Usuario reporta que persiste (Reabrir)
    
    Cerrado --> [*]
    
    state En_Proceso {
        [*] --> Atencion_Programada
        Atencion_Programada --> Ejecucion_Tecnica
    }
```

---

## 🔔 3. Diagrama de Secuencia (Notificaciones Real-Time)
*Evento → Signal → WebSocket → HTMX Interface.*

```mermaid
sequenceDiagram
    participant U as Actor (Admin/Tec/User)
    participant D as Django View / Signal
    participant M as Model (Notificacion)
    participant CL as Channel Layer (Redis)
    participant C as WebSocket Consumer
    participant F as Frontend (JS / HTMX)

    U->>D: Realiza acción (ej. Comentar, Resolver)
    D->>M: Crea Notificacion y NotificacionUsuario
    M-->>D: post_save Triggered
    D->>CL: send_notification_update (Async Group Send)
    CL->>C: Recibe mensaje de grupo
    C->>F: Envía Payload JSON (unread_count, message)
    F->>F: Actualiza Campana (JS) y Lista (HTMX)
```

---

## 🏗️ 4. Arquitectura de Software (Patrón MVT + Real-time)

```mermaid
graph TD
    User((Usuario)) -->|Request HTTP/WS| WebServer[Servidor Web / Nginx]
    WebServer -->|WSGI| Django[Django Core]
    WebServer -->|ASGI| Daphne[Daphne / Channels]
    
    subgraph Django_Framework
        URLs[URL Resolver] --> View[View Logic]
        View --> Models[Models / ORM]
        View --> Templates[Templates / HTML + HTMX]
        Models --> DB[(PostgreSQL)]
    end
    
    Daphne --> Cons[Consumers]
    Cons --> Redis[(Redis - Channel Layer)]
    View -.->|Signals| Cons
    
    Templates -->|Response| User
```

---

## ☁️ 5. Arquitectura de Infraestructura en la Nube (Cloud Deployment)

```mermaid
graph LR
    User[Browser Client] --> DNS{Route 53 / Cloudflare}
    DNS --> LB[Nginx Ingress / ALB]
    LB --> Docker[Docker Container Service]
    
    subgraph Docker_Host
        D_API[Django App - Gunicorn/Daphne]
        D_Celery[Celery Workers - Tareas Pesadas]
    end
    
    D_API --> RDS[(PostgreSQL Managed)]
    D_API --> Redis[(Redis Cache/WS)]
    D_API --> S3[S3 Bucket - Static/Media]
    
    Monitoring[CloudWatch / Grafana] -.-> Docker
```

---

## 🔄 6. Diagrama de Flujo del Proceso de Atención

```mermaid
flowchart TD
    A[Inicio: Usuario crea incidencia] --> B{¿Asignada?}
    B -- No --> C[Admin revisa y asigna técnico]
    B -- Sí --> D[Técnico recibe notificación]
    C --> D
    D --> E[Técnico programa y ejecuta atención]
    E --> F[Técnico registra solución y evidencia]
    F --> G[Estado: Resuelto]
    G --> H{¿Usuario conforme?}
    H -- No (Reabrir) --> E
    H -- Sí (Confirmar) --> I[Estado: Cerrado]
    I --> J[Fin del proceso]
```

---

## 🎨 7. Paleta de Colores del Sistema

```mermaid
graph LR
    Primary[#0f172a <br/> Slate 900 <br/> Sidebar/Header] --- Secondary[#3b82f6 <br/> Blue 500 <br/> Acciones/Botones]
    
    subgraph Estados
        Pendiente[#64748b <br/> Slate 500]
        EnProceso[#3b82f6 <br/> Blue 500]
        Resuelto[#22c55e <br/> Green 500]
        Cerrado[#94a3b8 <br/> Slate 400]
        Critica[#ef4444 <br/> Red 500]
    end
    
    style Primary fill:#0f172a,color:#fff
    style Secondary fill:#3b82f6,color:#fff
    style Pendiente fill:#64748b,color:#fff
    style EnProceso fill:#3b82f6,color:#fff
    style Resuelto fill:#22c55e,color:#fff
    style Cerrado fill:#94a3b8,color:#fff
    style Critica fill:#ef4444,color:#fff
```

---

## 🧭 8. Diagrama de Navegación / Arquitectura de Pantallas

```mermaid
flowchart TD
    Login[Login] --> Auth{Validación}
    Auth --> Dashboard[Dashboard Central]
    
    Dashboard --> IncList[Lista de Incidencias]
    Dashboard --> Profile[Mi Perfil / Ajustes]
    
    IncList --> Det[Detalle de Incidencia]
    IncList --> Create[Formulario Crear Incidencia]
    
    subgraph Admin_Only
        Users[Gestión de Usuarios]
        Areas[Configuración de Áreas]
        Reports[Generación de Reportes PDF]
    end
    
    Dashboard -.-> Admin_Only
    Det --> Resolved[Modal Resolución]
    Det --> Comms[Hilo de Comentarios]
```

---

## 👥 9. Diagrama de Casos de Uso

```mermaid
graph LR
    subgraph Actores
        User[Trabajador]
        Tec[Técnico]
        Admin[Administrador]
    end
    
    subgraph Casos_de_Uso
        UC1(Reportar Incidencia)
        UC2(Ver Estado de Mis Tickets)
        UC3(Responder Comentarios)
        UC4(Gestionar Tickets Asignados)
        UC5(Registrar Solución/Evidencia)
        UC6(Asignar Técnicos)
        UC7(Gestionar Usuarios y Áreas)
        UC8(Dashboard Global de Estadísticas)
    end
    
    User --> UC1
    User --> UC2
    User --> UC3
    
    Tec --> UC4
    Tec --> UC5
    Tec --> UC3
    
    Admin --> UC6
    Admin --> UC7
    Admin --> UC8
    Admin --> UC4
```

---

## ⚙️ Recomendación de Extensión para VS Code

Para visualizar estos diagramas directamente en tu barra lateral de VS Code y exportarlos a PNG/SVG:

1.  Abre el panel de extensiones (`Ctrl+Shift+X`).
2.  Busca e instala: **Mermaid Editor** (de *yuzutech*) o **Markdown Mermaid Preview**.
3.  Para exportar:
    *   Con el archivo `.md` abierto, abre la vista previa (`Ctrl+Shift+V`).
    *   Haz clic derecho sobre el diagrama y selecciona **Save as image** (dependiendo de la extensión instalada).
    *   Se recomienda **Mermaid Markdown Syntex & Preview** para una integración más fluida.

> [!NOTE]
> Esta documentación está preparada para escalar a una base de datos **PostgreSQL** y despliegue con contenedores **Docker**.
