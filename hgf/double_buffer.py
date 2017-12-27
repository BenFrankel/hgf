class double_buffer:
    def __init__(self, cls):
        self.__name__ = cls.__name__
        self.__doc__ = cls.__doc__

        try:
            self._transition_hook = getattr(cls, 'on_transition')
        except AttributeError:
            self._transition_hook = lambda self: None

        try:
            self._change_hook = getattr(cls, 'on_change')
        except AttributeError:
            self._change_hook = lambda self, before, after: None
        if self._change_hook.__code__.co_argcount != 3:
            raise TypeError('The on_change hook of a double_buffer must take 3 arguments (self, before, after): {}'
                            .format(self.__name__))

        underscores = 0
        for c in self.__name__:
            if c == '_':
                underscores += 1
            else:
                break
        name = self.__name__[underscores:]
        underscores = self.__name__[:underscores]

        self._curr_name = '__current_{}'.format(self.__name__)
        self._prev_name = '{}old_{}'.format(underscores, name)
        self._transition_hook_name = '{}on_{}_transition'.format(underscores, name)
        self._change_hook_name = '{}on_{}_change'.format(underscores, name)

    def __get__(self, instance, owner):
        try:
            return getattr(instance, self._curr_name)
        except ValueError:
            return getattr(owner, self._curr_name)

    def __set__(self, instance, value):
        # If not loaded yet, treat as an initial value
        if not instance.is_loaded:
            setattr(instance, self._prev_name, value)
            setattr(instance, self._curr_name, value)
            return

        # Call change hook if necessary
        before = getattr(instance, self._curr_name)
        setattr(instance, self._curr_name, value)
        if value != before:
            getattr(instance, self._change_hook_name)(before, value)

        # Put transition hook at front of queue or remove it
        queue = getattr(instance, _HookHandler._transition_hook_queue_name)
        try:
            queue.remove(self)
        except ValueError:
            pass
        if value != getattr(instance, self._prev_name):
            queue.append(self)


class _responsive:
    def __init__(self, func, init, priority, children_first):
        self._hook = func
        self._initial_value = init
        self._priority = priority
        self._children_first = children_first

        self.__name__ = func.__name__
        self.__doc__ = func.__doc__

        underscores = 0
        for c in self.__name__:
            if c == '_':
                underscores += 1
            else:
                break
        name = self.__name__[underscores:]
        if not name.startswith('refresh_'):
            raise NameError('Responsive method names must start with \'refresh_\': {}'.format(self.__name__))

        self._flag_name = '{}_flag'.format(self.__name__)
        self._hook_name = self.__name__

        if func.__code__.co_argcount != 1:
            raise TypeError('Responsive methods must accept 1 positional argument, not {}: {}'
                            .format(func.__code__.co_argcount, self.__name__))


def responsive(init=False, priority=0, children_first=False):
    def responsive_factory(func):
        return _responsive(func, init, priority, children_first)
    return responsive_factory


class _HookHandler(type):
    _initialized_flag_name = '__HookHandler_is_initialized'
    _transition_hook_queue_name = '__transition_hook_queue'
    _double_buffers_name = '__double_buffers'
    _responsive_attrs_name = '__responsive_attrs'

    def __init__(cls, name, *bases, **namespace):
        double_buffers = {attr for attr in bases[1].values() if isinstance(attr, double_buffer)}
        new_double_buffers = tuple(double_buffers)
        responsive_attrs = {attr for attr in bases[1].values() if isinstance(attr, _responsive)}
        new_responsive_attrs = tuple(responsive_attrs)

        for sprcls in bases[0]:
            if isinstance(sprcls, _HookHandler):
                double_buffers |= frozenset(getattr(sprcls, _HookHandler._double_buffers_name))
                responsive_attrs |= frozenset(getattr(sprcls, _HookHandler._responsive_attrs_name))

        double_buffers = tuple(double_buffers)
        responsive_attrs = tuple(sorted(responsive_attrs, key=lambda a: a._priority))

        setattr(cls, _HookHandler._double_buffers_name, double_buffers)
        setattr(cls, _HookHandler._responsive_attrs_name, responsive_attrs)

        # Create appropriate class attributes
        for attr in new_double_buffers:
            setattr(cls, attr._curr_name, None)
            setattr(cls, attr._prev_name, None)
            setattr(cls, attr._transition_hook_name, attr._transition_hook)
            setattr(cls, attr._change_hook_name, attr._change_hook)

        for attr in new_responsive_attrs:
            setattr(cls, attr._flag_name, attr._initial_value)
            setattr(cls, attr._hook_name, attr._hook)

        # Don't double inject if _HookHandler already injected stuff into a superclass
        if any(isinstance(sprcls, _HookHandler) for sprcls in bases[0]):
            super().__init__(name, bases, namespace)
            return

        # Create initialized flag
        setattr(cls, _HookHandler._initialized_flag_name, False)

        def call_transition_hooks(self):
            if getattr(self, _HookHandler._initialized_flag_name):
                for attr in getattr(self, _HookHandler._transition_hook_queue_name):
                    getattr(self, attr._transition_hook_name)()

        def flip_transition_hooks(self):
            setattr(self, _HookHandler._initialized_flag_name, True)
            queue = getattr(self, _HookHandler._transition_hook_queue_name)
            for attr in queue:
                setattr(self, attr._prev_name, getattr(self, attr._curr_name))
            queue.clear()

        def refresh_responsive_attrs(self, children_first):
            for attr in getattr(self, _HookHandler._responsive_attrs_name):
                if attr._children_first == children_first and getattr(self, attr._flag_name):
                    getattr(self, attr._hook_name)()
                    setattr(self, attr._flag_name, False)

        # TODO: Maintain priority-specified order AND after_children-specified order?
        def recursive_refresh_responsive_attrs(self):
            self._refresh_responsive_attrs(children_first=False)
            for child in self._children:
                if child.old_is_active or child.is_active:
                    child._recursive_refresh_responsive_attrs()
            self._refresh_responsive_attrs(children_first=True)

        def recursive_call_transition_hooks(self):
            self._call_transition_hooks()
            for child in self._children:
                if child.old_is_active or child.is_active:
                    child._recursive_call_transition_hooks()

        setattr(cls, '_call_transition_hooks', call_transition_hooks)
        setattr(cls, '_recursive_call_transition_hooks', recursive_call_transition_hooks)

        setattr(cls, '_flip_transition_hooks', flip_transition_hooks)

        setattr(cls, '_refresh_responsive_attrs', refresh_responsive_attrs)
        setattr(cls, '_recursive_refresh_responsive_attrs', recursive_refresh_responsive_attrs)

        # Modify __init__ to initialize hook queues
        old_init = cls.__init__
        def new_init(self, *args, **kwargs):
            setattr(self, _HookHandler._transition_hook_queue_name, [])
            old_init(self, *args, **kwargs)
        cls.__init__ = new_init

        super().__init__(name, bases, namespace)
