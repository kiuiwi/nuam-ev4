import requests

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.forms.models import model_to_dict

from .models import Usuario, Persona, Documento, EventoLog
from .forms import UsuarioForm, PersonaForm, DocumentoForm

from django.contrib.auth.decorators import login_required
from functools import wraps


# --------------------------------------------------------------------
# Helpers para microservicios
# --------------------------------------------------------------------

def microservicio_logs(mensaje: str):
    try:
        requests.post("http://logs_service:3001/log", json={"mensaje": mensaje}, timeout=3)
    except Exception:
        pass



def microservicio_notificaciones(mensaje: str):
    try:
        requests.post("http://notifications_service:3002/notify", json={"mensaje": mensaje, "usuario": "admin"}, timeout=3)
    except Exception:
        pass



# --------------------------------------------------------------------
# Middleware simple de login
# --------------------------------------------------------------------

def login_requerido(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("usuario_id"):
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper


# --------------------------------------------------------------------
# Indicadores vía microservicio
# --------------------------------------------------------------------

def obtener_indicadores():
    datos = {
        "tpm_actual": None,
        "tc_clp_pen": None,
        "tc_clp_cop": None,
        "valor_dolar": None,
        "valor_uf": None,
        "fechas": [],
        "valores": [],
        "error_api": None,
    }

    try:
        response = requests.get("http://indicadores_service:3000/indicadores", timeout=4)
        if response.status_code == 200:
            data = response.json()

            datos["valor_dolar"] = data.get("dolar")
            datos["valor_uf"] = data.get("uf")
            datos["tpm_actual"] = data.get("tpm")
            datos["tc_clp_pen"] = data.get("clp_pen")
            datos["tc_clp_cop"] = data.get("clp_cop")

            # Histórico para gráficos
            h = data.get("historico_dolar", [])
            datos["fechas"] = [x["fecha"][:10] for x in h]
            datos["valores"] = [x["valor"] for x in h]

        else:
            datos["error_api"] = "Error al conectarse al microservicio"
    except Exception as e:
        datos["error_api"] = f"Error microservicio: {str(e)}"

    return datos

# --------------------------------------------------------------------
# HOME
# --------------------------------------------------------------------

def inicio(request):
    context = obtener_indicadores()

    persona = None
    usuario_id = request.session.get("usuario_id")

    if usuario_id:
        usuario = Usuario.objects.filter(id_usuario=usuario_id).first()
        if usuario:
            persona = Persona.objects.filter(usuario=usuario).first()

    context["persona"] = persona

    return render(request, "app/inicio.html", context)


# --------------------------------------------------------------------
# CRUD USUARIO + PERSONA
# --------------------------------------------------------------------

def lista_registros(request):
    if request.session.get("tipo") != "Administrador":
        return redirect("inicio")

    personas = Persona.objects.select_related("usuario").all()
    return render(request, "registro/lista_registros.html", {"personas": personas})


def crear_registro(request):
    if request.session.get("tipo") != "Administrador":
        return redirect("inicio")

    if request.method == "POST":
        usuario_form = UsuarioForm(request.POST)
        persona_form = PersonaForm(request.POST)

        if usuario_form.is_valid() and persona_form.is_valid():
            usuario = usuario_form.save()
            persona = persona_form.save(commit=False)
            persona.usuario = usuario
            persona.save()

            mensaje = f"Usuario creado: {usuario.id_usuario} - {usuario.nombre_usuario} | Usuario ejecutor: {request.session.get('usuario_id')}"

            microservicio_logs(mensaje)
            microservicio_notificaciones(mensaje)

            EventoLog.objects.create(
                tipo="Usuario",
                mensaje=mensaje
            )

            return redirect("lista_registros")

    else:
        usuario_form = UsuarioForm()
        persona_form = PersonaForm()

    return render(request, "registro/crear_registro.html", {
        "usuario_form": usuario_form,
        "persona_form": persona_form
    })


def editar_registro(request, usuario_id):
    if request.session.get("tipo") != "Administrador":
        return redirect("inicio")

    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    persona = get_object_or_404(Persona, usuario=usuario)

    if request.method == "POST":
        usuario_form = UsuarioForm(request.POST, instance=usuario)
        persona_form = PersonaForm(request.POST, instance=persona)

        if usuario_form.is_valid() and persona_form.is_valid():
            usuario_form.save()
            persona_form.save()

            mensaje = f"Usuario editado: {usuario.id_usuario} - {usuario.nombre_usuario} | Usuario ejecutor: {request.session.get('usuario_id')}"

            microservicio_logs(mensaje)
            microservicio_notificaciones(mensaje)

            EventoLog.objects.create(
                tipo="Usuario",
                mensaje=mensaje
            )

            return redirect("lista_registros")

    else:
        usuario_form = UsuarioForm(instance=usuario)
        persona_form = PersonaForm(instance=persona)

    return render(request, "registro/editar_registro.html", {
        "usuario_form": usuario_form,
        "persona_form": persona_form
    })


def eliminar_registro(request, usuario_id):
    if request.session.get("tipo") != "Administrador":
        return redirect("inicio")

    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)

    if request.method == "POST":
        nombre_backup = usuario.nombre_usuario
        id_backup = usuario.id_usuario
        usuario.delete()

        mensaje = f"Usuario eliminado: {id_backup} - {nombre_backup} | Usuario ejecutor: {request.session.get('usuario_id')}"

        microservicio_logs(mensaje)
        microservicio_notificaciones(mensaje)

        EventoLog.objects.create(
            tipo="Usuario",
            mensaje=mensaje
        )

        return redirect("lista_registros")

    return render(request, "registro/eliminar_registro.html", {"usuario": usuario})


# --------------------------------------------------------------------
# CRUD DOCUMENTOS
# --------------------------------------------------------------------

def lista_documentos(request):
    if not request.session.get("usuario_id"):
        return redirect("login")

    query = request.GET.get('q')
    tipo = request.GET.get('tipo')

    documentos = Documento.objects.all()

    if query:
        documentos = documentos.filter(
            Q(documento_nombre__icontains=query) |
            Q(usuario__nombre_usuario__icontains=query) |
            Q(documento_tipo__documento_tipo__icontains=query)
        )

    if tipo and tipo != "":
        documentos = documentos.filter(documento_tipo__id_documento_tipo=tipo)

    return render(request, "documentos/lista_documentos.html", {
        "documentos": documentos,
        "query": query,
        "tipo": tipo,
    })


def crear_documento(request):
    if not request.session.get("usuario_id"):
        return redirect("login")

    if request.method == "POST":
        form = DocumentoForm(request.POST, request.FILES)

        if form.is_valid():
            doc = form.save()
            mensaje = f"Documento creado: {doc.id_documento} - {doc.documento_nombre}"

            microservicio_logs(mensaje)
            microservicio_notificaciones(mensaje)

            EventoLog.objects.create(
                tipo="Documento",
                mensaje=mensaje
            )

            return redirect("lista_documentos")

    else:
        form = DocumentoForm()

    return render(request, "documentos/crear_documento.html", {"form": form})


def editar_documento(request, documento_id):
    if not request.session.get("usuario_id"):
        return redirect("login")

    documento = get_object_or_404(Documento, id_documento=documento_id)

    if request.method == "POST":
        form = DocumentoForm(request.POST, request.FILES, instance=documento)

        if form.is_valid():
            doc = form.save()
            mensaje = f"Documento editado: {doc.id_documento} - {doc.documento_nombre}"

            microservicio_logs(mensaje)
            microservicio_notificaciones(mensaje)

            EventoLog.objects.create(
                tipo="Documento",
                mensaje=mensaje
            )

            return redirect("lista_documentos")

    else:
        form = DocumentoForm(instance=documento)

    return render(request, "documentos/editar_documento.html", {"form": form})


def eliminar_documento(request, documento_id):
    if not request.session.get("usuario_id"):
        return redirect("login")

    documento = get_object_or_404(Documento, id_documento=documento_id)

    if request.method == "POST":
        nombre_backup = documento.documento_nombre
        id_backup = documento.id_documento
        documento.delete()

        mensaje = f"Documento eliminado: {id_backup} - {nombre_backup}"

        microservicio_logs(mensaje)
        microservicio_notificaciones(mensaje)

        EventoLog.objects.create(
            tipo="Documento",
            mensaje=mensaje
        )

        return redirect("lista_documentos")

    return render(request, "documentos/eliminar_documento.html", {"documento": documento})



# LOGS DE EVENTOS (PULSAR)

def lista_logs(request):
    if request.session.get("tipo") != "Administrador":
        return redirect("inicio")
    logs = EventoLog.objects.order_by('-fecha')
    return render(request, 'logs/lista_logs.html', {'logs': logs})


def api_logs(request):
    if request.session.get("tipo") != "Administrador":
        return redirect("inicio")
    logs = EventoLog.objects.order_by('-fecha')
    data = [model_to_dict(log) for log in logs]
    return JsonResponse(data, safe=False)



# LOGIN + MENÚS

def login_view(request):
    indicadores = obtener_indicadores()

    if request.method == "POST":
        login_input = request.POST.get("login", "").strip()
        password = request.POST.get("password", "").strip()

        usuario = None

        # LOGIN TABLA Usuario
        try:
            usuario = Usuario.objects.get(
                nombre_usuario=login_input,
                contrasena=password
            )
        except Usuario.DoesNotExist:
            usuario = None

        # LOGIN POR EMAIL EN Persona
        if usuario is None:
            try:
                persona = Persona.objects.get(email=login_input)
                if persona.usuario.contrasena == password:
                    usuario = persona.usuario
            except Persona.DoesNotExist:
                usuario = None

        # LOGIN FALLIDO
        if usuario is None:
            mensaje = f"Intento de inicio de sesión fallido: '{login_input}'"
            microservicio_logs(mensaje)
            microservicio_notificaciones(mensaje)
            EventoLog.objects.create(tipo="Login", mensaje=mensaje)

            return render(request, "app/login.html", {
                "error": "Credenciales inválidas",
                **indicadores
            })

        # LOGIN EXITOSO → USUARIO PERSONALIZADO
        request.session["usuario_id"] = usuario.id_usuario
        request.session["tipo"] = usuario.usuario_tipo.usuario_tipo

        mensaje = f"Inicio de sesión exitoso: {usuario.nombre_usuario} (ID {usuario.id_usuario})"
        microservicio_logs(mensaje)
        microservicio_notificaciones(mensaje)
        EventoLog.objects.create(tipo="Login", mensaje=mensaje)

        return redirect("inicio")

    # GET → mostrar login con indicadores
    return render(request, "app/login.html", indicadores)


# MENUS

def menu_admin(request):
    if request.session.get("tipo") != "Administrador":
        return redirect("login")

    context = obtener_indicadores()
    return render(request, "app/menu_admin.html", context)




def menu_usuario(request):
    if request.session.get("tipo") != "Usuario":
        return redirect("login")

    context = obtener_indicadores()
    return render(request, "app/menu_usuario.html", context)



def logout_view(request):
    usuario_id = request.session.get("usuario_id")
    tipo = request.session.get("tipo")

    if usuario_id:
        mensaje = f"Cierre de sesión: Usuario ID {usuario_id}, tipo {tipo}"

        # Enviar a microservicios
        microservicio_logs(mensaje)
        microservicio_notificaciones(mensaje)

        # Guardar en base de datos
        EventoLog.objects.create(
            tipo="Login",
            mensaje=mensaje
        )

    # Limpiar la sesión
    request.session.flush()

    return redirect("login")
