import hashlib
from django.db.models import Model, Q
from django.utils.functional import SimpleLazyObject


def safe_cache_key(value):
    """Convert objects to a safe string representation for caching."""
    if isinstance(value, SimpleLazyObject):
        value = str(value)
    if isinstance(value, Model):
        value = f"{value.__class__.__name__}_{value.pk}"
    return str(value)


def generate_list_cache_key(model, filter_obj):
    if isinstance(filter_obj, dict):
        safe_items = [
            (key, safe_cache_key(value)) for key, value in sorted(filter_obj.items())
        ]
        raw_key = "cache_key:" + str(tuple(safe_items))
    elif isinstance(filter_obj, tuple):
        safe_items = tuple(safe_cache_key(value) for value in filter_obj)
        raw_key = "cache_key:" + str(safe_items)
    elif isinstance(filter_obj, Q):
        raw_key = "cache_key:" + str(filter_obj)
    else:
        print(type(filter_obj))
        raise ValueError(
            "Unsupported filter object type. Only dict, tuple, and Q are allowed."
        )

    hashed_key = hashlib.md5(raw_key.encode()).hexdigest()
    return f"cache_key:{hashed_key}"
