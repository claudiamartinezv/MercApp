from .permissions import es_admin, es_vendedor


def role_flags(request):
    """Add role boolean flags to template context.

    Provides `es_admin` and `es_vendedor` so templates can show admin-only UI
    when the user belongs to the Administrador group or is superuser.
    """
    user = getattr(request, 'user', None)
    return {
        'es_admin': es_admin(user) if user is not None else False,
        'es_vendedor': es_vendedor(user) if user is not None else False,
    }
