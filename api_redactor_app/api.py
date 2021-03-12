import base64, json, os, random, string, googleapiclient, reversion
from mimetypes import guess_extension, guess_type

from django.conf import settings
from django.urls import path
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.db.models import Q, F

from gphotospy import authorize
from gphotospy.media import Media
from gphotospy.album import Album

from rest_framework import generics, viewsets, permissions, status, response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from reversion.models import Version, Revision

from .serializers import UserElementSerializer, ProjectSerializer, PrototypeSerializer, ScreenSerializer,\
    ShareProjectSerializer, SharedProjectDeleteUserSerializer, ShareProjectBaseSerializer, OtherProjectSerializer
from content.models import Screen, Project, Prototype, UserElement, UserProfile, Project, Category, SharedProject
from .permissions import IsAuthor, EditPermission, DeletePermission, ReadPermission
from .helpers.is_auth import IsAuthenticated

CLIENT_SECRET_FILE = f"{settings.BASE_DIR}/google_secret.json"
print(settings.BASE_DIR)
service = authorize.init(CLIENT_SECRET_FILE)


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


class InitProject(APIView):
    def get(self, request, project, *args, **kwargs):
        response = []
        project = get_object_or_404(Project, pk=project)
        prototype_pk = project.prototype.pk
        categories = Category.objects.filter(categoryprototype__prototype=prototype_pk)
        for category in categories:
            category_j = {}
            category_j['title'] = category.title
            category_j['two_in_row'] = category.two_in_row
            elements = category_j['elements'] = []
            icons = category_j['icons'] = []
            response.append(category_j)
            for element in category.get_elements_on_prototype(prototype_pk).all():
                j_element = {}
                j_element['title'] = element.title
                j_element['layout'] = [element.light_layout, element.dark_layout]
                j_element['image'] = [str(element.light_image), str(element.dark_image)]
                j_element['active'] = element.active
                if 'icons_' in category.title:
                    icons.append(j_element)
                else:
                    elements.append(j_element)
        return JsonResponse({'categories': response})


class ScreenView(APIView):

    def get(self, request, project_id, screen_id=None, action=None):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse({'message': 'Project not found', "result": False})

        if screen_id:
            try:
                screen = project.screen_set.get(id=screen_id)
            except Screen.DoesNotExist:
                return JsonResponse({'message': 'Screen not found', "result": False})

            if action == 'duplicate':
                screen = Screen.objects.filter(id=screen_id, project=project_id).first()
                screen.id = None
                screen.save()
                serializer = ScreenSerializer(screen)
            else:
                serializer = ScreenSerializer(screen)
            return JsonResponse({'screen': serializer.data, "result": True})
        else:
            screens = project.screen_set
            serializer = ScreenSerializer(screens, many=True)
        return JsonResponse({'screens': serializer.data, "result": True})

    def put(self, request, project_id, screen_id=None):
        try:
            project = Project.objects.get(id=project_id, user=request.user)
        except Project.DoesNotExist:
            return JsonResponse({'message': 'Project not found', "result": False})
        try:
            screen = project.screen_set.get(id=screen_id)
        except Screen.DoesNotExist:
            return JsonResponse({'message': 'Screen not found', "result": False})
        with reversion.create_revision():
            payload = json.loads(request.body)
            if payload.get('title'): screen.title = payload['title']
            if payload.get('layout'): screen.layout = payload['layout']
            if payload.get('width'): screen.width = payload['width']
            if payload.get('height'): screen.height = payload['height']
            if payload.get('background_color'): screen.background_color = payload['background_color']
            if payload.get('position'): screen.position = payload['position']
            screen.save()
            serializer = ScreenSerializer(screen)
            reversion.set_user(request.user)
            reversion.set_comment(
                f"ТУТ БУДЕТ ИМЯ ЭЛЕМЕНТА"
            )
        return JsonResponse({'screen': serializer.data, "result": True})

    def post(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id, user=request.user)
        except Project.DoesNotExist:
            return JsonResponse({'message': 'Project not found', "result": False})

        payload = json.loads(request.body)
        screens = Screen.objects.filter(project=project_id)
        screen = Screen(
            title=payload['title'],
            project=project,
            layout="",
            width=project.prototype.width,
            height=project.prototype.height,
            position=(len(screens) + 1)
        )
        screen.save()
        serializer = ScreenSerializer(screen)
        return JsonResponse({'screen': serializer.data, "result": True})

    def delete(self, request, project_id, screen_id=None):

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse({'message': 'Project not found', "result": False})
        try:
            screen = project.screen_set.get(id=screen_id)
        except Screen.DoesNotExist:
            return JsonResponse({'message': 'Screen not found', "result": False})

        screen.delete()
        screens = project.screen_set.all()
        serializer = ScreenSerializer(screens, many=True)

        return JsonResponse({'result': True, 'screen': serializer.data})


class ProjectApiView(APIView):

    def get(self, request, project_id=None):
        if project_id:
            try:
                project_permissions = SharedProject.objects.filter(Q(to_user=request.user, project=project_id) |
                                                                   Q(all_users=True, project=project_id))
                for project_permission in project_permissions:
                    if "read" in project_permission.permission:
                        project = Project.objects.filter(id=project_id).all()
                        serializer = ProjectSerializer(project, many=True)
                        for i in serializer.data:
                            project_permissions = project.filter(
                                share_project__to_user=request.user, share_project__project=i['id']).\
                                values('share_project__permission')
                            all_users = project.filter(
                                share_project__project=i['id'], share_project__all_users=True).\
                                values('share_project__all_users')
                            all_permissions = project.filter(
                                share_project__all_users=True, share_project__project=i['id']).\
                                values('share_project__permission')
                            if project_permission:
                                i['to_user'] = {"permissions": (project_permissions[0]["share_project__permission"])}
                            else:
                                i['to_user'] = False
                            if all_users:
                                i['all_users'] = {"permissions": all_permissions[0]["share_project__permission"]}
                            else:
                                i['all_users'] = False
                            i['is_author'] = False
                        return JsonResponse({'project': serializer.data})
            except:
                pass
            try:
                project = Project.objects.filter(id=project_id, user=request.user)
                serializer = ProjectSerializer(project, many=True)
                for i in serializer.data:
                    all_users = project.filter(
                        share_project__project=project_id, share_project__all_users=True). \
                        values('share_project__all_users')
                    all_permissions = project.filter(
                        share_project__all_users=True, share_project__project=project_id). \
                        values('share_project__permission')
                    i['to_user'] = False
                    if all_users:
                        i['all_users'] = {"permissions": all_permissions[0]["share_project__permission"]}
                    else:
                        i['all_users'] = False
                    i['is_author'] = True
                    return JsonResponse({'project': serializer.data})
            except Project.DoesNotExist:
                return JsonResponse({'message': 'Project not found', "result": False})
        else:
            project = Project.objects.filter(user=request.user).all()
            serializer = ProjectSerializer(project, many=True)
            return JsonResponse({'project': serializer.data})

    def post(self, request):
        payload = json.loads(request.body)
        try:
            prototype = Prototype.objects.get(id=payload['prototype_id'])
        except Project.DoesNotExist:
            return JsonResponse({'message': 'Prototype not found', "result": False})
        project = Project()
        project.prototype = prototype
        project.name = payload['name']
        if payload.get('colors'):
            project.colors = payload['colors']
        project.user = request.user
        project.save()
        screen = Screen(
            title='first_page',
            project=project,
            width=project.prototype.width,
            height=project.prototype.height,
            position=1
        )
        screen.save()
        serializer = ProjectSerializer(project)
        data = serializer.data
        data['screen'] = ScreenSerializer(screen).data
        return JsonResponse({'project': data, "result": True})

    def put(self, request, project_id):
        payload = json.loads(request.body)
        try:
            project = Project.objects.get(id=project_id, user=request.user)
        except Project.DoesNotExist:
            return JsonResponse({'message': 'Project not found', "result": False})

        if payload.get('name'):
            project.name = payload['name']
        if 'colors' in payload.keys():
            project.colors = payload['colors']

        project.save()
        serializer = ProjectSerializer(project)
        return JsonResponse({'project': serializer.data, "result": True})

    def delete(self, request, project_id):

        try:
            project = Project.objects.get(id=project_id, user=request.user)
        except Project.DoesNotExist:
            return JsonResponse({'message': 'Project not found', "result": False})
        project.delete()
        return JsonResponse({'result': True})


class PrototypeApiView(generics.ListAPIView):
    serializer_class = PrototypeSerializer
    queryset = Prototype.objects.all()


class UserElementApiView(APIView):

    def get(self, request, project_id):
        user = request.user
        try:
            project_permission = SharedProject.objects.get(Q(to_user=request.user, project=project_id) |
                                                           Q(all_users=True, project=project_id))
            if "read" in project_permission.permission:
                project = Project.objects.get(id=project_id)
                elements = UserElement.objects.filter(project=project).all()
                serialize = UserElementSerializer(elements, many=True)
                return JsonResponse({"elements": serialize.data, "result": True})
        except:
            pass
        try:
            project = Project.objects.get(id=project_id, user=user)
        except Project.DoesNotExist:
            return JsonResponse({'message': f'Project for user {user.username} not found', "result": False})

        elements = UserElement.objects.filter(project=project).all()
        serialize = UserElementSerializer(elements, many=True)
        return JsonResponse({"elements": serialize.data, "result": True})

    def post(self, request, project_id):
        user = request.user
        payload = json.loads(request.body)

        if not payload.get('title'):
            return JsonResponse({"message": 'Missing title', "result": False})

        try:
            project = Project.objects.get(id=project_id, user=user)
        except Project.DoesNotExist:
            return JsonResponse({'message': 'Project not found', "result": False})

        element = UserElement(title=payload['title'], project=project)
        if payload.get('layout'):
            element.layout = payload['layout']
        element.save()
        serialize = UserElementSerializer(element)
        return JsonResponse({"elements": serialize.data, "result": True})

    def put(self, request, project_id, element_id):
        user = request.user

        try:
            project = Project.objects.get(id=project_id, user=user)
        except Project.DoesNotExist:
            return JsonResponse({'message': 'Project not found', "result": False})

        try:
            element = UserElement.objects.get(id=element_id, project=project)
        except UserElement.DoesNotExist:
            return JsonResponse({'message': 'Element not found', "result": False})

        payload = json.loads(request.body)

        if payload.get('title'):
            element.title = payload['title']
        if payload.get('layout'):
            element.layout = payload['layout']
        element.save()
        serialize = UserElementSerializer(element)
        return JsonResponse({"elements": serialize.data, "result": True})

    def delete(self, request, project_id, element_id):
        user = request.user

        try:
            project = Project.objects.get(id=project_id, user=user)
        except Project.DoesNotExist:
            return JsonResponse({'message': 'Project not found', "result": False})

        try:
            element = UserElement.objects.get(id=element_id, project=project)
        except UserElement.DoesNotExist:
            return JsonResponse({'message': 'Element not found', "result": False})
        element.delete()
        elements = UserElement.objects.filter(project=project).all()
        serialize = UserElementSerializer(elements, many=True)
        return JsonResponse({"result": True, "elements": serialize.data})


class GoogleImageView(APIView):

    def post(self, request):
        payload = json.loads(request.body)
        try:
            user_profile = UserProfile.objects.get(user_id=request.user.id)
        except UserProfile.DoesNotExist:
            user_profile = UserProfile(user=request.user)
        print(user_profile)

        album_manager = Album(service)
        media_manager = Media(service)
        if not bool(user_profile.google_album_id):
            new_album = album_manager.create(f'user#{request.user.id}')
            album_id = new_album.get("id")
            user_profile.google_album_id = album_id
            user_profile.save()

        data = payload['image'].split('base64,')[1].replace(' ', '+')
        ext = guess_extension(guess_type("data:image/png;base64,")[0])

        img_data = base64.b64decode(data)
        file = f'{settings.BASE_DIR}/{get_random_string(10)}{ext}'
        with open(file, 'wb') as f:
            f.write(img_data)

        media_manager.stage_media(file)
        os.remove(file)

        img_id = media_manager.batchCreate(album_id=user_profile.google_album_id)[0]['mediaItem']['id']
        img_url = media_manager.get(img_id)['baseUrl']

        return JsonResponse({"result": True, "img_id": img_id, "img_url": img_url})

    def delete(self, request):
        payload = json.loads(request.body)
        id_photo = payload['image_id']

        album_manager = Album(service)

        error = None
        user_profile = UserProfile.objects.get(user_id=request.user.id)
        try:
            album_manager.batchRemoveMediaItems(album_id=user_profile.google_album_id, items=[id_photo])
        except googleapiclient.errors.HttpError as e:
            print(e)
            error = str(e)
        return JsonResponse({'result': True, "error": error})


class ScreenCopyView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            screen = Screen.objects.get(project_id=kwargs["project_id"], id=kwargs["screen_id"])
            sceens = Screen.objects.filter(project_id=kwargs["project_id"])
            copy_screen = Screen.objects.create(
                title="Copy " + screen.title,
                layout=screen.layout,
                project=screen.project,
                last_change=screen.last_change,
                height=screen.height,
                width=screen.width,
                background_color=screen.background_color,
                position=(len(sceens) + 1)
            )
            copy_screen.save
            copy_screen_serializer = ScreenSerializer(copy_screen)
            return JsonResponse(copy_screen_serializer.data)
        except:
            return JsonResponse({"result": False, "message": "Screen not found"}, status=status.HTTP_404_NOT_FOUND)


class ProjectCopyView(APIView):
    permission_classes = [IsAuthor | EditPermission]

    '''Копирование проекта'''
    def copy_project(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
        except:
            return JsonResponse({'result': False, 'error': 'Project not found'})
        copy = Project.objects.create(
            name=('Copy ' + project.name),
            user=request.user,
            prototype=project.prototype,
            colors=project.colors
        )
        copy.save()
        return copy

    def copy_element(self, copy, project_id):
        elements = UserElement.objects.filter(project_id=project_id)
        if elements.count() > 0:
            for element in elements:
                copy_element = UserElement.objects.create(
                    title=element.title,
                    layout=element.layout,
                    project_id=copy.id
                )
                copy_element.save()
            copy_elements = UserElement.objects.filter(project_id=copy.id)
            copy_element_serializer = UserElementSerializer(copy_elements, many=True)
            return copy_element_serializer.data
        else:
            pass

    def copy_screen(self, copy, project_id):
        screens = Screen.objects.filter(project_id=project_id)
        if screens.count() > 0:
            for screen in screens:
                copy_screen = Screen.objects.create(
                    title=screen.title,
                    layout=screen.layout,
                    project=copy,
                    last_change=screen.last_change,
                    height=screen.height,
                    width=screen.width,
                    background_color=screen.background_color,
                    position=screen.position
                )
                copy_screen.save
            copy_screens = Screen.objects.filter(project_id=copy.id)
            copy_screen_serializer = ScreenSerializer(copy_screens, many=True)
            return copy_screen_serializer.data
        else:
            pass

    def post(self, request, *args, **kwargs):
        copy = self.copy_project(request=request, project_id=kwargs['project_id'])
        copy_element = self.copy_element(copy=copy, project_id=kwargs['project_id'])
        copy_screen = self.copy_screen(copy=copy, project_id=kwargs['project_id'])
        try:
            copy_serializer = ProjectSerializer(copy, many=False)
            return JsonResponse({'result': True, 'copy_project': copy_serializer.data,
                                 'copy_element': copy_element, 'copy_screen': copy_screen})
        except:
            return copy


class ShareProjectAllView(APIView):
    permission_classes = [IsAuthor]

    def post(self, request, *args, **kwargs):
        serializer = ShareProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        all_users = request.data.get('all_users')
        print("All users is " + all_users)
        if all_users == "False":
            to_user = serializer.validated_data['to_user']
            share_project = SharedProject.objects.filter(project=kwargs['project_id'], to_user=to_user)
            if len(share_project) > 0:
                return JsonResponse({'result': False, 'message': 'This project has already been shared'})
        if all_users == "True":
            if request.user.is_superuser or request.user.is_staff:
                serializer.validated_data['to_user'] = None
                share_project = SharedProject.objects.filter(project=kwargs['project_id'], all_users=True)
                if len(share_project) > 0:
                    return JsonResponse({'result': False, 'message': 'This project has already been shared'})
            else:
                return JsonResponse({'result': False, 'message': 'You are not superuser'},
                                    status=status.HTTP_403_FORBIDDEN)
        if request.data.get('to_user') == request.user.email:
            return JsonResponse({'result': False, 'message': "You cant share the project with yourself"})
        serializer.save(project_id=kwargs['project_id'], from_user=request.user)
        msg_html = render_to_string('mail/Share.html', {'to_user': serializer.data['to_user'],
                                                        'from_user': serializer.data['from_user'],
                                                        'project': serializer.data['project']
                                                        })
        send_mail(
            f"Shared project with you",
            msg_html,
            getattr(settings, "EMAIL_HOST_USER"),
            [serializer.data['to_user']],
            html_message=msg_html,
            fail_silently=True
        )
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        shared_projects = SharedProject.objects.filter(project=kwargs['project_id'])
        serializer = ShareProjectSerializer(shared_projects, many=True)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)

    def delete(self, requset, *args, **kwargs):
        serializer = SharedProjectDeleteUserSerializer(data=requset.data)
        serializer.is_valid(raise_exception=True)
        all_users = requset.data.get('all_users')
        print("All users is " + all_users)
        if all_users == 'True':
            shared_project = SharedProject.objects.filter(
                project=kwargs['project_id'], all_users=serializer.data['all_users']
            )
        elif serializer.data.get('to_user'):
            shared_project = SharedProject.objects.filter(
                project=kwargs['project_id'], to_user=serializer.data['to_user']
            )
        else:
            shared_project = SharedProject.objects.filter(project=kwargs['project_id'])
        if len(shared_project) > 0:
            shared_project.delete()
        else:
            return JsonResponse({"result": False, "message": "project permission not found"},
                                status=status.HTTP_200_OK)
        return JsonResponse({"result": True, "message": "All rights to the project have been removed"},
                            status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        serializer = ShareProjectBaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        all_users = request.data.get('all_users')
        print("All users is " + all_users)
        if request.data.get('to_user') == request.user:
            return JsonResponse({'result': False, 'message': "You cant share the project with yourself"})
        if (all_users is False) or (all_users == "False"):
            shared_project = SharedProject.objects.get(to_user=serializer.data['to_user'],
                                                       project=kwargs['project_id'])
            shared_project.permission = serializer.data['permission']
        else:
            serializer.validated_data['to_user'] = None
            shared_project = SharedProject.objects.get(all_users=True, project=kwargs['project_id'])
            shared_project.permission = serializer.data['permission']
        shared_project.save()
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)


class UserShareProjectsView(viewsets.ModelViewSet):
    serializer_class = OtherProjectSerializer
    queryset = SharedProject.objects.none()

    def list(self, request, *args, **kwargs):
        project = Project.objects.filter(Q(share_project__to_user=request.user.email)
                                         | Q(share_project__all_users=True)).distinct()
        serializer = self.get_serializer(project, many=True)
        for i in serializer.data:
            project_permissions = project.filter(share_project__to_user=request.user,
                                                 share_project__project=i['id']).values('share_project__permission')
            all_users = project.filter(share_project__project=i['id'],
                                       share_project__all_users=True).values('share_project__all_users')
            all_permissions = project.filter(share_project__all_users=True,
                                             share_project__project=i['id']).values('share_project__permission')
            if project_permissions:
                i['to_user'] = {"permissions": (project_permissions[0]["share_project__permission"])}
            else:
                i['to_user'] = False
            if all_users:
                i['all_users'] = {"permissions": all_permissions[0]["share_project__permission"]}
            else:
                i['all_users'] = False
        return JsonResponse({"project": serializer.data}, status=status.HTTP_200_OK, safe=False)


class UserShareProjectDeleteView(viewsets.ModelViewSet):

    serializer_class = SharedProjectDeleteUserSerializer
    queryset = SharedProject.objects.none()
    permission_classes = [DeletePermission]

    def delete(self, request, *args, **kwargs):
        serializer = SharedProjectDeleteUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        shared_project = SharedProject.objects.filter(project=kwargs['project_id'], to_user=request.user)
        if len(shared_project) > 0:
            shared_project.delete()
            return JsonResponse({"result": True, "message": "All rights to the project have been removed"},
                                status=status.HTTP_200_OK)
        else:
            return JsonResponse({"result": False, "message": "project permission not found"},
                                status=status.HTTP_200_OK)


class ScreenHistory(APIView):
    def get(self, request, project_id, screen_id):
        screen = Screen.objects.get(id=screen_id)
        versions = Version.objects.get_for_object(screen)
        data = versions.values('pk', date_time=F('revision__date_created'), user=F('revision__user__username')
                               ).order_by('revision__date_created').reverse()[:50]
        return response.Response({"data": data})


class ScreenVersionAll(APIView):
    def get(self, request, *args, **kwargs):
        try:
            v = Version.objects.all()
            data = []
            for i in v:
                data.append(i.field_dict)
            return response.Response({"past screens": data})
        except:
            return JsonResponse({"message": "Version not found", "result": False})


class ScreenVersion(APIView):

    def get(self, requset, *args, **kwargs):
        try:
            v = Version.objects.get(id=kwargs['version_id'])
            return response.Response({"data": v.field_dict})
        except:
            return JsonResponse({"message": "Version not found", "result": False})

    def put(self, request, *args, **kwargs):
        try:
            v = Version.objects.get(id=kwargs['version_id'])
            v = v.field_dict
            screen = Screen.objects.get(id=kwargs['screen_id'])
            screen.title = v['title']
            screen.layout = v['layout']
            screen.width = v['width']
            screen.height = v['height']
            screen.background_color = v['background_color']
            screen.position = v['position']
            screen.save()
            serializer = ScreenSerializer(screen)
            return JsonResponse({"screen": serializer.data, "result": True})
        except:
            return JsonResponse({"message": "Version not found", "result": False})
