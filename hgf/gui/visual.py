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

        self._send_hook = '{}_send'.format(self._hook)

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
    _queue = '__queue'
    _initialized = '__initialized'

    def __init__(cls, name, *bases, **namespace):
        # Find visualattrs
        _visualattrs = [attr for attr in cls.__dict__.values() if isinstance(attr, visualattr)]

        # Add value, previous value, change hook
        # and send change hook for each visualattr
        for attr in _visualattrs:
            setattr(cls, attr._value, None)
            setattr(cls, attr._prev_value, None)
            if attr._hook not in cls.__dict__:
                setattr(cls, attr._hook, lambda self, before, after: None)
            setattr(cls,
                    attr._send_hook,
                    lambda self: getattr(self, attr._hook)(getattr(self, attr._prev_value),
                                                           getattr(self, attr._value)))

        if any(isinstance(sprcls, Visual) for sprcls in cls.__bases__):
            super().__init__(name, bases, namespace)
            return

        # Add initialized flag
        setattr(cls, Visual._initialized, False)

        # Modify tick_hook to send visualattr hook
        def tick_hook_wrapper(tick_hook):
            def inner(self):
                queue = getattr(self, Visual._queue)
                if getattr(self, Visual._initialized):
                    for attr in queue:
                        self.is_dirty = True
                        prev_value = getattr(self, attr._prev_value)
                        value = getattr(self, attr._value)
                        getattr(self, attr._hook)(prev_value, value)
                        setattr(self, attr._prev_value, value)
                    tick_hook(self)
                else:
                    setattr(self, Visual._initialized, True)
                    for attr in _visualattrs:
                        setattr(self, attr._prev_value, getattr(self, attr._value))
                queue.clear()
            return inner
        cls.tick_hook = tick_hook_wrapper(cls.tick_hook or (lambda self: None))

        # Modify __init__ to initialize hook queue
        def init_wrapper(init):
            def inner(self, *args, **kwargs):
                setattr(self, Visual._queue, [])
                init(self, *args, **kwargs)
            return inner
        cls.__init__ = init_wrapper(cls.__init__)

        super().__init__(name, bases, namespace)
