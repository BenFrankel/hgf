###############################################################################
#                                                                             #
#   Copyright 2017 - Ben Frankel                                              #
#                                                                             #
#   Licensed under the Apache License, Version 2.0 (the "License");           #
#   you may not use this file except in compliance with the License.          #
#   You may obtain a copy of the License at                                   #
#                                                                             #
#       http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                             #
#   Unless required by applicable law or agreed to in writing, software       #
#   distributed under the License is distributed on an "AS IS" BASIS,         #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#   See the License for the specific language governing permissions and       #
#   limitations under the License.                                            #
#                                                                             #
###############################################################################

from .double_buffer import _HookHandler,  responsive, double_buffer
import logging


class Component(metaclass=_HookHandler):
    def __init__(self, *args,
                 frozen=False,
                 pause=False,
                 active=True,
                 **kwargs):
        super().__init__(*args, **kwargs)

        # Configuration
        self.type = None
        self._context = None

        # Hierarchy
        self._app = None
        self.parent = None
        self._children = []

        # State flags
        self.is_loaded = False

        self.is_visible = False
        self.is_frozen = frozen
        self.is_paused = pause
        self.is_active = active

    def load_style(self): pass

    def load_options(self): pass

    def on_load(self): pass

    def on_show(self): pass

    def on_hide(self): pass

    def on_freeze(self): pass

    def on_unfreeze(self): pass

    def on_pause(self): pass

    def on_unpause(self): pass

    def on_activate(self): pass

    def on_deactivate(self): pass

    def on_adoption(self): pass

    def on_disown(self): pass

    def on_tick(self, elapsed): pass

    @responsive(init=True, priority=-10)
    def refresh_style(self):
        for child in self._children:
            if child.is_loaded:
                child.refresh_style()
        self.load_style()

    @responsive(init=True, priority=-10)
    def refresh_options(self):
        for child in self._children:
            if child.is_loaded:
                child.refresh_options()
        self.load_options()

    @double_buffer
    class is_visible:
        def on_transition(self):
            if self.is_visible:
                self.on_show()
            else:
                self.on_hide()

    @double_buffer
    class is_frozen:
        def on_transition(self):
            if self.is_frozen:
                self.on_freeze()
            else:
                self.on_unfreeze()

    @double_buffer
    class is_paused:
        def on_transition(self):
            if self.is_paused:
                self.on_pause()
            else:
                self.on_unpause()

    @double_buffer
    class is_active:
        def on_transition(self):
            if self.is_active:
                self.on_activate()
            else:
                self.on_deactivate()

    @property
    def is_root(self):
        return self.parent is None

    @property
    def app(self):
        return self._app

    @app.setter
    def app(self, other):
        self._app = other
        for child in self._children:
            child.app = other

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, other):
        self._context = other
        for child in self._children:
            child.context = other

    def style_get(self, *args):
        try:
            return self._app._config.style_get(args[0], self.type, self.context)
        except KeyError:
            if len(args) == 2:
                return args[1]
            raise

    def options_get(self, *args):
        try:
            return self._app._config.options_get(args[0], self.type, self.context)
        except KeyError:
            if len(args) == 2:
                return args[1]
            raise

    def controls_get(self, *args):
        try:
            return self._app._config.controls_get(args[0], self.context)
        except KeyError:
            if len(args) == 2:
                return args[1]
            raise

    def load(self):
        self.is_loaded = True
        self.on_load()

    def show(self):
        self.is_visible = True

    def hide(self):
        self.is_visible = False

    def toggle_show(self):
        self.is_visible = not self.is_visible

    def freeze(self):
        self.is_frozen = True

    def unfreeze(self):
        self.is_frozen = False

    def toggle_frozen(self):
        self.is_frozen = not self.is_frozen

    def pause(self):
        self.is_paused = True

    def unpause(self):
        self.is_paused = False

    def toggle_paused(self):
        self.is_paused = not self.is_paused

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def toggle_active(self):
        self.is_active = not self.is_active

    def register(self, *children):
        for child in children:
            if not child.is_root:
                child.parent.unregister(child)
            child.parent = self
            child.app = self._app
            if child._context is None and self._context is not None:
                child.context = self._context
            child.on_adoption()
            self._children.append(child)

    def register_load(self, *children):
        self.register(*children)
        for child in children:
            child.load()

    def unregister(self, *children):
        for child in children:
            child.on_disown()
            child.app = None
            child.parent = None
            child.context = None
            self._children.remove(child)
            if child.is_focused:
                child.unfocus()

    def handle_message(self, sender, message, **params):
        self.send_message(message)

    def send_message(self, message, **params):
        if not self.is_root:
            self.parent.handle_message(self, message, **params)
        else:
            logging.warning('Unhandled message: "{}"'.format(message), params)

    def _step_input(self): pass

    def _step_tick(self, elapsed):
        self.on_tick(elapsed)

    def _step_output(self): pass

    def _step_reset(self):
        self._flip_transition_hooks()

    def _recursive_step_input(self):
        for child in self._children:
            if child.is_active and not child.is_frozen:
                child._recursive_step_input()
        self._step_input()

    def _recursive_step_tick(self, elapsed):
        for child in self._children:
            if child.is_active and not child.is_paused:
                child._recursive_step_tick(elapsed)
        self._step_tick(elapsed)

    def _recursive_step_output(self):
        for child in self._children:
            if (child.old_is_active or child.is_active) and child.is_visible:
                child._recursive_step_output()
        self._step_output()

    def _recursive_step_reset(self):
        for child in self._children:
            if child.old_is_active or child.is_active:
                child._recursive_step_reset()
        self._step_reset()

    def _recursive_step(self, elapsed):
        # Input
        self._recursive_step_input()

        # Logic
        self._recursive_step_tick(elapsed)

        # Refresh
        self._recursive_call_transition_hooks()
        self._recursive_refresh_responsive_attrs()

        # Output
        self._recursive_step_output()

        # Reset
        self._recursive_step_reset()
