from django.core.cache import cache


# set value if key exist or give error
def addKey(key, value, timeout=None):
    return cache.add(key, value, timeout=timeout)


# reassign value to key
def setKey(key, value, timeout=None):
    return cache.set(key, value, timeout=timeout)


# get value by key
def getKey(key):
    return cache.get(key)


# delete value by key
def deleteKey(key):
    return cache.delete(key)


# set value if key exist then add it
def get_or_set(key, timeout=None):

    value = cache.get(key)

    if value is None:
        value = []
        cache.set(key, value, timeout)
    return value


# print all data from cache
def retrieve_all_data_from_cache():
    all_keys = cache.keys("*")  # fetch all keys from the cache
    all_data = []

    for key in all_keys:
        value = cache.get(key)
        all_data.append({"key": key, "value": value})
    print("cached data", all_data)


# delete all user sessions keys from the cache
def delete_all_data_from_cache():
    all_keys = cache.keys("user_" + "*")

    for key in all_keys:
        cache.delete(key)
