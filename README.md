<br>

## **NUAM**
<br>

### **🧩 Descripción del Proyecto**

* NUAM es un sistema de gestión documental y de usuarios que integra:
* CRUD de Usuarios
* CRUD de Personas asociadas
* CRUD de Documentos (con subida de archivos)
* Sistema de Login con roles (Administrador / Usuario)
* Registro detallado de eventos de negocio
* Mensajería asíncrona mediante Apache Pulsar (Pub/Sub)
* Envío de eventos en tiempo real mediante Apache Pulsar
* Microservicios desacoplados
* API REST completa mediante Django REST Framework
* Visualización de indicadores económicos (API mindicador.cl)
* Soporte para HTTPS local mediante certificado generado
* Este proyecto está desarrollado en Django, sin base de datos externa adicional (solo modelo Django).

El proyecto está desarrollado en Django + Flask, con Apache Pulsar como broker de eventos, siguiendo principios de microservicios y auditoría.

<br>

---

### 🐳 Microservicios

El proyecto NUAM incluye tres microservicios implementados en Flask. Dos de ellos consumen eventos de Apache Pulsar.

### 1️⃣ Microservicio de Indicadores Económicos (indicadores_service)

Puerto: 3000

Funcionalidad: Consume múltiples APIs externas de forma síncrona, específicamente mindicador.cl para indicadores financieros de Chile y Exchange Rate API (open.er-api.com) para obtener tasas de cambio internacionales, combinando ambas fuentes para calcular conversiones monetarias adicionales.para obtener indicadores económicos y exponerlos vía HTTP.
Adicionalmente, el servicio se integra a Apache Pulsar como consumidor, escuchando eventos del sistema de forma asíncrona para fines de monitoreo y extensibilidad.

<br>

Endpoints:

GET /indicadores

<br>

Devuelve:

* dolar: valor actual del dólar
* uf: valor actual de la UF
* tpm: Tasa de Política Monetaria
* clp_pen: conversión CLP → PEN
* clp_cop: conversión CLP → COP
* historico_dolar: últimos 10 días del dólar

<br>

**Integración con Apache Pulsar:**

Se conecta al broker Pulsar (pulsar://pulsar:6650)

Se suscribe al tópico:
```

persistent://public/default/indicadores
```

* Consume mensajes de manera continua en un hilo independiente
* Los eventos recibidos se procesan actualmente mediante salida por consola
* Esta integración permite reaccionar a eventos del sistema sin acoplar el servicio al backend principal

<br>

*Notas:*

* *La funcionalidad principal del servicio es síncrona (consulta HTTP).*
* *La integración con Pulsar es asíncrona, orientada a eventos.*
* *Actualmente el consumer no modifica el estado del servicio, pero habilita:*

	* *monitoreo*
	* *trazabilidad*
	* *ampliación futura (caché, alertas, métricas)*

<br>

### 2️⃣ Microservicio de Logs (logs_service)

Puerto: 3001

Rol arquitectónico: Auditoría y trazabilidad.

Funcionalidad:

* Consume eventos desde Apache Pulsar (suscriptor).
* Registra acciones reales del sistema.
* Expone los logs vía API REST.

Eventos procesados:
* Login exitoso / fallido
* Logout
* Creación, edición y eliminación de usuarios
* Creación, edición y eliminación de documentos

<br>

Endpoints:

GET /logs → Devuelve todos los eventos registrados

<br>

Formato de salida:

```
{
  "fecha": "2025-12-12T22:58:28",
  "mensaje": "Inicio de sesión exitoso: inacap (ID 7)"
}
```

*Notas:*
*Los logs se almacenan en memoria.*
*No interactúa directamente con Django.*
*Consume eventos vía Pulsar (modelo Pub/Sub).*

<br>

### 3️⃣ Microservicio de Notificaciones (notifications_service)

Puerto: 3002

Rol arquitectónico: Canal de alertas.

Funcionalidad:

* Consume los mismos eventos desde Apache Pulsar.
* Transforma eventos en notificaciones.
* Asocia cada notificación a un usuario (ej: admin).

<br> 

**Endpoints:**

GET /notifications

<br>

Formato de salida:

```
{
  "mensaje": "Documento editado: Informe Septiembre",
  "usuario": "admin"
}

```

*Notas:*
*No guarda timestamps (no es auditoría).*
*No persiste datos.*
*Consume eventos vía Pulsar.*

---

<br><br>

### 📖 **Manual de Usuario**

Consulta el archivo Manual de Usuario.pdf incluido en el repositorio para obtener una guía completa sobre el manejo de la interfaz y funcionalidades del sistema.


<br>

---

<br>

### **🏗 Arquitectura General**

```
                    ┌────────────────────┐
                    │       Django       │
                    │ API + Auth + CRUD  │
                    │  (Publisher)       │
                    └─────────┬──────────┘
                              │ Eventos
                              ▼
                    ┌────────────────────┐
                    │   Apache Pulsar    │
                    │   Broker Pub/Sub   │
                    │   6650 / 8080      │
                    └─────────┬──────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
┌────────────────┐   ┌────────────────┐   ┌─────────────────────┐
│ Logs Service   │   │ Notifications  │   │ Indicadores Service │
│ :3001          │   │ Service :3002  │   │ :3000               │
│ Auditoría      │   │ Alertas        │   │ Indicadores + APIs  │
└────────────────┘   └────────────────┘   └─────────┬───────────┘
                                                      │
                                     ┌────────────────┼────────────────┐
                                     ▼                ▼                ▼
                               mindicador.cl    open.er-api.com   (externas)

```


<br>

---

<br>

### **⚙️Tecnologías Utilizadas**
```
| Tecnología            | Uso                                    |
|-----------------------|----------------------------------------|
| Python 3.12           | Lenguaje principal                     |
| Django 5              | Backend, views, modelos, sesiones      |
| Django REST Framework | API REST                               |
| Apache Pulsar         | Broker Pub/Sub         			     |
| Docker                | Contenedores           		         |
| Bootstrap             | Estilos del frontend                   |
| HTTPS                 | Certificados locales 					 |

```
<br>

---

<br>

### **⚙️ Requisitos previos:**


* Python 3.12 o superior
* pip (administrador de paquetes de Python)
* Git
* Virtualenv
* Docker Desktop (Windows) / Docker Engine (Linux)
* Django 5.1.4 o superior (se instalará automáticamente desde requirements.txt)

<br>

---

<br><br>

### **🛠️ Instalación del Proyecto**


1\. Crea una carpeta para el proyecto
<br><br>

2\. Abre una terminal y accede a la carpeta creada, luego ejecuta:

```
git clone https://github.com/kiuiwi/nuam-ev4.git
```

```
cd nuam-ev4
```

<br>

3\. Crear y activar entorno virtual (venv):

Desde la misma carpeta del proyecto "nuam-ev4", ejecuta:


Windows:
```
py -m venv venv
```
```
venv\Scripts\activate
```
<br>

Linux/Mac:
```
python3 -m venv venv
```
```
source venv/bin/actívate
```

<br>

4\. Instala las dependencias de Python:

Windows:
```
py -m pip install -r requirements.txt
```


Linux:
```
pip3 install -r requirements.txt
```
<br>


5\. Construir y levantar los microservicios con Docker:

(en Windows abre Docker Desktop y asegúrate de que esté ejecutándose.)

```
docker-compose up --build
```
<br>

Esto inicia:

- Django
- Indicadores Service
- Logs Service
- Notification Service
- Pulsar (standalone)



<br><br>

6\. Acceder a los servicios:

Dashboard principal: 
http://localhost:8000



*Nota: Si los indicadores no aparecen, recargue la página.*

<br>

**Microservicios:**

Indicadores: 
http://localhost:3000/indicadores

Logs: 
http://localhost:3001/logs

Notificaciones: 
http://localhost:3002/notifications

<br>

---

### **👤 Login**

**Usuario Admin**

Usuario: inacap

Contraseña: 1234

<br>

**Usuario**

Usuario: juan.perez

Contraseña: 1234


<br>


**Superusuario Django**

Usuario: inacap

Contraseña: inacap123


<br>

---

<br>

### 🔍 Verificación del sistema Pub/Sub

Luego de ejecutar:

docker-compose up --build

<br>

1\. Realizar acciones en la app:

- Login
- Crear usuario
- Editar documento
- Logout

<br>

2\. Verificar consumidores via navegador:

Logs:  http://localhost:3001/logs

Notifications:  http://localhost:3002/notifications

<br>

3\. Verificar que Pulsar está funcionando directamente:
- Ver contenedores activos:

Abre **una segunda terminal** y ejecuta:

```
cd nuam-ev4
```

```
docker ps
```

*Debes ver algo como "nuam-ev4-pulsar1" en ejecucion* 

<br>

- Entrar al contenedor de Pulsar:

```
docker exec -it nuam-ev4-pulsar-1 /bin/bash
```



<br>

- Abrir un consumidor de prueba:

```
bin/pulsar-client consume persistent://public/default/test -s test-sub -n 0
```
<br>

- En una **tercera terminal**, enviar un mensaje de prueba:

```
cd nuam-ev4
```

```
docker exec -it nuam-ev4-pulsar-1 /pulsar/bin/pulsar-client produce persistent://public/default/test  -m "Hola NUAM"

```

<br>

- La **segunda terminal** debe mostrar:

```
----- got message -----
content: Hola NUAM

```

*Esto confirma que el broker funciona correctamente y que los mensajes pueden ser consumidos y producidos de manera independiente a los microservicios.*

<br>

4\. Ver mensajes en consola del servicio indicadores:

```
[PULSAR INDICADORES] Inicio de sesión exitoso...
```

<br><br>


---

<br><br>

### 📡 Sistema de Logs + Apache Pulsar (Pub/Sub)

📤 Publicación de eventos (Publisher)

Django actúa como productor de eventos, publicando mensajes en Apache Pulsar cada vez que ocurre una acción de negocio relevante dentro del sistema.

La publicación de eventos se realiza mediante la función publish_event(), ubicada en:

utils/pulsar_client.py


Cada evento representa una acción real del sistema y se envía al broker Pulsar siguiendo el modelo Publish/Subscribe, permitiendo que múltiples servicios reaccionen de forma desacoplada.

Eventos publicados por Django:

- Login exitoso
- Login fallido
- Cierre de sesión (Logout)
- Creación de usuarios
- Edición de usuarios
- Eliminación de usuarios
- Creación de documentos
- Edición de documentos
- Eliminación de documentos


#### Flujo de eventos:

1. Django publica el evento en Apache Pulsar (publish_event()).

2. Apache Pulsar distribuye el mensaje a los consumidores suscritos.

3. Los microservicios consumidores procesan el evento según su responsabilidad:

	- logs_service: registra auditoría.
	- notifications_service: genera notificaciones.
	- indicadores_service: escucha eventos para monitoreo/extensibilidad.


<br><br>


### **🌐 API REST (Django REST Framework)**


Expuesta mediante ViewSets:

* class UsuarioViewSet(viewsets.ModelViewSet)
* class PersonaViewSet(viewsets.ModelViewSet)
* class DocumentoViewSet(viewsets.ModelViewSet)
* class EventoLogViewSet(viewsets.ModelViewSet)


<br>


Endpoints reales de la API interna como JSON

(se puede acceder desde Menu admin):



http://localhost:8000/api/usuarios/

http://127.0.0.1:8000/api/personas/

http://127.0.0.1:8000/api/documentos/

http://localhost:8000/api/logs/


<br>


**Endpoints disponibles:**

/api/usuarios/	GET, POST	CRUD usuarios

/api/usuarios/<id>/	GET, PUT, DELETE	Operaciones sobre un usuario

/api/personas/	CRUD	Personas

/api/documentos/	CRUD	Documentos

/api/eventolog/	CRUD	Logs generados

<br>



**Swagger UI:**

interfaz web interactiva para explorar API REST

http://localhost:8000/swagger/



<br><br>



### **🌐 Integración con APIs Externas Indicadores Económicos**


El sistema integra APIs públicas externas a través del microservicio independiente Indicadores Service, encargado de centralizar la consulta de datos económicos y exponerlos al resto del sistema de forma síncrona.

Django no consume APIs externas directamente, sino que obtiene los datos mediante una llamada HTTP al microservicio, manteniendo una arquitectura desacoplada y escalable.



### 1️⃣ mindicador.cl (Chile)
Fuente oficial de indicadores económicos nacionales.

Se utiliza para obtener:

* Dólar (CLP)
* UF
* TPM (Tasa de Política Monetaria)
* Serie histórica del dólar

### 2️⃣ open.er-api.com (Exchange Rate API)
Servicio público de tasas de cambio internacionales.

Se utiliza para obtener:

* Conversión USD → PEN
* Conversión USD → COP

Cálculo derivado:

* CLP → PEN
* CLP → COP

<br>

**Microservicio responsable:**

Indicadores Service
Puerto: 3000

Función principal:

* Consultar APIs externas
* Normalizar los datos
* Exponerlos mediante un endpoint HTTP

<br>

Endpoint expuesto:

GET /indicadores

<br>

Datos entregados

* dolar: Valor actual del dólar en CLP
* uf: Valor actual de la UF
* tpm: Tasa de Política Monetaria
* clp_pen: Conversión CLP → PEN
* clp_cop: Conversión CLP → COP
* historico_dolar: Últimos 10 registros del dólar

<br>

#### Manejo de errores y resiliencia

El microservicio implementa:

- Timeout en llamadas HTTP externas

- Manejo de errores de conexión

- Validación de datos faltantes

- Fallback de histórico del dólar en caso de indisponibilidad

Esto evita que una falla externa afecte la disponibilidad del sistema principal.

<br>

#### Visualización en la aplicación:

Los datos de indicadores económicos se consumen desde Django y se muestran en las siguientes vistas:

- inicio.html
- menu_admin.html
- menu_usuario.html
- login.html



<br>

---

<br><br>

### **📁 Estructura del Proyecto**

```
/nuam.

|
├── app
│   ├── admin.py
│   ├── api\_views.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── serializers.py
│   │ 
│   ├── static
│   │   └── app
│   │       ├── nuam\_HD2.png
│   │       ├── nuam\_HD.png
│   │       └── styles.css
│   │ 
│   ├── templates
│   │   ├── app
│   │   │   ├── inicio.html
│   │   │   ├── login.html
│   │   │   ├── menu\_admin.html
│   │   │   └── menu\_usuario.html
│   │   │
│   │   ├── base.html
│   │   │
│   │   ├── documentos
│   │   │
│   │   │   ├── crear\_documento.html
│   │   │   ├── editar\_documento.html
│   │   │   ├── eliminar\_documento.html
│   │   │   └── lista\_documentos.html
│   │   │
│   │   ├── logs
│   │   │   └── lista\_logs.html
│   │   │
│   │   ├── registro
│   │   │   ├── crear\_registro.html
│   │   │   ├── editar\_registro.html
│   │   │   ├── eliminar\_registro.html
│   │   │   └── lista\_registros.html
│   │   │
│   │   └── usuarios
│   │       ├── crear\_usuario.html
│   │       ├── eliminar\_usuario.html
│   │       └── lista\_usuarios.html
│   │  
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── certificados
│   ├── cert.crt
│   ├── certificate.crt
│   ├── cert.key
│   ├── nuam.crt
│   ├── nuam.key
│   ├── private.key
│   └── request.csr
│     
│   
├── microservicios
│   ├── indicadores_service
│   │       ├── Dockerfile
│   │       ├── main.py
│   │       └── requirements.txt
│   │  
│   ├── log_service
│   │       ├── Dockerfile
│   │       ├── main.py
│   │       └── requirements.txt
│   │  
│   └── notification_service
│           ├── Dockerfile
│           ├── main.py
│           └── requirements.txt
│     
│
├── consumer.py
│
├── db.sqlite3
│
├── documentos
│   └── comprobante\_depositos.txt
│
├── manage.py
│
├── docker-compose.yml
│
├── Dockerfile
│
│
├── nuam
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── README.txt
├── requirements.txt
│
└── utils
    ├── pulsar_client.py
    └── services_client.py
```


<br>

---
<br>

### **🔐 Certificados**

**Certificados utilizados en el proyecto**:

* Certificado: nuam.crt

* Clave privada: nuam.key

* Ubicación: Carpeta certificados/ dentro del proyecto.

* Tipo: Auto-firmado (self-signed) para entorno de desarrollo.

* Generación: Se creó con OpenSSL

Nota: Este certificado no está emitido por una autoridad confiable, por lo que los navegadores mostrarán advertencias de seguridad.

<br>

**Archivos adicionales:**

* certificate.crt

* private.key

* request.csr (solicitud de firma de certificado)


<br>

---

<br>

### **🗂 Estructura de Modelos (Modelo de Datos)**

**El proyecto incluye:**

* Usuario
* Persona
* Documento
* DocumentoTipo
* UsuarioTipo
* EventoLog (logs generados por Pulsar)

<br>

**El CRUD depende de estas relaciones:**

UsuarioTipo 1 ──── N Usuario

Usuario 1 ──── 1 Persona

DocumentoTipo 1 ──── N Documento

Usuario 1 ──── N Documento



<br><br>

**👥 CRUD de Usuarios y Personas**

* Crear
* Editar
* Eliminar
* Listar

<br>

**Al crear o editar un usuario:**

* Se guarda el usuario con su Persona asociada.
* Se genera un evento Pulsar (publish_event()).
* Se registra un EventoLog en la base de datos.

<br>

**Flujo de creación**

* Usuario + Persona enviados por POST
* Validación de formularios
* Guardado en DB
* Pulsar produce evento
* EventoLog guarda en DB
* Redirige a la lista

<br>

**Vistas incluidas:**

* lista_registros
* crear_registro
* editar_registro
* eliminar_registro




<br><br>


**📄 CRUD de Documentos**

Funcionalidades:

* Subir archivo (request.FILES)
* Editar metadatos
* Eliminar documento
* Filtros (texto y tipo)
* Logs + eventos Pulsar

<br><br>

**Vistas:**

* lista_documentos
* crear_documento
* editar_documento
* eliminar_documento

<br>

**Cada operación:**

✔ Envía evento al broker
✔ Guarda EventoLog en la base de datos



<br><br>


**🔑 Autenticación y Perfiles de Usuario**

**Sistema de login flexible:**

1. Login desde tabla Usuario (username + password)
2. Login por email (tabla Persona)
3. Login del Administrador Django (authenticate())

<br>

**Roles:**

Administrador → acceso a menú admin

Usuario → acceso a menú usuario

<br>

**Ambos almacenados en:**

request.session["tipo"]
request.session["usuario_id"]


<br><br>






### **✨ Autores:**

Nombres: Sol Toledo, Camila Cruz, Alejandra Miranda

Carrera: Analista Programador

Institución: Inacap

Año: 2025

