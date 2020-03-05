from django import template

register = template.Library()


@register.filter('format_numbers')
def format_numbers(number, fmt):
    if isinstance(number, int):
        fmt = '%0' + str(fmt) + 'd'
        return fmt % number
    return False
