from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Create Administrator and Vendedor groups and assign appropriate permissions'

    def handle(self, *args, **options):
        # Administrator: give all permissions
        admin_group, created = Group.objects.get_or_create(name='Administrador')
        if created:
            self.stdout.write('Created group Administrador')
        # assign all permissions
        all_perms = Permission.objects.all()
        admin_group.permissions.set(all_perms)
        self.stdout.write(f'Assigned {all_perms.count()} permissions to Administrador')

        # Vendedor: limited permissions (explicit mapping)
        vendedor_group, created = Group.objects.get_or_create(name='Vendedor')
        if created:
            self.stdout.write('Created group Vendedor')

        # Define a mapping of app_label.model -> list of codenames we want for vendedores
        permisos_map = {
            # allow vendedores to create and view ventas
            ('mercapp', 'venta'): ['add_venta', 'view_venta'],
            # allow vendedores to view productos but not add/change/delete
            ('mercapp', 'producto'): ['view_producto'],
            # optionally allow viewing sale details if the model exists
            ('mercapp', 'detalleventa'): ['view_detalleventa'],
        }

        perms_to_add = []
        for (app_label, model), codenames in permisos_map.items():
            try:
                ct = ContentType.objects.get(app_label=app_label, model=model)
                found = list(Permission.objects.filter(content_type=ct, codename__in=codenames))
                if found:
                    perms_to_add += found
                else:
                    self.stdout.write(f'No permissions found for {app_label}.{model} -> {codenames}')
            except ContentType.DoesNotExist:
                self.stdout.write(f'ContentType not found for {app_label}.{model}')

        # Apply (replace) the permissions for the vendedor group
        vendedor_group.permissions.set(perms_to_add)
        self.stdout.write(f'Assigned {len(perms_to_add)} permissions to Vendedor')

        self.stdout.write(self.style.SUCCESS('Roles setup completed'))
