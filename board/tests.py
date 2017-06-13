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


class TestCreateUserProfile(TestCase):
    def test_valid_data(self):
        """Test we the form is validated."""
        form = UserForm({'firstname': "firstname",
                         'lastname': "lastname",
                         'username': "username",
                         'email': "user@example.com",
                         })
        self.assertTrue(form.is_valid())