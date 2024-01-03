import weakref

class Singleton:
    _instances = weakref.WeakValueDictionary()
    def __new__(cls, user_id, *args, **kwargs):
        key = (cls, user_id)
        if key not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[key] = instance
        return cls._instances[key]
