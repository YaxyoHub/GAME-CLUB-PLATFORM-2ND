from django.urls import path
from .views import (
    ClubListView, ClubCreateView, ClubUpdateByManagerView,
    ClubUpdateBySuperAdminView, ClubDeleteView, ClubByCityView,
    ClubByLocationView
)

urlpatterns = [
    path('clubs/', ClubListView.as_view(), name='club-list'),
    path('clubs/create/', ClubCreateView.as_view(), name='club-create'),
    path('clubs/<uuid:pk>/update/manager/', ClubUpdateByManagerView.as_view(), name='club-update-manager'),
    path('clubs/<uuid:pk>/update/admin/', ClubUpdateBySuperAdminView.as_view(), name='club-update-admin'),
    path('clubs/<uuid:pk>/delete/', ClubDeleteView.as_view(), name='club-delete'),
    path('clubs/city/<str:city>/', ClubByCityView.as_view(), name='club-by-city'),
    path('clubs/by-location/', ClubByLocationView.as_view(), name='club-by-location'),
]
