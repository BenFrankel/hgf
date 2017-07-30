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
from .visual import visualattr

from ..util import Rect


class Menu(GraphicalComponent):
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

    @visualattr
    def justify(self): pass

    def load_hook(self):
        for button_info in self._button_info:
            self.buttons.append(Button(*button_info))
        del self._button_info
        self.register_load(*self.buttons)

        self._title_text = Text(self.title, fgcolor=(0, 60, 100))
        self.register_load(self._title_text)

    def justify_change_hook(self, before, after):
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

    def resize_hook(self, before, after):
        self._button_gap = self.h // 50
        self._button_w = self.w // 5
        self._button_h = self.h // 10

        buttons_rect = Rect(w=self._button_w,
                            h=len(self.buttons) * (self._button_h + self._button_gap) - self._button_gap)

        self._title_text.fontsize = self._button_h

        button_y = self.midy - buttons_rect.midy
        self._title_text.midy = button_y // 2

        for button in self.buttons:
            button.size = self._button_w, self._button_h
            button.y = button_y
            button_y += button.h + self._button_gap

        self.send_justify_change_hook()

    def add_button(self, name, message):
        self._button_info.append((name, message))
