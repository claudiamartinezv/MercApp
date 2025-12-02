from django.test import TestCase


class ViewsTest(TestCase):
    def test_lista_productos_requires_login(self):
        """GET /productos/ debe redirigir al login si no hay sesión."""
        resp = self.client.get('/productos/')
        # Debe redirigir a login (302) y la ubicación debe contener /accounts/login/
        self.assertEqual(resp.status_code, 302)
        location = resp.headers.get('Location', '')
        self.assertIn('/accounts/login/', location)
