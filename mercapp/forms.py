
from django import forms
from django.forms import formset_factory
from .models import Producto, Venta, DetalleVenta

from django import forms
from django.contrib.auth import get_user_model


class VendedorCreationForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Las contraseñas no coinciden')
        return cleaned


class UsuarioCreationForm(VendedorCreationForm):
    ROLE_CHOICES = [
        ('vendedor', 'Vendedor'),
        ('administrador', 'Administrador'),
    ]

    rol = forms.ChoiceField(choices=ROLE_CHOICES, initial='vendedor', label='Rol')

    def clean(self):
        cleaned = super().clean()
        # additional validation could go here
        return cleaned


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["codigo", "nombre", "categoria", "precio", "stock", "stock_minimo", "activo"]


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ["metodo_pago"]


class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ["producto", "cantidad", "precio_unitario"]


DetalleVentaFormSet = formset_factory(DetalleVentaForm, extra=3, min_num=1, validate_min=True)


class AnulacionForm(forms.Form):
    motivo = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), label='Motivo de anulación', required=True)
