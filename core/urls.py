from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),

    path('register/', views.register_view, name='register'),
    path("prices/", views.price_list, name="price_list"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("recycler-dashboard/", views.recycler_dashboard, name="recycler_dashboard"),

    path('request/', views.request_pickup, name='request_pickup'),
    path('verify/', views.verify_request, name='verify'),
    path("resend-otp/", views.resend_otp, name="resend_otp"),

    path('success/', views.request_success, name='success'),
    path('logout/', views.logout_view, name='logout'),
    path("profile/", views.profile_view, name="profile"),
    path("change-password/", views.change_password, name="change_password"),

    path("agent-dashboard/", views.agent_dashboard, name="agent_dashboard"),
    path("agent-update/<int:request_id>/", views.agent_update_status, name="agent_update_status"),
    path("assign-agent/<int:request_id>/", views.assign_agent, name="assign_agent"),
]
