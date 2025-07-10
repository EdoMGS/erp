# erp_system/accounts/urls.py
# This is your central login/logout config.

from django.contrib.auth import views as auth_views
from django.urls import path

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]
# No changes needed if settings.py is properly configured to use CustomUser
