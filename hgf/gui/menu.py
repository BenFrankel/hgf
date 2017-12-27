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

from hgf.double_buffer import double_buffer
from .button import LabeledButton
from .component import LayeredComponent
from .text import Text


class Menu(LayeredComponent):
    def __init__(self, justify='center', title='Menu', **kwargs):
        super().__init__(**kwargs)
        self.type = 'menu'

        self.title = title
        self._title_text = None

        self._button_info = []
        self.buttons = []

        self._button_gap = None
        self._button_w = None
        self._button_h = None

        self.justify = justify

    @double_buffer
    class justify:
        def on_transition(self):
            if self.justify == 'left':
                button_x = self._button_gap
                self._title_text.x = self._button_gap
            elif self.justify == 'right':
                button_x = self.relright - self._button_gap - self._button_w
                self._title_text.right = self.relright - self._button_gap
            else:
                button_x = self.relmidx - self._button_w // 2
                self._title_text.midx = self.relmidx

            for button in self.buttons:
                button.x = button_x

    def on_load(self):
        for button_info in self._button_info:
            self.buttons.append(LabeledButton(*button_info))
        del self._button_info
        self.register_load(*self.buttons)

        self._title_text = Text(self.title, fgcolor=(0, 60, 100))
        self.register_load(self._title_text)

    def refresh_proportions(self):
        super().refresh_proportions()
        self._button_gap = self.h // 50
        self._button_w = self.w // 5
        self._button_h = self.h // 10

        for button in self.buttons:
            button.size = self._button_w, self._button_h

        self._title_text.fontsize = self._button_h
        self._title_text.on_fontsize_transition()

    def refresh_layout(self):
        super().refresh_layout()
        button_y = self.midy - self._button_w // 2
        self._title_text.midy = button_y // 2

        for button in self.buttons:
            button.y = button_y
            button_y += button.h + self._button_gap

        self.on_justify_transition()

    def add_button(self, name, message):
        self._button_info.append((name, message))
