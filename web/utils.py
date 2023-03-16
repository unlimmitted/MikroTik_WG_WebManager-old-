from .models import *

header = [{'title': 'MikroTik WG WebManager'}]


class DataMixin:
    def get_user_context(self, **kwargs):
        context = kwargs
        context['header'] = header
        return context
