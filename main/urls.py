"""
MAIN URLS
"""

from django.urls import path

from authentication.views import (
    LoginAPIView,
    LogoutAPIView,
    DeleteAccountAPIView
)

from club.views import (
    ClubListView, ClubCreateView, ClubUpdateByManagerView,
    ClubUpdateBySuperAdminView, ClubDeleteView, ClubByCityView,
    ClubByLocationView
)

urlpatterns = [
    # qodir
    path('login/', LoginAPIView.as_view()),
    path('logout/', LogoutAPIView.as_view()),
    path('logout-delete/', DeleteAccountAPIView.as_view()),

    # bexa
    path('clubs/', ClubListView.as_view()),
    path('clubs/create/', ClubCreateView.as_view()),
    path('clubs/<uuid:pk>/update/manager/', ClubUpdateByManagerView.as_view()),
    path('clubs/<uuid:pk>/update/admin/', ClubUpdateBySuperAdminView.as_view()),
    path('clubs/<uuid:pk>/delete/', ClubDeleteView.as_view()),
    path('clubs/city/<str:city>/', ClubByCityView.as_view()),
    path('clubs/by-location/', ClubByLocationView.as_view()),
]
