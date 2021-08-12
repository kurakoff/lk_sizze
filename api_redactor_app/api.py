import base64, json, os, random, string, googleapiclient, reversion, datetime, requests
from mimetypes import guess_extension, guess_type
from typing import Union

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.db.models import Q, F

from gphotospy import authorize
from gphotospy.media import Media
from gphotospy.album import Album

from rest_framework import generics, viewsets, status, response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from reversion.models import Version, Revision

from .serializers import UserElementSerializer, ProjectSerializer, PrototypeSerializer, ScreenSerializer,\
    ShareProjectSerializer, SharedProjectDeleteUserSerializer, ShareProjectBaseSerializer, OtherProjectSerializer,\
    PastProjectsSerializer, ModesStateSerializer, ConstantColorsSerializer, CategorySerializer, ElemetSerializer, \
    RequestSerializer, TutorialSerializer
from content.models import Screen, Project, Prototype, UserElement, UserProfile, Project, Category, SharedProject,\
    BaseWidthPrototype, ModesState, Constant_colors, Element, Request, Tutorials
from .permissions import IsAuthor, EditPermission, DeletePermission, StartPermission, ProfessionalPermission, TeamPermission


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
        categories = Category.objects.filter(prototype=prototype_pk)
        for category in categories:
            category_j = {}
            category_j['title'] = category.title
            category_j['two_in_row'] = category.two_in_row
            elements = category_j['elements'] = []
            icons = category_j['icons'] = []
            response.append(category_j)
            for element in Element.objects.filter(category_prototype=category.id,
                                                  category_prototype__prototype=prototype_pk):
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

# class InitProject(APIView):
#     def get(self, request, project, *args, **kwargs):
#         response = []
#         project = get_object_or_404(Project, pk=project)
#         prototype_pk = project.prototype.pk
#         categories = Category.objects.filter(categoryprototype__prototype=prototype_pk)
#         for category in categories:
#             category_j = {}
#             category_j['title'] = category.title
#             category_j['two_in_row'] = category.two_in_row
#             elements = category_j['elements'] = []
#             icons = category_j['icons'] = []
#             response.append(category_j)
#             for element in category.get_elements_on_prototype(prototype_pk).all():
#                 j_element = {}
#                 j_element['title'] = element.title
#                 j_element['layout'] = [element.light_layout, element.dark_layout]
#                 j_element['image'] = [str(element.light_image), str(element.dark_image)]
#                 j_element['active'] = element.active
#                 if 'icons_' in category.title:
#                     icons.append(j_element)
#                 else:
#                     elements.append(j_element)
#         return JsonResponse({'categories': response})


class ScreenView(APIView):

    def get(self, request, project_id, screen_id=None, action=None):
        print(request.COOKIES)
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
        payload = json.loads(request.body)
        if payload.get('title'): screen.title = payload['title']
        if payload.get('layout') or payload.get('layout') == "": screen.layout = payload['layout']
        if payload.get('width'):
            screen.width = payload['width']
            project.theLastAppliedWidth = payload['width']
        if payload.get('height'):
            screen.height = payload['height']
            project.theLastAppliedHeight = payload['height']
        if payload.get('background_color'): screen.background_color = payload['background_color']
        if payload.get('position'): screen.position = payload['position']
        if payload.get('constant_color'): screen.constant_color_id = payload['constant_color']
        elif payload.get('constant_color') is None: screen.constant_color_id = None
        if payload.get('styles'): screen.styles = payload['styles']
        screen.save()
        if project.count == 10:
            with reversion.create_revision():
                    obj = project
                    obj.save()
                    reversion.set_user(request.user)
                    reversion.set_date_created(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    project.count = 0
        project.count += 1
        project.save()
        serializer = ScreenSerializer(screen)
        return JsonResponse({'screen': serializer.data, "result": True})

    def post(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id, user=request.user)
        except Project.DoesNotExist:
            return JsonResponse({'message': 'Project not found', "result": False})

        payload = json.loads(request.body)
        screens = Screen.objects.filter(project=project_id)
        width = project.prototype.width
        height = project.prototype.height
        layout = ""
        if payload.get('width'):
            width = payload['width']
            project.theLastAppliedWidth = payload['width']
        if payload.get('height'):
            height = payload['height']
            project.theLastAppliedHeight = payload['height']
        if payload.get('layout'): layout = payload['layout']
        screen = Screen.objects.create(
            title=payload['title'],
            project=project,
            layout=layout,
            width=width,
            height=height,
            position=(len(screens) + 1),
            constant_color_id=payload.get('constant_color')
        )
        project.save()
        if payload.get('background_color'): screen.background_color = payload.get('background_color')
        if payload.get('styles'): screen.styles = payload.get('styles')
        screen.base = screen.id
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
        screens = project.screen_set.all()
        if len(screens) != 1:
            position = screen.position
            preview = project.previewScreenId.position
            screen.delete()
            for i in screens:
                if i.position > position:
                    i.position -= 1
                    i.save()
            if int(preview) == int(position):
                new_screen = Screen.objects.get(project_id=project_id, position=1)
                project.previewScreenId = new_screen
                project.save()
            return JsonResponse({'result': True})
        else:
            return JsonResponse({"result": False})


class ProjectApiView(APIView):

    def create_base_colors(self, prototype, project):
        queryset = Constant_colors.objects.filter(to_prototype_id=prototype)
        serializer = ConstantColorsSerializer(queryset, many=True)
        for i in serializer.data:
            Constant_colors.objects.create(
                title=i['title'],
                dark_value=i['dark_value'],
                light_value=i['light_value'],
                project=project
            )

    def get(self, request, project_id=None):
        print(request.COOKIES)
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
                project = Project.objects.filter(id=project_id)
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
        print(request.COOKIES)
        payload = json.loads(request.body)
        try:
            prototype = Prototype.objects.get(id=payload['prototype_id'])
        except Project.DoesNotExist:
            return JsonResponse({'message': 'Prototype not found', "result": False})
        project = Project()
        project_list = Project.objects.filter(user=request.user)
        if request.user.userpermission.permission == 'START':
            if len(project_list) > 3:
                return JsonResponse({'message': 'Project limit reached', 'result': False}, status=status.HTTP_403_FORBIDDEN)
        project.prototype = prototype
        project.name = payload['name']
        project.user = request.user
        project.theLastAppliedWidth = project.prototype.width
        project.theLastAppliedHeight = project.prototype.height
        project.save()
        screen = Screen.objects.create(
            title='first_page',
            project=project,
            width=project.prototype.width,
            height=project.prototype.height,
            position=1,
        )
        project.previewScreenId = screen
        project.save()
        serializer = ProjectSerializer(project)
        data = serializer.data
        data['screen'] = ScreenSerializer(screen).data
        self.create_base_colors(project=project, prototype=prototype.pk)
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
        if payload.get('previewScreenId'):
            project.previewScreenId_id = payload['previewScreenId']
        project.save()
        if project.count == 10:
            with reversion.create_revision():
                    obj = project
                    obj.save()
                    reversion.set_user(request.user)
                    reversion.set_date_created(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    project.count = 0
        project.count += 1
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

    def list(self, request, *args, **kwargs):
        print(request.COOKIES)
        queryset = self.filter_queryset(self.get_queryset()).order_by("-id")
        serializer = self.get_serializer(queryset, many=True)
        for i in serializer.data:
            width = BaseWidthPrototype.objects.\
                    filter(prototype=i['id'])
            i['base_width'] = width.values()
        return response.Response(serializer.data)


class UserElementApiView(APIView):

    def get(self, request, project_id):
        print(request.COOKIES)
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
        if payload.get('type'):
            element.type = payload['type']
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
        if payload.get('type'):
            element.type = payload['type']
        element.save()
        if project.count == 10:
            with reversion.create_revision():
                    obj = project
                    obj.save()
                    reversion.set_user(request.user)
                    reversion.set_date_created(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    project.count = 0
        project.count += 1
        project.save()
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
                position=(len(sceens) + 1),
                constant_color=screen.constant_color,
                styles=screen.styles,
                base=screen.id
            )
            copy_screen.save
            copy_screen_serializer = ScreenSerializer(copy_screen)
            return JsonResponse(copy_screen_serializer.data)
        except:
            return JsonResponse({"result": False, "message": "Screen not found"}, status=status.HTTP_404_NOT_FOUND)


class ProjectCopyView(APIView):
    permission_classes = [IsAuthor or EditPermission]

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
            colors=project.colors,
            theLastAppliedWidth=project.theLastAppliedWidth,
            theLastAppliedHeight=project.theLastAppliedHeight
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
        project = Project.objects.get(id=project_id)
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
                    position=screen.position,
                    styles=screen.styles,
                    base=screen.base
                )
                try:
                    if project.previewScreenId.position == copy_screen.position:
                        copy.previewScreenId = copy_screen
                        copy.save()
                except: pass
                copy_screen.save()
            copy_screens = Screen.objects.filter(project_id=copy.id)
            copy_screen_serializer = ScreenSerializer(copy_screens, many=True)
            return copy_screen_serializer.data
        else:
            pass

    def copy_modesState(self, copy, project_id):
        try:
            modes = ModesState.objects.get(project_id=project_id)
            if modes:
                copy_modes = ModesState.objects.create(
                    project=copy,
                    elements=modes.elements
                )
            serializer = ModesStateSerializer(copy_modes)
            return serializer.data
        except ModesState.DoesNotExist:
            pass

    def copy_constant_colors(self, copy, project_id):
        colors = Constant_colors.objects.filter(project_id=project_id)
        if colors.count() > 0:
            for color in colors:
                copy_color = Constant_colors.objects.create(
                    title=color.title,
                    dark_value=color.dark_value,
                    light_value=color.light_value,
                    project=copy,
                    to_prototype=None
                )
                copy_color.save
            copy_colors = Constant_colors.objects.filter(project_id=copy.id)
            copy_colors_serializer = ConstantColorsSerializer(copy_colors, many=True)
            return copy_colors_serializer.data
        else:
            pass

    def post(self, request, *args, **kwargs):
        project_list = Project.objects.filter(user=request.user)
        if request.user.userpermission.permission == 'START':
            if len(project_list) > 3:
                return JsonResponse({'message': 'Project limit reached', 'result': False}, status=status.HTTP_403_FORBIDDEN)
        copy = self.copy_project(request=request, project_id=kwargs['project_id'])
        copy_element = self.copy_element(copy=copy, project_id=kwargs['project_id'])
        copy_screen = self.copy_screen(copy=copy, project_id=kwargs['project_id'])
        copy_modes = self.copy_modesState(copy=copy, project_id=kwargs['project_id'])
        copy_color = self.copy_constant_colors(copy=copy, project_id=kwargs['project_id'])
        try:
            copy_serializer = ProjectSerializer(copy, many=False)
            return JsonResponse({'result': True, 'copy_project': copy_serializer.data,
                                 'copy_element': copy_element, 'copy_screen': copy_screen, 'copy_modes_state': copy_modes,
                                 'copy_color': copy_color})
        except:
            return copy


class ShareProjectAllView(APIView):
    permission_classes = [IsAuthor]

    def check_max_share_limit(self, user, project):
        share_list = SharedProject.objects.filter(project=project)
        if user.userpermission.permission == 'PROFESSIONAL':
            if len(share_list)>=3:
                return True
        if user.userpermission.permission == 'START':
            if len(share_list)>=1:
                return True
        return False

    def generate_link(self, project_id):
        link = f"https://dashboard.sizze.io/editor/{project_id}?project=shared"
        return link

    def post(self, request, *args, **kwargs):
        serializer = ShareProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        all_users = request.data.get('all_users')
        max_list = self.check_max_share_limit(user=request.user, project=kwargs['project_id'])
        if max_list is True:
            return JsonResponse({'result': False}, status=status.HTTP_403_FORBIDDEN)
        if request.data.get('to_user') == request.user.email:
            return JsonResponse({'result': False, 'message': "You cant share the project with yourself"})
        if (all_users is False) or (all_users == "False"):
            to_user = serializer.validated_data['to_user']
            share_project = SharedProject.objects.filter(project=kwargs['project_id'], to_user=to_user)
            if len(share_project) > 0:
                return JsonResponse({'result': False, 'message': 'This project has already been shared'})
            link = self.generate_link(kwargs['project_id'])
            serializer.save(project_id=kwargs['project_id'], from_user=request.user)
            msg_html = render_to_string('mail/Shared.html', {'to_user': serializer.data['to_user'],
                                                             'from_user': serializer.data['from_user'],
                                                             'project': serializer.data['project'],
                                                             'link': link}
                                        )
            from auth_users.utils import send_html_mail
            send_html_mail(subject=f'{to_user}, the project {serializer.data["project"]} was shared with you',
                           html_content=msg_html, sender=f'Sizze.io <{getattr(settings, "EMAIL_HOST_USER")}>',
                           recipient_list=[serializer.data['to_user']])
            data = serializer.data
            data['link'] = link
            return JsonResponse(data, status=status.HTTP_201_CREATED)
        if all_users is True or (all_users == "True"):
            if request.user.is_superuser or request.user.is_staff:
                serializer.validated_data['to_user'] = None
                share_project = SharedProject.objects.filter(project=kwargs['project_id'], all_users=True)
                if len(share_project) > 0:
                    return JsonResponse({'result': False, 'message': 'This project has already been shared'})
            else:
                return JsonResponse({'result': False, 'message': 'You are not superuser'},
                                    status=status.HTTP_403_FORBIDDEN)
            serializer.save(project_id=kwargs['project_id'], from_user=request.user)
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        shared_projects = SharedProject.objects.filter(project=kwargs['project_id'])
        serializer = ShareProjectSerializer(shared_projects, many=True)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)

    def delete(self, requset, *args, **kwargs):
        serializer = SharedProjectDeleteUserSerializer(data=requset.data)
        serializer.is_valid(raise_exception=True)
        all_users = requset.data.get('all_users')
        if (all_users is True) or (all_users == 'True'):
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
    def get(self, request, project_id):
        project = Project.objects.get(id=project_id)
        versions = Version.objects.get_for_object(project)
        data = versions.values("revision_id", date_time=F('revision__date_created'), user=F('revision__user__username'),
                               comment=F('revision__comment')).order_by('revision__date_created').reverse()[:50]
        return response.Response({"past_projects": data})


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

    def get_data(self, serializer):
        project = {}
        user_element = []
        screens = []
        modes_state = {}
        constant_color = {}
        for i in serializer.data:
            data = dict(i)
            new_data = json.loads(data.get('serialized_data'))
            if new_data[0]['model'] == 'content.screen':
                new_data[0]['fields']['id'] = new_data[0]['pk']
                screens.append(new_data[0]['fields'])
            if new_data[0]['model'] == 'content.project':
                new_data[0]['fields']['id'] = new_data[0]['pk']
                project.update(new_data[0]['fields'])
            if new_data[0]['model'] == 'content.userelement':
                user_element.append(new_data[0]['fields'])
            if new_data[0]['model'] == 'content.modesstate':
                new_data[0]['fields']['id'] = new_data[0]['pk']
                modes_state.update(new_data[0]['fields'])
            if new_data[0]['model'] == 'content.constant_colors':
                new_data[0]['fields']['id'] = new_data[0]['pk']
                constant_color.update(new_data[0]['fields'])
        response_data = {'project': project, 'screens': screens, 'userElements': user_element, "modesState": modes_state,
                         'constant_colors': constant_color}
        return response_data

    def copy_project(self, data):
        project = data.get('project')
        new_project = Project.objects.create(
            name="Restored " + project['name'],
            user_id=project['user'],
            prototype_id=project['prototype'],
            colors=project['colors'],
            theLastAppliedWidth=project['theLastAppliedWidth'],
            theLastAppliedHeight=project['theLastAppliedHeight'],
        )
        return new_project

    def copy_screen(self, new_project, data):
        screens = data.get('screens')
        project = data.get('project')
        previewScreenId = project['previewScreenId']
        for screen in screens:
            new_screen = Screen.objects.create(
                title=screen['title'],
                layout=screen['layout'],
                project_id=new_project.id,
                last_change=screen['last_change'],
                width=screen['width'],
                height=screen['height'],
                background_color=screen['background_color'],
                position=screen['position'],
                styles=screen['styles'],
                base=screen['base']
            )
            if screen['id'] == previewScreenId:
                new_project.previewScreenId = new_screen
                new_project.save()

    def copy_userElement(self, new_project, data):
        elements = data.get('userElements')
        for element in elements:
            UserElement.objects.create(
                title=element['title'],
                layout=element['layout'],
                project_id=new_project.id
            )

    def copy_modesState(self, new_project, data):
        modes = data.get('modesState')
        if modes:
            ModesState.objects.create(
                project_id=new_project.id,
                elements=modes['elements']
            )

    def copy_constant_colors(self, new_project, data):
        color = data.get('constant_colors')
        if color:
            Constant_colors.objects.create(
                title=color['title'],
                dark_value=color['dark_value'],
                light_value=color['light_value'],
                project_id=new_project.id,
                to_prototype=None
            )

    def get(self, request, *args, **kwargs):
        try:
            v = Version.objects.filter(revision_id=kwargs['revision_id']).values('serialized_data')
            serializer = PastProjectsSerializer(v, many=True)
            data = self.get_data(serializer)
            return response.Response(data)
        except:
            return JsonResponse({"message": "Version not found", "result": False})

    def post(self, request, *args, **kwargs):
        # try:
        project_list = Project.objects.filter(user=request.user)
        if request.user.userpermission.permission == "START":
            if len(project_list) > 3:
                return JsonResponse({'message': 'Project limit reached', 'result': False},
                                    status=status.HTTP_403_FORBIDDEN)
        v = Version.objects.filter(revision_id=kwargs['revision_id']).values('serialized_data')
        serializer = PastProjectsSerializer(v, many=True)
        data = self.get_data(serializer)
        new_project = self.copy_project(data)
        self.copy_screen(new_project=new_project, data=data)
        self.copy_userElement(new_project=new_project, data=data)
        self.copy_modesState(new_project=new_project, data=data)
        self.copy_constant_colors(new_project=new_project, data=data)
        return JsonResponse({"message": "Project restored", "result": True})
        # except:
        #     return JsonResponse({"message": "Project not restored", "result": False})

    def delete(self, request, *args, **kwargs):
        try:
            v = Version.objects.filter(revision_id=kwargs['revision_id'])
            r = Revision.objects.filter(id=kwargs['revision_id'])
            v.delete()
            r.delete()
            return JsonResponse({"message": "Past project versions deleted", "result": True})
        except:
            return JsonResponse({"message": "Past project versions not delete", "result": False})

    def put(self, request, *args, **kwargs):
        # try:
        revision = Revision.objects.get(id=kwargs['revision_id'])
        revision.comment = request.data.get('comment')
        revision.save()
        return JsonResponse({'revision_id': revision.id, "date_time": revision.date_created, "user": revision.user.email,
                             "comment": revision.comment})


class ModesStateView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            queryset = ModesState.objects.filter(project_id=kwargs['project_id'])
            queryset.delete()
        except:
            pass
        serializer = ModesStateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(project_id=kwargs['project_id'])
        return JsonResponse(serializer.data)

    def get(self, request, *args, **kwargs):
        try:
            queryset = ModesState.objects.get(project_id=kwargs['project_id'])
            serializer = ModesStateSerializer(queryset)
            return JsonResponse(serializer.data)
        except ModesState.DoesNotExist:
            return JsonResponse({"result": False, "message": "ModesState does not exist"})


class ConstantColorsView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ConstantColorsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(project_id=kwargs['project_id'])
        return JsonResponse(serializer.data)

    def get(self, request, *args, **kwargs):
        queryset = Constant_colors.objects.filter(project_id=kwargs['project_id'])
        serializer = ConstantColorsSerializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)

    def put(self, request, *args, **kwargs):
        queryset = Constant_colors.objects.get(id=kwargs['constant_color_id'])
        title = request.data.get('title')
        if title:
            queryset.title = title
        light = request.data.get('light_value')
        if light:
            queryset.light_value = light
        dark = request.data.get('dark_value')
        if dark:
            queryset.dark_value = dark
        to_prototype = request.data.get('to_prototype')
        if to_prototype:
            queryset.to_prototype = to_prototype
        queryset.save()
        serializer = ConstantColorsSerializer(queryset)
        return JsonResponse(serializer.data)

    def delete(self, *args, **kwargs):
        queryset = Constant_colors.objects.get(id=kwargs['constant_color_id'])
        queryset.delete()
        return JsonResponse({"result": True, "message": "Constant_colors delete success"})


class CategoriApi(APIView):
    def post(self, request):
        data = request.data
        category = Category.objects.create(
            title=data['title'],
            slug=data['slug'],
            two_in_row=data['two_in_row']
        )
        category.prototype.add(request.data['prototype'])
        serializer = CategorySerializer(category)
        category.save()
        return JsonResponse(serializer.data)

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return JsonResponse(serializer.data, safe=False)


class CategoryDetailApi(APIView):
    def get(self, request, category_id):
        category = Category.objects.get(id=category_id)
        serialzier = CategorySerializer(category)
        return JsonResponse(serialzier.data)

    def put(self, request, category_id):
        category = Category.objects.get(id=category_id)
        if request.data.get('title'): category.title = request.data['title']
        if request.data.get('slug'): category.slug = request.data['slug']
        if request.data.get('two_in_row'): category.two_in_row = request.data['two_in_row']
        if request.data.get('prototype'): category.prototype.add(*request.data['prototype'])
        serialzier = CategorySerializer(category)
        category.save()
        return JsonResponse(serialzier.data)


    def delete(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id)
            category.delete()
            return JsonResponse({"result": True})
        except:
            return JsonResponse({'result': False})


class ElementApi(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request):
        elements = Element.objects.all()
        serializer = ElemetSerializer(elements, many=True)
        return JsonResponse(serializer.data)

    def post(self, request):
        data = request.data
        new_element = Element.objects.create(
            title=request.data.get('title'),
            category_prototype_id=request.data.get('category_prototype'),
            light_image=request.FILES.get('light_image'),
            dark_image=request.FILES.get('dark_image'),
            light_layout=request.data.get('light_layout'),
            dark_layout=request.data.get('dark_layout'),
            active=request.data.get('active')
        )
        serializer = ElemetSerializer(new_element)
        new_element.save()
        return JsonResponse(serializer.data)


class ElementDetailApi(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request, element_id):
        element = Element.objects.get(id=element_id)
        serializer = ElemetSerializer(element)
        return JsonResponse(serializer.data)

    def put(self, request, element_id):
        element = Element.objects.get(id=element_id)
        if request.data.get('title'): element.title = request.data.get('title')
        if request.data.get('category_prototype'): element.category_prototype_id = request.data.get('category_prototype')
        if request.FILES.get('light_image'): element.light_image = request.FILES.get('light_image')
        if request.FILES.get('dark_image'): element.dark_image = request.FILES.get('dark_image')
        if request.data.get('light_layout'): element.light_layout = request.data.get('light_layout')
        if request.data.get('dark_layout'): element.dark_layout = request.data.get('dark_layout')
        if request.data.get('active'): element.active = request.data.get('active')
        serializer = ElemetSerializer(element)
        element.save()
        return JsonResponse(serializer.data)

    def delete(self, element_id):
        element = Element.objects.get(id=element_id)
        element.delete()
        return JsonResponse({'result': True})


class RequestApi(APIView):
    def post(self, request, project_id):
        requests = Request.objects.create(
            request_type=request.data.get('type'),
            header=request.data.get('header'),
            url=request.data.get('url'),
            title=request.data.get('title'),
            data=request.data.get('data'),
            project_id=project_id,
            backendType=request.data.get("backendType")
        )
        requests.save()
        serializer = RequestSerializer(requests)
        return JsonResponse(serializer.data)

    def get(self, request, project_id):
        request = Request.objects.filter(project=project_id)
        serializer = RequestSerializer(request, many=True)
        return JsonResponse(serializer.data, safe=False)

class RequestApiDetail(APIView):
    def put(self, request, project_id, request_id):
        requests = Request.objects.get(id=request_id)
        if request.data.get('type'): requests.request_type = requests.data.get('type')
        if request.data.get('header'): requests.header = request.data.get('header')
        if request.data.get('url'): requests.url = request.data.get('url')
        if request.data.get('title'): requests.title = request.data.get('title')
        if request.data.get('data'): requests.data = request.data.get('data')
        if request.data.get('backendType'): requests.backendType = request.data.get('backendType')
        requests.save()
        serializer = RequestSerializer(requests)
        return JsonResponse(serializer.data)

    def get(self, request, project_id, request_id):
        requests = Request.objects.get(id=request_id)
        serializer = RequestSerializer(requests)
        return JsonResponse(serializer.data, safe=False)

    def delete(self, request, project_id, request_id):
        requests = Request.objects.get(id=request_id)
        requests.delete()
        return JsonResponse({'result': True})


class TutorialApi(APIView):
    def get(self, request):
        tutor = Tutorials.objects.all()
        serializer = TutorialSerializer(tutor, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request):
        tutor = Tutorials.objects.create(
            name=request.data.get('name'),
            source=request.data.get('source')
        )
        serializer = TutorialSerializer(tutor)
        return JsonResponse(serializer.data)


class TutorialDetailApi(APIView):
    def get(self, request, tutorial_id):
        tutor = Tutorials.objects.get(id=tutorial_id)
        serializer = TutorialSerializer(tutor)
        return JsonResponse(serializer.data)

    def put(self, request, tutorial_id):
        tutor = Tutorials.objects.get(id=tutorial_id)
        if request.data.get('name'): tutor.name = request.data.get('name')
        if request.data.get('source'): tutor.source = request.data.get('source')
        tutor.save()
        serializer = TutorialSerializer(tutor)
        return JsonResponse(serializer.data)

    def delete(self, request, tutorial_id):
        tutor = Tutorials.objects.get(id=tutorial_id)
        tutor.delete()
        return JsonResponse({"result": True})
