import os, firebase_admin, ast
from content.models import FirebaseSettings, FirebaseRequest
from .serializers import FirebaseSerializer, FirebaseRequestSerializer
from rest_framework.views import APIView
from django.http.response import JsonResponse
from sizzy_lk import settings
from firebase_admin import credentials
from firebase_admin import firestore


class FirebaseSettingsApi(APIView):
    def post(self, request, project_id):
        past_settings = FirebaseSettings.objects.filter(user=request.user, project=project_id)
        if len(past_settings) > 0:
            past_settings.delete()
        # credential_dict = str(request.data.get('credentials'))
        # credential = credential_dict.split()
        # new_credential = ''
        # for i in range(len(credential)):
        #     if i % 2 != 0:
        #         try:
        #             new_credential += (f' "{credential[i][:-1]}": {credential[i+1]}')
        #         except: pass
        # new_credential = "{" + new_credential + "}"
        # new_str = ast.literal_eval(new_credential)
        firebase = FirebaseSettings.objects.create(
            user=request.user,
            project_id=project_id,
            credentials=request.data.get('credentials')
        )
        firebase.save()
        serializer = FirebaseSerializer(firebase)
        return JsonResponse(serializer.data, safe=False)

    def get(self, request, project_id):
        try:
            firebase = FirebaseSettings.objects.get(user=request.user, project=project_id)
            serializer = FirebaseSerializer(firebase)
            return JsonResponse(serializer.data)
        except FirebaseSettings.DoesNotExist:
            return JsonResponse({"result": False})

    def put(self, request, project_id):
        firebase = FirebaseSettings.objects.get(user=request.user, project=project_id)
        if request.data.get('credentials'):
            firebase.credentials = request.data.get('credentials')
        firebase.save()
        serializer = FirebaseSerializer(firebase)
        return JsonResponse(serializer.data)

    def delete(self, request, project_id):
        firebase = FirebaseSettings.objects.get(user=request.user, project=project_id)
        firebase.delete()
        serializer = FirebaseSerializer(firebase)
        return JsonResponse(serializer.data)


class FirebaseRequestApi(APIView):
    def post(self, request, project_id):
        settings = FirebaseSettings.objects.get(user=request.user, project=project_id)
        firebase_req = FirebaseRequest.objects.create(
            request=settings,
            collection=request.data.get('collection'),
            fields=request.data.get('fields')
        )
        firebase_req.save()
        serializer = FirebaseRequestSerializer(firebase_req)
        return JsonResponse(serializer.data, safe=False)

    def get(self, request, project_id):
        firebase_req = FirebaseRequest.objects.filter(request__project_id=project_id)
        serializer = FirebaseRequestSerializer(firebase_req, many=True)
        return JsonResponse(serializer.data, safe=False)


class FirebaseRequestDetailApi(APIView):
    def get(self, request, project_id, fire_req_id):
        firebase_req = FirebaseRequest.objects.get(id=fire_req_id)
        serializer = FirebaseRequestSerializer(firebase_req)
        return JsonResponse(serializer.data)

    def put(self, request, project_id, fire_req_id):
        firebase_req = FirebaseRequest.objects.get(id=fire_req_id)
        if request.data.get('fields'): firebase_req.fields = request.data.get('fields')
        if request.data.get('collection'): firebase_req.collection = request.data.get('collection')
        firebase_req.save()
        serializer = FirebaseRequestSerializer(firebase_req)
        return JsonResponse(serializer.data)

    def delete(self, request, project_id, fire_req_id):
        firebase_req = FirebaseRequest.objects.get(id=fire_req_id)
        firebase_req.delete()
        serializer = FirebaseRequestSerializer(firebase_req)
        return JsonResponse(serializer.data)


class DataApi(APIView):
    def get(self, request, project_id, fire_req_id):
        firebase_req = FirebaseRequest.objects.get(id=fire_req_id)
        settings_file = f'{settings.MEDIA_ROOT}/firebase_credentials/{request.user}__{project_id}.json'
        cred = credentials.Certificate(settings_file)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        docs = db.collection(firebase_req.collection)
        data = docs.stream()
        res = {}
        for i in data:
            res[i.id] = i.to_dict()
        return JsonResponse(res)