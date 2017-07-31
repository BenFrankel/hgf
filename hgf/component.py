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


class Component:
    def __init__(self, pause=False):

        # Configuration
        self.type = None
        self._context = None

        # Hierarchy
        self._app = None
        self.parent = None
        self._children = []

        # State flags
        self.is_frozen = pause
        self.is_paused = pause
        self.is_loaded = False

    def load_hook(self): pass

    def load_style(self): pass

    def load_options(self): pass

    def prepare_hook(self): pass

    def freeze_hook(self): pass

    def unfreeze_hook(self): pass

    def pause_hook(self): pass

    def unpause_hook(self): pass

    def new_parent_hook(self): pass

    def disowned_hook(self): pass

    def tick_hook(self): pass

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

    def _recursive_load_style(self):
        for child in self._children:
            if child.is_loaded:
                child._recursive_load_style()
        self.load_style()

    def _recursive_load_options(self):
        for child in self._children:
            if child.is_loaded:
                child._recursive_load_options()
        self.load_options()

    def load(self):
        self.is_loaded = True
        self.load_hook()

    def _recursive_prepare_hook(self):
        self.prepare_hook()
        for child in self._children:
            if child.is_loaded:
                child._recursive_prepare_hook()

    def prepare(self):
        self.load()
        self._recursive_load_style()
        self._recursive_load_options()
        self._recursive_prepare_hook()

    def reload_style(self):
        self._recursive_load_style()

    def reload_options(self):
        self._recursive_load_options()

    def freeze(self):
        self.is_frozen = True
        self.freeze_hook()
        for child in self._children:
            child.freeze()

    def unfreeze(self):
        self.is_frozen = False
        self.unfreeze_hook()
        for child in self._children:
            child.unfreeze()

    def toggle_freeze(self):
        if self.is_frozen:
            self.unfreeze()
        else:
            self.freeze()

    def pause(self):
        self.is_paused = True
        self.freeze()
        self.pause_hook()

    def unpause(self):
        self.is_paused = False
        self.unfreeze()
        self.unpause_hook()

    def toggle_pause(self):
        if self.is_paused:
            self.unpause()
        else:
            self.pause()

    def register(self, *children):
        for child in children:
            if not child.is_root:
                child.parent.unregister(child)
            child.parent = self
            child.app = self._app
            if child._context is None and self._context is not None:
                child.context = self._context
            child.new_parent_hook()
            self._children.append(child)

    def register_load(self, *children):
        self.register(*children)
        for child in children:
            child.load()

    def register_prepare(self, *children):
        self.register(*children)
        for child in children:
            child.prepare()

    def unregister(self, *children):
        for child in children:
            child.disowned_hook()
            child.app = None
            child.parent = None
            child.context = None
            self._children.remove(child)
            if child.is_focused:
                child.lose_focus()

    def handle_message(self, sender, message, **params):
        self.send_message(message)

    def send_message(self, message, **params):
        if not self.is_root:
            self.parent.handle_message(self, message, **params)

    def _recursive_tick_hook(self):
        for child in self._children:
            if not child.is_paused:
                child._recursive_tick_hook()
        self.tick_hook()

    def step(self):
        self._recursive_tick_hook()
