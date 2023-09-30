import weakref

class Singleton:
    _instances = weakref.WeakValueDictionary()

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[cls] = instance
        return cls._instances[cls]