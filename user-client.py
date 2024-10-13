class SingletonMeta(type):
    """
    A metaclass for creating singleton classes.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class User(metaclass=SingletonMeta):
    """
    User class that uses the Singleton pattern.
    """
    def __init__(self, id):
        self.id = id


