
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from .models import DetalleVenta


@receiver(post_save, sender=DetalleVenta)
def actualizar_stock_y_total(sender, instance, created, **kwargs):
    if not created:
        return

    producto = instance.producto
    if producto.stock < instance.cantidad:
        raise ValidationError(
            f"No hay stock suficiente para {producto.nombre}. "
            f"Stock actual: {producto.stock}, solicitado: {instance.cantidad}"
        )

    producto.stock -= instance.cantidad
    producto.save()

    instance.venta.recalcular_total()
