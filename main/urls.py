"""
MAIN URLS
"""

from django.urls import path

from authentication.views import (
    LoginAPIView,
    LogoutAPIView,
    RegisterAPIView,
    DeleteAccountAPIView,
    AdminUserListView,
    AdminUserRoleUpdateView,
    AdminUserToggleActiveView,
    AdminUserDeleteView,
    UserProfileView,
    TelegramBotAuthAPIView
)

from club.views import (
    ClubListView,
    ClubDetailView,
    ClubCreateView, 
    ClubUpdateByManagerView,
    ClubUpdateBySuperAdminView, 
    ClubDeleteView,
    ClubToggleActiveView,
    ClubByCityView,
    ClubByLocationView,
    ClubSeatsView,
    AllSeatsListView,
    SeatReleaseView,
    SeatOccupyView,
    BookingCreateView,
    UserBookingsView,
    BookingCancelView,
    AllBookingsView
)

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

urlpatterns = [
    # Auth endpoints
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('logout-delete/', DeleteAccountAPIView.as_view(), name='logout-delete'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('bot/auth/', TelegramBotAuthAPIView.as_view(), name='bot-auth'),

    # Admin User Management endpoints
    path('users/', AdminUserListView.as_view(), name='admin-users-list'),
    path('users/<int:pk>/role/', AdminUserRoleUpdateView.as_view(), name='admin-user-role-update'),
    path('users/<int:pk>/toggle-active/', AdminUserToggleActiveView.as_view(), name='admin-user-toggle-active'),
    path('users/<int:pk>/delete/', AdminUserDeleteView.as_view(), name='admin-user-delete'),

    # Club endpoints
    path('clubs/', ClubListView.as_view(), name='club-list'),
    path('clubs/create/', ClubCreateView.as_view(), name='club-create'),
    path('clubs/by-location/', ClubByLocationView.as_view(), name='club-by-location'),
    path('clubs/city/<str:city>/', ClubByCityView.as_view(), name='club-by-city'),
    path('clubs/<uuid:pk>/', ClubDetailView.as_view(), name='club-detail'),
    path('clubs/<uuid:pk>/seats/', ClubSeatsView.as_view(), name='club-seats'),
    path('clubs/<uuid:pk>/update/manager/', ClubUpdateByManagerView.as_view(), name='club-update-manager'),
    path('clubs/<uuid:pk>/update/admin/', ClubUpdateBySuperAdminView.as_view(), name='club-update-admin'),
    path('clubs/<uuid:pk>/delete/', ClubDeleteView.as_view(), name='club-delete'),
    path('clubs/<uuid:pk>/toggle-active/', ClubToggleActiveView.as_view(), name='club-toggle-active'),

    # Seat Management endpoints
    path('seats/', AllSeatsListView.as_view(), name='all-seats'),
    path('seats/<uuid:pk>/release/', SeatReleaseView.as_view(), name='seat-release'),
    path('seats/<uuid:pk>/occupy/', SeatOccupyView.as_view(), name='seat-occupy'),

    # Booking endpoints
    path('bookings/', BookingCreateView.as_view(), name='booking-create'),
    path('bookings/my/', UserBookingsView.as_view(), name='user-bookings'),
    path('bookings/all/', AllBookingsView.as_view(), name='all-bookings'),
    path('bookings/<uuid:pk>/cancel/', BookingCancelView.as_view(), name='booking-cancel'),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]