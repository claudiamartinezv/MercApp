from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mercapp.models import Producto, Venta, DetalleVenta, Respaldo

print("🔧 Creando grupos y asignando permisos...")

# ----- GRUPOS -----
grupos = {
    "Administrador": Group.objects.get_or_create(name="Administrador")[0],
    "Vendedor": Group.objects.get_or_create(name="Vendedor")[0],
    "Supervisor": Group.objects.get_or_create(name="Supervisor")[0],
    "Auditor": Group.objects.get_or_create(name="Auditor")[0],
}

# ----- PERMISOS BÁSICOS POR MODELO -----
ct_producto = ContentType.objects.get_for_model(Producto)
ct_venta = ContentType.objects.get_for_model(Venta)
ct_detalle = ContentType.objects.get_for_model(DetalleVenta)
ct_respaldo = ContentType.objects.get_for_model(Respaldo)

# Permisos personalizados del modelo Venta
perm_ver_reportes = Permission.objects.get(codename="can_view_reports")
perm_borrar_ventas = Permission.objects.get(codename="can_delete_sales")

# Permisos personalizados del respaldo
perm_respaldo_admin = Permission.objects.get(codename="can_manage_backups")
perm_ver_auditoria = Permission.objects.get(codename="can_view_audit_logs")


# --------------------------------------------------------
# 🔥 ADMINISTRADOR → TODOS LOS PERMISOS
# --------------------------------------------------------
grupos["Administrador"].permissions.set(Permission.objects.all())


# --------------------------------------------------------
# 🛒 VENDEDOR → CRUD productos + crear ventas + agregar detalles
# --------------------------------------------------------
permisos_vendedor = Permission.objects.filter(
    content_type__in=[ct_producto, ct_venta, ct_detalle],
    codename__in=[
        "view_producto", "add_producto", "change_producto",
        "view_venta", "add_venta",
        "view_detalleventa", "add_detalleventa"
    ]
)

grupos["Vendedor"].permissions.set(permisos_vendedor)


# --------------------------------------------------------
# 📊 SUPERVISOR → ver productos, ventas, reportes
# --------------------------------------------------------
permisos_supervisor = Permission.objects.filter(
    content_type__in=[ct_producto, ct_venta],
    codename__in=[
        "view_producto",
        "view_venta",
    ]
)

grupos["Supervisor"].permissions.set(list(permisos_supervisor) + [perm_ver_reportes])


# --------------------------------------------------------
# 🔍 AUDITOR → solo lectura + auditoría
# --------------------------------------------------------
permisos_auditor = Permission.objects.filter(
    codename__startswith="view_"
)

grupos["Auditor"].permissions.set(list(permisos_auditor) + [perm_ver_auditoria])


print("✅ Grupos creados y permisos asignados correctamente.")
