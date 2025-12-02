
from django.urls import path
from . import views

urlpatterns = [
    # Página de inicio (dashboard)
    path("", views.inicio, name="inicio"),

    path("productos/", views.lista_productos, name="lista_productos"),
    path("productos/nuevo/", views.crear_producto, name="crear_producto"),
    path("productos/<int:producto_id>/editar/", views.editar_producto, name="editar_producto"),
    path("productos/<int:producto_id>/eliminar/", views.eliminar_producto, name="eliminar_producto"),

    path("ventas/nueva/", views.registrar_venta, name="registrar_venta"),
    path("ventas/<int:venta_id>/", views.detalle_venta_view, name="detalle_venta"),
    path("ventas/<int:venta_id>/anular/", views.anular_venta, name="anular_venta"),

    path("reportes/ventas/", views.reporte_ventas, name="reporte_ventas"),
    # Vendedores management
    path("vendedores/nuevo/", views.crear_vendedor, name="crear_vendedor"),
    path("usuarios/nuevo/", views.crear_usuario, name="crear_usuario"),
    # User management (admin)
    path("usuarios/", views.lista_usuarios, name="lista_usuarios"),
    path("usuarios/<int:user_id>/toggle/", views.toggle_usuario_activo, name="toggle_usuario_activo"),
    path("usuarios/<int:user_id>/reset_password/", views.resetear_password, name="resetear_password"),
    path("usuarios/<int:user_id>/eliminar/", views.eliminar_usuario, name="eliminar_usuario"),
]
