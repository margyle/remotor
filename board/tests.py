from django.contrib.auth.models import User
from django.test import LiveServerTestCase, TestCase
from django.test.client import Client

from .forms import UserForm


class TestRegistration(LiveServerTestCase):
    """Tests response codes for views with HTTP methods."""
    fixtures = ['users.json']

    def setUp(self):
        self.client = Client()

    def test_index(self):
        """Test we get a response from /index/."""
        response = self.client.get('/index/')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/index/')
        self.assertEqual(response.status_code, 405)

    def test_signup(self):
        """Test we get a response from /signup/."""
        response = self.client.get('/signup/')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/signup/')
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        """Test we get a response from /login/."""
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Login' in response.content)
        self.client.login(username='xxx', password="xxxxyyyy")
        response = self.client.get('/login/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue('Logout' in response.content)

    def test_logout(self):
        """Test we get a response from /logout/."""
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Login' in response.content)
        response = self.client.post('/logout/')
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Login' in response.content)


class TestCreateUser(TestCase):
    """Test a form to add a user behaves as expected."""
    def test_valid_data(self):
        """Test the form is validated."""
        form = UserForm({'username': "username",
                         'password1': 'xxxxyyyy',
                         'password2': 'xxxxyyyy',
                         'email': "user@example.com",
                         })
        self.assertTrue(form.is_valid())
        form.save()
        user = User.objects.first()
        self.assertEqual(user.username, "username")
        self.assertTrue(user.password)
        self.assertEqual(user.email, "user@example.com")
        self.assertTrue(user.profile)

    def test_no_data(self):
        """Test the form is not validated if blank."""
        form = UserForm({})
        self.assertFalse(form.is_valid())


class TestEditProfile(LiveServerTestCase):
    fixtures = ['users.json']

    def setUp(self):
        self.client = Client()

    def test_profile(self):
        """Test we get a response from /profile/."""
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Login' in response.content)
        self.client.login(username='xxx', password="xxxxyyyy")
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)

    def test_add_required_techs(self):
        self.client.login(username='xxx', password="xxxxyyyy")
        data = {'required_techs': 'django,python'}
        response = self.client.post('/profile/', data=data)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('django' in response.content)
        self.assertTrue('python' in response.content)

    def test_add_excluded_techs(self):
        self.client.login(username='xxx', password="xxxxyyyy")
        data = {'excluded_techs': 'django,python'}
        response = self.client.post('/profile/', data=data)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('django' in response.content)
        self.assertTrue('python' in response.content)

