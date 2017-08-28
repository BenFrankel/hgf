class transition:
    def __init__(self, func):
        self._hook = func

        self.__name__ = func.__name__
        self.__doc__ = func.__doc__

        self._curr_name = '__current_{}'.format(self.__name__)
        self._prev_name = '__previous_{}'.format(self.__name__)
        self._hook_name = '{}_transition'.format(self.__name__)
        self._send_name = '{}_apply_transition'.format(self.__name__)

        argc = func.__code__.co_argcount
        if argc == 1:
            self._send = lambda s: getattr(s, self._hook_name)()
        elif argc == 2:
            self._send = lambda s: getattr(s, self._hook_name)(getattr(s, self._curr_name))
        elif argc == 3:
            self._send = lambda s: getattr(s, self._hook_name)(getattr(s, self._prev_name), getattr(s, self._curr_name))
        else:
            raise TypeError('{} should require 1, 2 or 3 positional arguments, not {}'
                            .format(self.__name__, argc))

    def __get__(self, instance, owner):
        try:
            return getattr(instance, self._curr_name)
        except ValueError:
            return getattr(owner, self._curr_name)

    def __set__(self, instance, value):
        setattr(instance, self._curr_name, value)
        queue = getattr(instance, _HookHandler._hook_queue_name)
        try:
            queue.remove(self)
        except ValueError:
            pass
        if value != getattr(instance, self._prev_name):
            queue.append(self)


class _HookHandler(type):
    _initialized_flag_name = '__initialized'
    _hook_queue_name = '__hook_queue'

    def __init__(cls, name, *bases, **namespace):
        # Find hook attrs
        hook_attrs = [attr for attr in bases[1].values() if isinstance(attr, transition)]

        # Setattr the value, previous value, change hook
        # and send change hook for each hook attr
        for attr in hook_attrs:
            setattr(cls, attr._curr_name, None)
            setattr(cls, attr._prev_name, None)
            setattr(cls, attr._hook_name, attr._hook)
            setattr(cls, attr._send_name, attr._send)

        if any(isinstance(sprcls, _HookHandler) for sprcls in bases[0]):
            super().__init__(name, bases, namespace)
            return

        # Add initialized flag
        setattr(cls, _HookHandler._initialized_flag_name, False)

        # Modify tick_hook to send attr hooks
        def transition_hook(self):
            queue = getattr(self, _HookHandler._hook_queue_name)
            if getattr(self, _HookHandler._initialized_flag_name):
                if queue:
                    self.is_stale = True
                    self.is_dirty = True
                for attr in queue:
                    getattr(self, attr._send_name)()
                    setattr(self, attr._prev_name, getattr(self, attr._curr_name))
            else:
                setattr(self, _HookHandler._initialized_flag_name, True)
                for attr in hook_attrs:
                    setattr(self, attr._prev_name, getattr(self, attr._curr_name))
            queue.clear()

        def recursive_transition_hook(self):
            self._transition_hook()
            for child in self._graphical_children:
                if not child.is_paused:
                    child._recursive_transition_hook()

        setattr(cls, '_transition_hook', transition_hook)
        setattr(cls, '_recursive_transition_hook', recursive_transition_hook)

        # Modify __init__ to initialize hook queues
        def init_wrapper(init):
            def inner(self, *args, **kwargs):
                setattr(self, _HookHandler._hook_queue_name, [])
                init(self, *args, **kwargs)
            return inner
        cls.__init__ = init_wrapper(cls.__init__)

        super().__init__(name, bases, namespace)
