from decimal import Decimal, ROUND_HALF_UP
from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

User = get_user_model()


# Normalización de decimales -------------------------
def quantize_decimal(value, places=2):
    if value is None:
        return None
    q = Decimal(10) ** -places
    return Decimal(value).quantize(q, rounding=ROUND_HALF_UP)


# Timestamp base ------------------------------------
class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ---------------------------------------------------
# PRODUCTO
# ---------------------------------------------------
class Producto(TimestampedModel):
    codigo = models.CharField(max_length=50, blank=True, null=True, unique=True)
    nombre = models.CharField(max_length=150)
    categoria = models.CharField(max_length=100, blank=True)
    precio = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    stock_minimo = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        default_permissions = ('add', 'change', 'delete', 'view')
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['nombre']),
        ]

    def __str__(self):
        return f"{self.nombre} (stock: {self.stock})"


# ---------------------------------------------------
# VENTA
# ---------------------------------------------------
class Venta(TimestampedModel):
    METODO_PAGO_CHOICES = [
        ("EFECTIVO", "Efectivo"),
        ("DEBITO", "Débito"),
        ("CREDITO", "Crédito"),
        ("TRANSFERENCIA", "Transferencia"),
    ]

    fecha = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, default="EFECTIVO")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="ventas")
    anulada = models.BooleanField(default=False)
    motivo_anulacion = models.TextField(blank=True, null=True)
    anulada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas_anuladas')
    fecha_anulacion = models.DateTimeField(null=True, blank=True)

    stock_aplicado = models.BooleanField(default=False, editable=False)

    class Meta:
        ordering = ['-fecha']
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        default_permissions = ('add', 'change', 'delete', 'view')
        permissions = [
            ("can_view_reports", "Can view advanced reports"),
            ("can_delete_sales", "Can delete or annul sales"),
        ]

    def __str__(self):
        return f"Venta #{self.id} - {self.fecha.date()}"

    def recalcular_total(self):
        total = sum(quantize_decimal(d.subtotal) for d in self.detalles.all())
        self.total = quantize_decimal(total)
        return self.total

    def aplicar_stock(self):
        if self.stock_aplicado:
            return
        with transaction.atomic():
            for detalle in self.detalles.select_related('producto').all():
                prod = detalle.producto
                if prod.stock - detalle.cantidad < 0:
                    raise ValidationError(
                        f"Stock insuficiente para {prod.nombre}. Disponible: {prod.stock}, requerido: {detalle.cantidad}"
                    )
                prod.stock -= detalle.cantidad
                prod.save()
            self.stock_aplicado = True
            self.save(update_fields=['stock_aplicado'])

    def restaurar_stock(self):
        if not self.stock_aplicado:
            return
        with transaction.atomic():
            for detalle in self.detalles.select_related('producto').all():
                prod = detalle.producto
                prod.stock += detalle.cantidad
                prod.save()
            self.stock_aplicado = False
            self.save(update_fields=['stock_aplicado'])


# ---------------------------------------------------
# DETALLE DE VENTA
# ---------------------------------------------------
class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="detalles_venta")
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, editable=False)

    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"
        default_permissions = ('add', 'change', 'delete', 'view')

    def clean(self):
        if self.cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor que 0.")
        if self.precio_unitario < Decimal('0.00'):
            raise ValidationError("El precio unitario no puede ser negativo.")

    def save(self, *args, **kwargs):
        self.precio_unitario = quantize_decimal(self.precio_unitario)
        self.subtotal = quantize_decimal(self.cantidad * self.precio_unitario)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad} (venta {self.venta_id})"


# ---------------------------------------------------
# RESPALDO
# ---------------------------------------------------
class Respaldo(models.Model):
    TIPO_CHOICES = [
        ("AUTOMATICO", "Automático"),
        ("MANUAL", "Manual"),
    ]

    fecha = models.DateTimeField(default=timezone.now)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    ubicacion = models.FileField(upload_to='respaldos/', blank=True, null=True)
    archivo_path = models.CharField(max_length=1024, blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name="respaldos")

    class Meta:
        verbose_name = "Respaldo"
        verbose_name_plural = "Respaldos"
        default_permissions = ('add', 'change', 'delete', 'view')
        permissions = [
            ("can_manage_backups", "Can manage backups"),
            ("can_view_audit_logs", "Can view audit logs"),
        ]

    def __str__(self):
        return f"Respaldo {self.tipo} - {self.fecha}"


# ---------------------------------------------------
# SEÑALES
# ---------------------------------------------------
@receiver(post_save, sender=DetalleVenta)
def detalleventa_post_save(sender, instance, created, **kwargs):
    venta = instance.venta
    venta.total = venta.recalcular_total()
    venta.save(update_fields=['total'])


@receiver(post_delete, sender=DetalleVenta)
def detalleventa_post_delete(sender, instance, **kwargs):
    venta = instance.venta
    if venta.stock_aplicado:
        with transaction.atomic():
            prod = instance.producto
            prod.stock += instance.cantidad
            prod.save()
            venta.stock_aplicado = False
            venta.save(update_fields=['stock_aplicado'])

    venta.total = venta.recalcular_total()
    venta.save(update_fields=['total'])


@receiver(pre_save, sender=Venta)
def venta_pre_save(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        previous = Venta.objects.get(pk=instance.pk)
    except Venta.DoesNotExist:
        return

    if not previous.anulada and instance.anulada:
        if previous.stock_aplicado:
            with transaction.atomic():
                previous.restaurar_stock()
                previous.anulada = True
                previous.fecha_anulacion = instance.fecha_anulacion or timezone.now()
                previous.motivo_anulacion = instance.motivo_anulacion
                previous.anulada_por = instance.anulada_por
