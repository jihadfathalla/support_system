from django.apps import apps
from django.http import Http404
from config.cache_function import getKey, setKey


def get_model_by_pk(app_name, model_name, pk):
    model = apps.get_model(app_name, model_name)
    cache_key = f"{model_name}-{pk}"
    data = getKey(cache_key)
    if not data:
        data = model.objects.filter(pk=pk).first()
        if not data:
            raise Http404(f"{model_name} not found")
        setKey(cache_key, data)
        data = getKey(cache_key)
    return data
