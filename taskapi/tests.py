from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Task, Profile


class AuthTests(APITestCase):

    def test_register_user(self):
        data = {'username': 'alice', 'password': 'pass123', 'role': 'developer'}
        response = self.client.post('/api/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_returns_token(self):
        User.objects.create_user(username='bob', password='pass123')
        response = self.client.post('/api/token/', {'username': 'bob', 'password': 'pass123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_wrong_password_fails(self):
        User.objects.create_user(username='carol', password='right')
        response = self.client.post('/api/token/', {'username': 'carol', 'password': 'wrong'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TaskTests(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_user(username='admin1', password='pass123')
        Profile.objects.create(user=self.admin, role='admin')
        self.dev = User.objects.create_user(username='dev1', password='pass123')
        Profile.objects.create(user=self.dev, role='developer')

        r1 = self.client.post('/api/token/', {'username': 'admin1', 'password': 'pass123'})
        self.admin_token = r1.data['access']

        r2 = self.client.post('/api/token/', {'username': 'dev1', 'password': 'pass123'})
        self.dev_token = r2.data['access']

    def auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_create_task(self):
        self.auth(self.admin_token)
        response = self.client.post('/api/tasks/', {'title': 'Fix bug', 'status': 'todo', 'priority': 'high'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_tasks(self):
        self.auth(self.admin_token)
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_token_blocked(self):
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_by_status(self):
        self.auth(self.admin_token)
        Task.objects.create(title='T1', status='todo', priority='low', created_by=self.admin)
        Task.objects.create(title='T2', status='done', priority='high', created_by=self.admin)
        response = self.client.get('/api/tasks/filter/?status=todo')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_developer_sees_only_own_tasks(self):
        self.auth(self.dev_token)
        Task.objects.create(title='Admin Task', status='todo', priority='low', created_by=self.admin)
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.data['count'], 0)