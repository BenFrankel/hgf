class visualattr:
    def __init__(self, func):
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__
        self._value = '_current_{}'.format(self.__name__)
        self._prev_value = '_previous_{}'.format(self.__name__)

        if func.__code__.co_argcount == 1:
            self._hook = '{}_change_hook'.format(self.__name__)
        elif func.__code__.co_argcount == 2:
            self._hook = func.__code__.co_varnames[1]
        else:
            raise TypeError('{} expects 1 or 2 positional arguments but {} were given'
                            .format(self.__class__.__name__, func.__code__.co_argcount))

        self._send_hook = 'send_{}'.format(self._hook)

    def __get__(self, instance, owner):
        try:
            return getattr(instance, self._value)
        except ValueError:
            return getattr(owner, self._value)

    def __set__(self, instance, value):
        setattr(instance, self._value, value)
        queue = getattr(instance, Visual._queue)
        try:
            queue.remove(self)
        except ValueError:
            pass
        if getattr(instance, self._prev_value) != value:
            queue.append(self)


class Visual(type):
    _queue = '__Visual_queue'

    def __init__(cls, name, *bases, **namespace):
        # Find visual attrs
        _visual_attrs = [value for value in cls.__dict__.values() if isinstance(value, visualattr)]

        # Add value, previous value, and change hook for each visualattr
        for attr in _visual_attrs:
            setattr(cls, attr._value, None)
            setattr(cls, attr._prev_value, None)
            if attr._hook not in cls.__dict__:
                setattr(cls, attr._hook, lambda self, before, after: None)
            hook = getattr(cls, attr._hook)
            setattr(cls, attr._send_hook, lambda self: hook(self,
                                                            getattr(self, attr._prev_value),
                                                            getattr(self, attr._value)))

        # Get tick_hook
        try:
            old_tick_hook = cls.tick_hook
        except AttributeError:
            old_tick_hook = lambda self: None

        # Modify tick_hook to send visualattr hook
        def tick_hook(self):
            queue = getattr(self, Visual._queue)
            for attr in queue:
                self.is_dirty = True
                prev_value = getattr(self, attr._prev_value)
                value = getattr(self, attr._value)
                print(attr.__name__, ':', 'Shift from', prev_value, 'to', value, '--', self)
                setattr(self, attr._prev_value, value)
                getattr(self, attr._hook)(prev_value, value)
            queue.clear()
            old_tick_hook(self)
        cls.tick_hook = tick_hook

        # Get __init__
        old_init = cls.__init__

        # Modify __init__ to initialize visualattr hook queue
        def init(self, *args, **kwargs):
            setattr(self, Visual._queue, [])
            old_init(self, *args, **kwargs)
        cls.__init__ = init

        super().__init__(name, bases, namespace)
