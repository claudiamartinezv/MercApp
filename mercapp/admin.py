
from django.contrib import admin
from .models import Producto, Venta, DetalleVenta, Respaldo


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "categoria", "precio", "stock", "stock_minimo", "activo")
    search_fields = ("nombre", "categoria")
    list_filter = ("activo", "categoria")


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("id", "fecha", "total", "metodo_pago", "usuario")
    list_filter = ("metodo_pago", "fecha")
    inlines = [DetalleVentaInline]


@admin.register(Respaldo)
class RespaldoAdmin(admin.ModelAdmin):
    list_display = ("id", "fecha", "tipo", "ubicacion", "usuario")
    list_filter = ("tipo", "fecha")
