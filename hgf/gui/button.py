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

from .widget import MouseState
from .text import Text
from .component import FlatComponent, LayeredComponent


class Button(MouseState, FlatComponent):
    def __init__(self, message, **kwargs):
        super().__init__(opacity=1, **kwargs)
        self.type = 'button'
        self._bg_factory = None

        self.message = message

    def load_style(self):
        super().load_style()
        self._bg_factory = self.style_get('background')

    def refresh_background(self):
        super().refresh_background()
        self.background = self._bg_factory(self.size, self.mouse_state)

    def on_mouse_state_change(self, before, after):
        super().on_mouse_state_change(before, after)
        if before == MouseState.PRESS and after == MouseState.HOVER:
            self.send_message(self.message)


class LabeledButton(MouseState, LayeredComponent):
    def __init__(self, label_text, message, **kwargs):
        super().__init__(**kwargs)
        self._label_text = label_text
        self.label = None

        self._button_message = message
        self.button = None

    def on_load(self):
        super().on_load()
        self.label = Text(self._label_text,
                          fgcolor=(255, 255, 255),
                          parent_style=True)
        self.register_load(self.label)

        self.button = Button(self._button_message)
        self.register_load(self.button)

    def refresh_proportions(self):
        super().refresh_proportions()
        self.label.fontsize = max(self.h // 3, 14)
        self.label.on_fontsize_transition()

        self.button.size = self.size

    def refresh_layout(self):
        super().refresh_layout()
        self.label.center = self.relcenter
        self.button.pos = self.relpos

    def on_mouse_state_transition(self):
        super().on_mouse_state_transition()
        if self.mouse_state == MouseState.PRESS:
            self.label.x -= 1
            self.label.y += 1
        elif self.old_mouse_state == MouseState.PRESS:
            self.label.x += 1
            self.label.y -= 1
