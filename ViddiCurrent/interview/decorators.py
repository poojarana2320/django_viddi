from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def user_role_less_than_required(
        function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login', role_less_than=1):
    '''
    Decorator for views that checks that the logged in user is has minimum specific role,
    redirects to the log-in page if necessary.
    '''
    actual_decorator = user_passes_test(
        lambda u: u.is_active and (u.user_type < role_less_than),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def user_role_is_required(
        function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login', role_is=0):
    '''
    Decorator for views that checks that the logged in user is has specific role,
    redirects to the log-in page if necessary.
    '''
    actual_decorator = user_passes_test(
        lambda u: u.is_active and (u.user_type == role_is),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
