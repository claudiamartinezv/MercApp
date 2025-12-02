import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Sum, F
from django.db.models.deletion import ProtectedError
from django.forms import modelformset_factory
from django import forms

from .models import Producto, Venta, DetalleVenta, Respaldo
from .forms import ProductoForm, VentaForm, DetalleVentaForm, VendedorCreationForm, UsuarioCreationForm, AnulacionForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .permissions import es_admin, es_vendedor

logger = logging.getLogger('mercapp')

@login_required
def inicio(request):
    user = request.user
    hoy = timezone.localdate()

    ventas_hoy = Venta.objects.filter(fecha__date=hoy)

    # El vendedor solo ve sus ventas (el admin ve todas)
    if es_vendedor(user) and not es_admin(user):
        ventas_hoy = ventas_hoy.filter(usuario=user)

    total_hoy = ventas_hoy.aggregate(total=Sum('total'))['total'] or 0

    productos_bajo_stock = Producto.objects.filter(
        activo=True,
        stock__lte=F('stock_minimo')
    )

    contexto = {
        'ventas_hoy': ventas_hoy,
        'total_hoy': total_hoy,
        'productos_bajo_stock': productos_bajo_stock,
        'es_admin': es_admin(user),
        'es_vendedor': es_vendedor(user),
    }

    return render(request, 'mercapp/inicio.html', contexto)


@login_required
@user_passes_test(es_admin)
def lista_productos(request):
    productos = Producto.objects.filter(activo=True)
    return render(request, 'mercapp/lista_productos.html', {'productos': productos})


@login_required
@user_passes_test(es_admin)
def crear_producto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto creado correctamente.")
            logger.info(f"Producto creado por {request.user.username}")
            return redirect('lista_productos')
        else:
            # provide feedback about why the form failed
            errors = form.errors.as_json()
            logger.warning(f"Error al crear producto por {request.user.username}: {errors}")
            messages.error(request, "El formulario contiene errores. Revísalos y vuelve a intentar.")
    else:
        form = ProductoForm()
    return render(request, 'mercapp/producto_form.html', {'form': form, 'titulo': 'Crear producto'})


@login_required
@user_passes_test(es_admin)
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == "POST":
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado correctamente.")
            logger.info(f"Producto {producto.id} actualizado por {request.user.username}")
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'mercapp/producto_form.html', {'form': form, 'titulo': 'Editar producto'})


@login_required
@user_passes_test(es_admin)
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == "POST":
        logger.info(f"Producto {producto.id} eliminado por {request.user.username}")
        producto.delete()
        messages.success(request, "Producto eliminado correctamente.")
        return redirect('lista_productos')
    return render(request, 'mercapp/producto_confirm_delete.html', {'producto': producto})


@login_required
@user_passes_test(lambda u: es_admin(u) or es_vendedor(u))
def registrar_venta(request):
    DetalleFormSet = modelformset_factory(
        DetalleVenta,
        form=DetalleVentaForm,
        extra=1,
        can_delete=False
    )

    if request.method == "POST":
        venta_form = VentaForm(request.POST)
        detalle_formset = DetalleFormSet(request.POST, queryset=DetalleVenta.objects.none())

        if venta_form.is_valid() and detalle_formset.is_valid():
            venta = venta_form.save(commit=False)
            venta.usuario = request.user
            venta.save()

            for form in detalle_formset:
                detalle = form.save(commit=False)
                if detalle.producto and detalle.cantidad:
                    detalle.venta = venta
                    detalle.save()

            venta.recalcular_total()
            logger.info(f"Venta {venta.id} registrada por {request.user.username}")
            messages.success(request, "Venta registrada correctamente.")
            return redirect('detalle_venta', venta_id=venta.id)

    else:
        venta_form = VentaForm()
        detalle_formset = DetalleFormSet(queryset=DetalleVenta.objects.none())

    contexto = {
        'venta_form': venta_form,
        'formset': detalle_formset,
        'productos': Producto.objects.filter(activo=True),
    }
    return render(request, 'mercapp/registrar_venta.html', contexto)


@login_required
@user_passes_test(lambda u: es_admin(u) or es_vendedor(u))
def detalle_venta_view(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    detalles = DetalleVenta.objects.filter(venta=venta)
    return render(request, 'mercapp/detalle_venta.html', {'venta': venta, 'detalles': detalles})


@login_required
@user_passes_test(es_admin)
def anular_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    if request.method == 'POST':
        form = AnulacionForm(request.POST)
        if form.is_valid():
            motivo = form.cleaned_data['motivo']
            # mark as anulada
            venta.anulada = True
            venta.motivo_anulacion = motivo
            venta.anulada_por = request.user
            venta.fecha_anulacion = timezone.now()
            venta.save()
            logger.info(f"Venta {venta.id} anulada por {request.user.username}: {motivo}")
            messages.success(request, f'Venta {venta.id} anulada correctamente.')
            return redirect('detalle_venta', venta_id=venta.id)
    else:
        form = AnulacionForm()

    return render(request, 'mercapp/confirmar_anulacion.html', {'venta': venta, 'form': form})


@login_required
@user_passes_test(lambda u: es_admin(u) or es_vendedor(u))
def reporte_ventas(request):
    ventas = Venta.objects.all()

    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    if fecha_desde:
        ventas = ventas.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        ventas = ventas.filter(fecha__date__lte=fecha_hasta)

    # Acceso a reportes:
    # - Administrador ve todas las ventas.
    # - Cualquier usuario con permiso 'mercapp.can_view_reports' puede ver todas.
    # - Vendedor (grupo) ve sólo sus propias ventas.
    if not (es_admin(request.user) or request.user.has_perm('mercapp.can_view_reports')):
        # si no es admin ni tiene permiso de ver reportes, restringir a sus ventas
        ventas = ventas.filter(usuario=request.user)

    total_vendido = ventas.aggregate(total=Sum('total'))['total'] or 0
    stock_bajo = Producto.objects.filter(stock__lte=F('stock_minimo'))

    # Reporte mejorado: productos más vendidos (top 10)
    top_productos = (
        DetalleVenta.objects
        .values('producto__nombre')
        .annotate(cantidad_total=Sum('cantidad'), ventas_total=Sum('subtotal'))
        .order_by('-cantidad_total')[:10]
    )

    contexto = {
        'ventas': ventas,
        'total_vendido': total_vendido,
        'stock_bajo': stock_bajo,
        'top_productos': top_productos,
    }

    return render(request, 'mercapp/reporte_ventas.html', contexto)


@login_required
@user_passes_test(lambda u: es_admin(u))
def crear_vendedor(request):
    """Permite al admin crear un usuario con rol 'Vendedor' y asignar permisos básicos."""
    if request.method == 'POST':
        form = VendedorCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data.get('email')
            password = form.cleaned_data['password1']

            User = get_user_model()
            if User.objects.filter(username=username).exists():
                messages.error(request, 'El usuario ya existe')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                # ensure group exists
                group, created = Group.objects.get_or_create(name='Vendedor')

                # assign some sensible permissions to vendedores (add and view ventas)
                try:
                    ct = ContentType.objects.get_for_model(Venta)
                    perms = Permission.objects.filter(content_type=ct, codename__in=['add_venta','view_venta'])
                    for p in perms:
                        group.permissions.add(p)
                except Exception:
                    # ignore if permissions not found
                    pass

                user.groups.add(group)
                messages.success(request, f'Vendedor {username} creado y asignado al grupo Vendedor')
                return redirect('lista_productos')
    else:
        form = VendedorCreationForm()

    return render(request, 'mercapp/vendedor_form.html', {'form': form})


@login_required
@user_passes_test(es_admin)
def crear_usuario(request):
    """Vista para que un admin cree un usuario y le asigne un rol (Vendedor o Administrador).

    Reglas asumidas:
    - Cualquier usuario con `es_admin` puede crear usuarios con rol 'vendedor'.
    - Sólo los superusers pueden crear usuarios con rol 'administrador' (prevención de elevación accidental).
    """
    User = get_user_model()

    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data.get('email')
            password = form.cleaned_data['password1']
            rol = form.cleaned_data.get('rol')

            if User.objects.filter(username=username).exists():
                messages.error(request, 'El usuario ya existe')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)

                if rol == 'administrador':
                    # allow only superusers to create Administrador accounts
                    if not request.user.is_superuser:
                        user.delete()
                        messages.error(request, 'Sólo un superusuario puede crear administradores desde la UI')
                        return redirect('lista_usuarios')
                    group, _ = Group.objects.get_or_create(name='Administrador')
                else:
                    group, _ = Group.objects.get_or_create(name='Vendedor')

                # assign group permissions are handled by setup_roles; ensure group exists
                user.groups.add(group)
                messages.success(request, f'Usuario {username} creado y asignado al rol {rol}')
                return redirect('lista_usuarios')
    else:
        form = UsuarioCreationForm()

    return render(request, 'mercapp/usuario_form.html', {'form': form})


@login_required
@user_passes_test(es_admin)
def lista_usuarios(request):
    User = get_user_model()
    usuarios = User.objects.all().order_by('username')
    return render(request, 'mercapp/lista_usuarios.html', {'usuarios': usuarios})


@login_required
@user_passes_test(es_admin)
def toggle_usuario_activo(request, user_id):
    User = get_user_model()
    usuario = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        # Prevent an admin from deactivating their own account via this action
        if request.user.id == usuario.id:
            messages.error(request, 'No puedes desactivar tu propia cuenta desde aquí.')
            return redirect('lista_usuarios')

        usuario.is_active = not usuario.is_active
        usuario.save()
        if usuario.is_active:
            messages.success(request, f'Usuario {usuario.username} reactivado.')
        else:
            messages.warning(request, f'Usuario {usuario.username} desactivado. Nota: un usuario desactivado no podrá iniciar sesión.')
    return redirect('lista_usuarios')


class ResetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label='Nueva contraseña')


@login_required
@user_passes_test(es_admin)
def resetear_password(request, user_id):
    User = get_user_model()
    usuario = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            usuario.set_password(form.cleaned_data['password'])
            usuario.save()
            messages.success(request, f'Contraseña actualizada para {usuario.username}')
            return redirect('lista_usuarios')
    else:
        form = ResetPasswordForm()
    return render(request, 'mercapp/reset_password.html', {'form': form, 'usuario': usuario})


@login_required
@user_passes_test(es_admin)
def eliminar_usuario(request, user_id):
    """Eliminar un usuario (confirmación). Se evita que un admin se elimine a sí mismo desde aquí."""
    User = get_user_model()
    usuario = get_object_or_404(User, id=user_id)

    # Prevent deleting self
    if request.user.id == usuario.id:
        messages.error(request, 'No puedes eliminar tu propia cuenta desde aquí.')
        return redirect('lista_usuarios')

    # Only superusers can delete other superusers
    if usuario.is_superuser and not request.user.is_superuser:
        messages.error(request, 'Sólo un superusuario puede eliminar a otro superusuario.')
        return redirect('lista_usuarios')

    if request.method == 'POST':
        username = usuario.username
        try:
            usuario.delete()
            messages.success(request, f'Usuario {username} eliminado correctamente.')
            logger.info(f'Usuario {username} eliminado por {request.user.username}')
        except ProtectedError as e:
            # Si el usuario está referenciado por objetos protegidos (p.ej. Ventas),
            # evitamos la excepción y en su lugar desactivamos la cuenta para
            # preservar integridad referencial y datos históricos.
            usuario.is_active = False
            usuario.save()
            messages.warning(request, (
                f'No se pudo eliminar al usuario {username} porque tiene objetos relacionados protegidos (p.ej. ventas). '
                'Se ha desactivado la cuenta en su lugar.'
            ))
            logger.warning(f'Intento de eliminar usuario {username} falló por ProtectedError; cuenta desactivada por {request.user.username}.')
        return redirect('lista_usuarios')

    return render(request, 'mercapp/usuario_confirm_delete.html', {'usuario': usuario})
