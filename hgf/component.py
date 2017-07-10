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
    def __init__(self):
        # Configuration
        self.type = None
        self._context = None

        # Hierarchy
        self._app = None
        self.parent = None
        self._children = []
        self.z = 0

        # Flags
        self.is_paused = False
        self.is_loaded = False

    def load_style(self): pass

    def load_options(self): pass

    def load_hook(self): pass

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

    def style_get(self, query):
        return self._app._config.style_get(query, self.type, self.context)

    def options_get(self, query):
        return self._app._config.options_get(query, self.type, self.context)

    def controls_get(self, query):
        return self._app._config.controls_get(query, self.context)

    def _reload_style(self):
        for child in self._children:
            if child.is_loaded:
                child._reload_style()
        self.load_style()

    def _reload_options(self):
        for child in self._children:
            if child.is_loaded:
                child._reload_options()
        self.load_options()

    def _load(self):
        self.load_style()
        self.load_options()
        self.load_hook()
        self.is_loaded = True

    def pause(self):
        self.is_paused = True
        self.pause_hook()

    def unpause(self):
        self.is_paused = False
        self.unpause_hook()

    def toggle_pause(self):
        if self.is_paused:
            self.unpause()
        else:
            self.pause()

    def register(self, child):
        if not child.is_root:
            child.parent.unregister(child)
        child.parent = self
        child.app = self._app
        if child.context is None and self.context is not None:
            child.context = self.context
        child.new_parent_hook()
        self._children.append(child)

    def register_all(self, children):
        for child in children:
            self.register(child)

    def unregister(self, child):
        child.disowned_hook()
        child.app = None
        child.parent = None
        child.context = None
        self._children.remove(child)
        if child.is_focused:
            child.lose_focus()

    def unregister_all(self, children):
        for child in children:
            self.unregister(child)

    def register_load(self, child):
        self.register(child)
        child._load()

    def register_load_all(self, children):
        for child in children:
            self.register_load(child)

    def handle_message(self, sender, message, **params):
        self.send_message(message)

    def send_message(self, message, **params):
        if not self.is_root:
            self.parent.handle_message(self, message, **params)

    def _tick(self):
        if not all(self._children[i].z <= self._children[i+1].z for i in range(len(self._children) - 1)):
            self._children.sort(key=lambda x: x.z)
            self.is_dirty = True
        for child in self._children:
            if not child.is_paused:
                child._tick()
        self.tick_hook()

    def step(self):
        self._tick()
