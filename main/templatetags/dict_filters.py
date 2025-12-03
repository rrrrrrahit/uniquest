from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Получить элемент словаря по ключу в шаблоне"""
    if dictionary is None:
        return None
    try:
        return dictionary.get(key)
    except (AttributeError, TypeError):
        return None

