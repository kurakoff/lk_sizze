from django.test import TestCase, Client, TransactionTestCase
from django.contrib.auth.models import User
from content.models import Project, Prototype, ProjectPermissions, ShareProject
from rest_framework.test import APITestCase
from rest_framework import status


def createUser(username, email, password):
    user = User.objects.create(username=username, email=email)
    user.set_password(password)
    user.save()
    return user

def craeteProject(name, user):
    prototype = Prototype.objects.create(device_name='Айфон', width=1080, height=720,
                                         image='/randomname', image_hover='randomrane')
    project = Project.objects.create(name=name, user=user, prototype=prototype)
    return project

def craetePermission(name):
    permission = ProjectPermissions.objects.create(permission=name)
    return permission


class ShareProjectTest(APITestCase):
    def data(self):
        user_1 = createUser(username='user_1', email='user_1@gmail.com', password='349561')
        user_2 = createUser(username='user_2', email='user_2@gmail.com', password='349561')
        user_3 = createUser(username='user_3', email='user_3@gmail.com', password='349561')
        user_2
        craeteProject('To all user', user=user_1)
        craeteProject('To second user', user=user_1)
        craeteProject('To me', user=user_1)
        permission_list = ['read', 'edit', 'delete']
        for item in permission_list:
            craetePermission(item)

    def test_post_share_project_1_to_all(self):
        '''Пост запрос на предоставление прав 1 проекту для всех от автора'''
        self.data()
        url = '/api/editor/project/1/share/'
        data = {
            "permissions": [1, 2],
            "project_user_id": 1,
            "user": None
        }
        self.client.login(username='user_1@gmail.com', password='349561')
        response = self.client.post(url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ShareProject.objects.count(), 1)
        self.assertTrue(ShareProject.objects.get(permissions=1))
        self.assertTrue(ShareProject.objects.get(permissions=2))

    def test_post_share_project_2_to_user_2(self):
        '''Пост запрос на предоставление прав 2 проекту для 2 юзера от автора'''
        self.data()
        url = '/api/editor/project/2/share/'
        data = {
            "permissions": [1],
            "project_user_id": 1,
            "user": 2
        }
        self.client.login(username='user_1@gmail.com', password='349561')
        response = self.client.post(url, data, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ShareProject.objects.count(), 1)
        self.assertTrue(ShareProject.objects.get(permissions=1))

    def test_get_share_project_1_to_all(self):
        '''Пользователь делает запрос на всем доступный проект'''
        self.data()
        url = '/api/editor/project/2/share/'
        self.client.login(username='user_1@gmail.com', password='349561')
        data = {
            "permissions": [1, 2],
            "project_user_id": 1,
            "user": None
        }
        self.client.post(url, data, format='json', follow=True)
        get = self.client.get(url)
        self.assertEqual(get.status_code, status.HTTP_200_OK)
        self.assertEqual(ShareProject.objects.count(), 1)

    def test_get_share_project_2_to_user_2(self):
        '''Пользователь с правами на проект 2 делает запрос и получает 200'''
        self.data()
        get_url = '/api/editor/project/2'
        url = '/api/editor/project/2/share/'
        data = {
            "permissions": [1],
            "project_user_id": 1,
            "user": 2
        }

        self.client.login(username='user_1@gmail.com', password='349561')
        self.client.post(url, data, format='json', follow=True)
        self.client.logout()

        self.client.login(username='user_2@gmail.com', password='349561')
        get = self.client.get(get_url)
        self.assertEqual(get.status_code, status.HTTP_200_OK)
        self.assertEqual(ShareProject.objects.count(), 1)

    def test_get_share_project_2_to_user_3(self):
        '''Пользователь без прав делая запрос на 2 проект получает 403'''
        self.data()
        get_url = '/api/editor/project/2'
        self.client.login(username='user_3@gmail.com', password='349561')
        get = self.client.get(get_url)
        self.assertEqual(get.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_share_project_3_to_author(self):
        '''Автор делая запрос на свой 2 проект получает 200'''
        self.data()
        get_url = '/api/editor/project/3'
        self.client.login(username='user_1@gmail.com', password='349561')
        get = self.client.get(get_url)
        self.assertEqual(get.status_code, status.HTTP_200_OK)
