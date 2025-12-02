from django.test import TestCase
from django.contrib.auth import get_user_model


class AuthFlowTest(TestCase):
    def setUp(self):
        User = get_user_model()
        # create a test admin
        self.username = 'admin'
        self.email = 'admin@example.com'
        self.password = 'adminpass123'
        if not User.objects.filter(username=self.username).exists():
            User.objects.create_superuser(self.username, self.email, self.password)

    def test_login_and_logout_flow(self):
        # login
        logged = self.client.login(username=self.username, password=self.password)
        self.assertTrue(logged, 'Could not log in with test credentials')

        # access a protected page
        resp = self.client.get('/productos/')
        # should be 200 for logged-in admin
        self.assertEqual(resp.status_code, 200)

        # perform logout via POST
        resp = self.client.post('/accounts/logout/', follow=True)
        # After logout we expect to be redirected to the login page
        self.assertEqual(resp.status_code, 200)
        # final redirected path should include accounts/login
        self.assertIn('/accounts/login/', resp.request.get('PATH_INFO', resp.request.get('PATH_INFO', '')))
        # final page should be the login page (we ensure PATH_INFO includes the login path)
        self.assertIn('/accounts/login/', resp.request.get('PATH_INFO', ''))
