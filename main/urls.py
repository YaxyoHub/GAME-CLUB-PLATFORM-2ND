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
    ClubListView, 
    ClubCreateView, 
    ClubUpdateByManagerView,
    ClubUpdateBySuperAdminView, 
    ClubDeleteView, 
    ClubByCityView,
    ClubByLocationView
)

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

urlpatterns = [
    # Qodir lee
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('logout-delete/', DeleteAccountAPIView.as_view(), name='logout-delete'),

    # Bexruzbek

    # Club List & Special Queries (Statik va maxsus routelar tepada)
    path('clubs/', ClubListView.as_view(), name='club-list'),
    path('clubs/create/', ClubCreateView.as_view(), name='club-create'),
    path('clubs/by-location/', ClubByLocationView.as_view(), name='club-by-location'),
    path('clubs/city/<str:city>/', ClubByCityView.as_view(), name='club-by-city'),
    # Club Detail / Actions (UUID parametrli routelar pastda)
    path('clubs/<uuid:pk>/update/manager/', ClubUpdateByManagerView.as_view(), name='club-update-manager'),
    path('clubs/<uuid:pk>/update/admin/', ClubUpdateBySuperAdminView.as_view(), name='club-update-admin'),
    path('clubs/<uuid:pk>/delete/', ClubDeleteView.as_view(), name='club-delete'),


    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]