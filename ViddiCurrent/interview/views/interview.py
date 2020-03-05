from django.shortcuts import redirect, render
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from ..forms import (UserAuthenticationForm, )

from ..forms import AdminSignUpForm, AdminAuthenticationForm
from ..models import User
from turborecruit.settings import DEBUG


class HomePageView(TemplateView):
    template_name = 'index.html'


# Redirect user to respect dashboard based on User Type
def home(request):
    if request.user.is_authenticated:
        if request.user.user_type < 10:
            return redirect('interviewer:dashboard')
        else:
            return redirect('interviewee:dashboard')
    return render(request, 'login')


# Redirect User from index to user portal by default
def index(request):
    return redirect('user_login')


class AdminLoginView(LoginView):
    """
    Custom admin login view.
    """
    form_class = AdminAuthenticationForm
    template_name = 'registration/admin_login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        if not form.get_user().user_type < 10:
            logout(self.request)
            return redirect('user_login')
        return super(AdminLoginView, self).form_valid(form)


class UserLoginView(LoginView):
    """
    Custom user login view.
    """
    form_class = UserAuthenticationForm
    template_name = 'registration/user_login.html'
    redirect_authenticated_user = True


class AdminSignUpView(CreateView):
    model = User
    form_class = AdminSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'admin'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('index')


class AdminUpdateView(UpdateView):
    model = User
    form_class = AdminSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'admin'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('index')
