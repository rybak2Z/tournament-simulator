import threading


def lock_data(func):
    """Decorator function. Wrapper acquires and releases a threading.Lock (taken from variable ThreadSharedData.lock)
    to prevent race conditions."""
    
    def wrapper(cls, *args):
        cls.lock.acquire()
        data = func(cls, *args)
        cls.lock.release()
        return data
    
    return wrapper


class ThreadSharedData:
    """
    This class is used to share data between threads. Acquiring and releasing a threading.Lock for preventing race
    conditions is handled by this class and thus does not need to be paid attention to.
    
    You are not meant to create instances of this class but only use the class itself (all methods are class methods).
    """
    
    __shared_data: dict = None    # This holds all the data to share
    lock: threading.Lock = None    # To prevent race conditions
    
    @classmethod
    def init(cls, data: dict = None, lock: threading.Lock = None):
        """
        Class (!) initialization (mandatory to use this class!).
        :param data: The data to share right away. Defaults to an empty dictionary.
        :param lock: The threading.Lock object to use. If none is given, a new one is instantiated.
        """
        
        if data is not None:
            cls.__shared_data = data
        else:
            cls.__shared_data = {}
        
        if lock is not None:
            cls.lock = lock
        else:
            cls.lock = threading.Lock()
    
    @classmethod
    @lock_data
    def get_all(cls):
        """Returns the whole dictionary of shared data."""
        return cls.__shared_data
    
    @classmethod
    @lock_data
    def get_keys(cls):
        """Returns all keys of the shared-data-dictionary."""
        return cls.__shared_data.keys()
    
    @classmethod
    @lock_data
    def get_values(cls):
        """Returns all values of the shared-data-dictionary."""
        return cls.__shared_data.values()
    
    @classmethod
    @lock_data
    def get(cls, key):
        """Returns the value corresponding to the given key of the shared-data-dictionary."""
        return cls.__shared_data.get(key)
    
    @classmethod
    @lock_data
    def set(cls, key, value):
        """Adds/updates a key-value-pair in the shared-data-dictionary."""
        cls.__shared_data[key] = value

    @classmethod
    @lock_data
    def update(cls, dictionary: dict):
        """Updates the shared-data-dictionary with the given dictionary."""
        cls.__shared_data.update(dictionary)
    
    @classmethod
    @lock_data
    def clear(cls):
        """Clears the shared-data-dictionary."""
        cls.__shared_data.clear()
