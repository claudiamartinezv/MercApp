from django.contrib.auth.models import Group


def es_admin(user):
    """Usuario administrador: se considera admin si es superuser o pertenece
    al grupo 'Administrador'. Esto permite gestionar administradores desde
    la UI (usuarios de grupo) sin requerir superuser.
    """
    if not getattr(user, 'is_authenticated', False):
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name='Administrador').exists()


def es_vendedor(user):
    """Usuario vendedor: pertenece al grupo 'Vendedor'.

    Evita depender únicamente de "no ser admin" porque un usuario puede no
    ser superuser y tampoco vendedor.
    """
    if not getattr(user, 'is_authenticated', False):
        return False
    return user.groups.filter(name='Vendedor').exists()
