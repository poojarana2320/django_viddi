"""turborecruit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from interview.views import interview, messages
from interview.forms import AdminAuthenticationForm, MyPasswordChangeForm
from django.conf.urls import handler404, handler500
from django.contrib.auth import views
from django.urls import reverse_lazy
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', interview.index, name="index"),
    path('admin/', interview.AdminLoginView.as_view(), name='login'),
    path('user/', interview.UserLoginView.as_view(), name='user_login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('', include('interview.urls')),
    # path('index/', interview.HomePageView.as_view(), name='index'),
    path('accounts/signup/admin/', interview.AdminSignUpView.as_view(), name='admin_signup'),
    # path('accounts/edit/admin/<int:pk>/', interview.AdminUpdateView.as_view(), name='admin_edit'),
] + [
    path('password_change/', views.PasswordChangeView.as_view(
        success_url=reverse_lazy('login'),
        form_class=MyPasswordChangeForm),
        name='password_change'),
    path('password_change/done/', views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),
    # Work pending : Forgot Password flow
    path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = messages.error_404
handler500 = messages.error_500
