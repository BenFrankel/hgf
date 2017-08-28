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
    def __init__(self, label_text, message, **kwargs):
        super().__init__(opacity=1, **kwargs)
        self.type = 'button'
        self._bg_factory = None

        self._label_text = label_text
        self.label = None

        self.message = message

    def load_hook(self):
        super().load_hook()
        self.label = Text(self._label_text,
                          fgcolor=(255, 255, 255),
                          parent_style=True)
        self.register_load(self.label)

    def load_style(self):
        super().load_style()
        self._bg_factory = self.style_get('background')

    def refresh(self):
        super().refresh()
        self.background = self._bg_factory(self.size, self.mouse_state)

    def layout_hook(self):
        super().layout_hook()
        self.label.fontsize = max(self.h // 3, 14)
        self.label.fontsize_apply_transition()
        self.label.center = self.relcenter

    def mouse_state_transition(self, before, after):
        if after == SimpleWidget.PRESS:
            self.label.x -= 1
            self.label.y += 1
        elif before == SimpleWidget.PRESS:
            self.label.x += 1
            self.label.y -= 1
            if after == SimpleWidget.HOVER:
                self.send_message(self.message)
