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

from .component import LayeredComponent


class ContextSwitcher(LayeredComponent):
    def __init__(self, opacity=0, **kwargs):
        super().__init__(opacity=opacity, **kwargs)
        self.location = None

    def on_load(self):
        if self.location is not None:
            self.location.load()

    def refresh_proportions(self):
        super().refresh_proportions()
        for child in self._graphical_children:
            child.size = self.size

    def refresh_layout(self):
        for child in self._graphical_children:
            child.pos = self.relpos

    def enter_node(self, child):
        if self.location is not child:
            if self.location is not None:
                self.location.deactivate()
            self.location = child
            if self.is_loaded and not child.is_loaded:
                child.load()
            child.activate()


class Sequence(ContextSwitcher):
    MSG_NEXT = 'next'
    MSG_PREV = 'prev'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loc_list = []
        self.loc_index = None

    @property
    def at_head(self):
        return self.loc_index == 0

    @property
    def at_tail(self):
        return self.loc_index == len(self.loc_list) - 1

    def enter_index(self, index):
        self.loc_index = index
        self.enter_node(self.loc_list[index])

    def handle_message(self, sender, message, **params):
        if message == Sequence.MSG_NEXT and self.loc_index is not None and not self.at_tail:
            self.enter_index(self.loc_index + 1)
        elif message == Sequence.MSG_PREV and self.loc_index is not None and not self.at_head:
            self.enter_index(self.loc_index - 1)
        else:
            super().handle_message(sender, message, **params)

    def register_index(self, index, child):
        self.loc_list.insert(index, child)
        if self.loc_index is None:
            self.enter_index(index)
        elif self.loc_index == index:
            self.enter_node(child)
        else:
            child.deactivate()
        self.register(child)

    def register_head(self, head):
        self.register_index(0, head)

    def register_tail(self, tail):
        self.register_index(len(self.loc_list), tail)


class Hub(ContextSwitcher):
    MSG_RETURN_TO_CENTER = 'exit'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loc_center = None
        self.loc_nodes = dict()

    def register_node(self, name, node):
        if name in self.loc_nodes:
            raise KeyError('A node with the name {} is already registered'.format(name))
        self.loc_nodes[name] = node
        node.deactivate()
        self.register(node)

    def register_center(self, center):
        if self.loc_center is not None:
            raise KeyError('A center node is already registered')
        self.loc_center = center
        if self.location is None:
            self.enter_node(center)
        else:
            center.deactivate()
        self.register(center)

    def handle_message(self, sender, message, **params):
        if message == Hub.MSG_RETURN_TO_CENTER and self.location is not self.loc_center:
            self.enter_node(self.loc_center)
        elif message in self.loc_nodes:
            self.enter_node(self.loc_nodes[message])
        else:
            super().handle_message(sender, message, **params)
