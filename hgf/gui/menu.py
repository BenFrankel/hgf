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
from .component import GraphicalComponent
from ..util import Rect


# TODO: self.justify = 'left' or 'center' or 'right', default to 'center'
class Menu(GraphicalComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = 'menu'

        self._button_info = []
        self.buttons = []

        self.button_gap = self.h // 50
        self.button_w = self.w // 5
        self.button_h = self.h // 10

    def load_hook(self):
        for button_info in self._button_info:
            self.buttons.append(Button(*button_info,
                                       w=self.button_w,
                                       h=self.button_h))
            self.register_load(self.buttons[-1])
        del self._button_info

    def add_button(self, name, message):
        self._button_info.append((name, message))

    def tick_hook(self):
        buttons_rect = Rect(w=self.button_w,
                            h=len(self.buttons) * (self.button_h + self.button_gap) - self.button_gap)
        button_x = self.midx - buttons_rect.midx
        button_y = self.midy - buttons_rect.midy
        for button in self.buttons:
            button.x = button_x
            button.y = button_y
            button_y += button.h + self.button_gap
