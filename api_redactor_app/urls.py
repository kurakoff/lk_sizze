from . import api
from firebase.api import FirebaseSettingsApi, FirebaseRequestApi, FirebaseRequestDetailApi, DataApi
from django.urls import path


urlpatterns = [
    path('image', api.GoogleImageView.as_view()),

    path('init/<int:project>', api.InitProject.as_view()),
    path('project', api.ProjectApiView.as_view()),
    path('other-project/', api.UserShareProjectsView.as_view({'get': 'list'})),
    path('project/<int:project_id>', api.ProjectApiView.as_view()),
    path('project/<int:project_id>/copy/', api.ProjectCopyView.as_view()),
    path('project/<int:project_id>/share/', api.ShareProjectAllView.as_view()),
    path('project/<int:project_id>/share/user/', api.UserShareProjectDeleteView.as_view({'delete': 'delete'})),

    path('prototype', api.PrototypeApiView.as_view()),
    path('userelements', api.UserElementApiView.as_view()),

    path('userelements/<int:project_id>', api.UserElementApiView.as_view()),
    path('userelements/<int:project_id>/<int:element_id>', api.UserElementApiView.as_view()),

    path('project/<int:project_id>/screens', api.ScreenView.as_view()),
    path('project/<int:project_id>/screens/<int:screen_id>', api.ScreenView.as_view()),
    path('project/<int:project_id>/screens/<int:screen_id>/copy/', api.ScreenCopyView.as_view()),
    path('project/<int:project_id>/screens/<int:screen_id>/<str:action>', api.ScreenView.as_view()),

    path('project/<int:project_id>/history/', api.ScreenHistory.as_view()),
    path('project/<int:project_id>/screens/<int:screen_id>/history/all/', api.ScreenVersionAll.as_view()),
    path('project/<int:project_id>/history/<int:revision_id>/', api.ScreenVersion.as_view()),

    path('project/<int:project_id>/elements/', api.ModesStateView.as_view()),
    path('project/<int:project_id>/constant_colors/', api.ConstantColorsView.as_view()),
    path('project/<int:project_id>/constant_colors/<int:constant_color_id>/', api.ConstantColorsView.as_view()),
    path('project/<int:project_id>/request/', api.RequestApi.as_view()),
    path('project/<int:project_id>/request/<int:request_id>/', api.RequestApiDetail.as_view()),
    path('project/<int:project_id>/firebase/', FirebaseSettingsApi.as_view()),
    path('project/<int:project_id>/firebase/request/', FirebaseRequestApi.as_view()),
    path('project/<int:project_id>/firebase/request/<int:fire_req_id>/', FirebaseRequestDetailApi.as_view()),
    path('project/<int:project_id>/firebase/request/<int:fire_req_id>/data/', DataApi.as_view()),

    path('category/', api.CategoriApi.as_view()),
    path('category/<int:category_id>/', api.CategoryDetailApi.as_view()),

    path('element/', api.ElementApi.as_view()),
    path('element/<int:element_id>/', api.ElementDetailApi.as_view()),

    path('tutorial/', api.TutorialApi.as_view()),
    path('tutorial/<int:tutorial_id>/', api.TutorialDetailApi.as_view()),

    path('screen_category/', api.ScreenCategoryApi.as_view()),
    path('screen_category/<int:screen_category_id>/', api.ScreenCategoryDetailApi.as_view()),
    path('screen_category/<int:screen_category_id>/screen/', api.ScreenCategoryScreen.as_view()),
    path('screen_category/<int:screen_category_id>/screen/<int:screen_id>/', api.ScreenCategoryScreenDetail.as_view()),
]
