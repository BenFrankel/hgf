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

from .widget import SimpleWidget
from .text import Text


class Button(SimpleWidget):
    def __init__(self, label_name, message, **kwargs):
        super().__init__(**kwargs)
        self.type = 'button'

        self._label_name = label_name
        self.message = message

        self.label = None

        self._bg_factory = None

    def load_hook(self):
        self.label = Text(self._label_name,
                          fontsize=max(self.h // 3, 14),
                          fgcolor=(255, 255, 255),
                          parent_style=True)
        self.label.center = self.rel_rect().center
        self.register_load(self.label)

    def load_style(self):
        self._bg_factory = self.style_get('background')

    def refresh(self):
        self.background = self._bg_factory(self.size, self.mouse_state)

    @property
    def label_name(self):
        return self._label_name

    @label_name.setter
    def label_name(self, other):
        if self._label_name != other:
            self._label_name = other
            self.label.text = other

    def mouse_state_change_hook(self, before, after):
        if before == SimpleWidget.PRESS and after == SimpleWidget.HOVER:
            self.send_message(self.message)

    def tick_hook(self):
        self.label.center = self.rel_rect().center
        if self.mouse_state == SimpleWidget.PRESS:
            self.label.x -= 1
            self.label.y += 1