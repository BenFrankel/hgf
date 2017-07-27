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

from .button import Button
from .text import Text
from .component import GraphicalComponent
from ..util import Rect


class Menu(GraphicalComponent):
    def __init__(self, justify='center', title='Menu', **kwargs):
        super().__init__(**kwargs)
        self.type = 'menu'

        self.title = title
        self._title_text = None

        self._button_info = []
        self.buttons = []

        self.justify = justify
        self._button_gap = self.h // 50
        self._button_w = self.w // 5
        self._button_h = self.h // 10

    def load_hook(self):
        for button_info in self._button_info:
            self.buttons.append(Button(*button_info,
                                       w=self._button_w,
                                       h=self._button_h))
            self.register_load(self.buttons[-1])
        del self._button_info
        self._title_text = Text(self.title, fontsize=self._button_h, fgcolor=(0, 60, 100))
        self.register_load(self._title_text)

    def add_button(self, name, message):
        self._button_info.append((name, message))

    def tick_hook(self):
        buttons_rect = Rect(w=self._button_w,
                            h=len(self.buttons) * (self._button_h + self._button_gap) - self._button_gap)
        if self.justify == 'left':
            button_x = self._button_gap
            self._title_text.x = self._button_gap
        elif self.justify == 'right':
            button_x = self.right - self._button_w - self._button_gap
            self._title_text.right = self.w - self._button_gap
        else:
            button_x = self.midx - buttons_rect.midx
            self._title_text.midx = self.midx
        button_y = self.midy - buttons_rect.midy
        self._title_text.midy = button_y // 2
        for button in self.buttons:
            button.x = button_x
            button.y = button_y
            button_y += button.h + self._button_gap
