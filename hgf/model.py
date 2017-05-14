#!/usr/bin/env python

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


class Subject:
    def __init__(self):
        self._observers = []

        self.parent = None
        self._children = []

        self.state_properties = tuple()
        self._old_state = None

    def add_observer(self, observer):
        self._observers.append(observer)

    def register(self, child):
        self._children.append(child)
        if child.parent is not None:
            child.parent.unregister(child)
        child.parent = self

    def register_all(self, children):
        for child in children:
            self.register(child)

    def unregister(self, child):
        self._children.remove(child)
        child.parent = None

    def _notify_all(self, diff):
        for observer in self._observers:
            observer.notify(self, diff)

    def _get_state(self):
        return State(self.state_properties, tuple(getattr(self, attr) for attr in self.state_properties))

    def update(self):
        pass

    def _update(self):
        self.update()
        for child in self._children:
            child._update()
        new_state = self._get_state()
        if self._old_state != new_state:
            before = self._old_state
            self._old_state = new_state
            self._notify_all(StateChange(before, new_state))

    def tick(self):
        self._update()


class State:
    def __init__(self, attrs, vals):
        self.attrs = attrs
        for attr, val in zip(attrs, vals):
            setattr(self, attr, val)

    def __eq__(self, other):
        return all(attr in dir(other) and getattr(other, attr) == getattr(self, attr) for attr in self.attrs)

    def __str__(self):
        return '{' + ', '.join('{}: {}'.format(attr, getattr(self, attr)) for attr in self.attrs) + '}'


class StateChange:
    def __init__(self, before, after):
        self.before = before
        self.after = after
        for attr in after.attrs:
            setattr(self, attr, before is None or getattr(before, attr) != getattr(after, attr))
