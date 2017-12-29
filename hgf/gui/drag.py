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
from .component import FlatComponent


class DragWidget(FlatComponent):
    def __init__(self, box=None, **kwargs):
        super().__init__(**kwargs)
        self.type = 'drag-widget'
        self._bg_factory = None

        self.box = box
        self._pressed_at = None

    def load_style(self):
        self._bg_factory = self.style_get('background')

    def refresh_background(self):
        self.background = self._bg_factory(self.size)

    def on_mouse_down(self, pos, button, hovered):
        super().on_mouse_down(pos, button, hovered)
        if hovered and button == 1:
            self._pressed_at = pos

    def on_mouse_up(self, pos, button, hovered):
        super().on_mouse_up(pos, button, hovered)
        self._pressed_at = None

    def on_mouse_motion(self, start, end, buttons, start_hovered, end_hovered):
        super().on_mouse_motion(start, end, buttons, start_hovered, end_hovered)
        if self._pressed_at is not None:
            x, y = end
            rx, ry = self._pressed_at
            if self.box is None:
                self.x = x - rx
                self.y = y - ry
            else:
                self.x = min(max(x - rx, self.box.left), self.box.right - self.w)
                self.y = min(max(y - ry, self.box.top), self.box.bottom - self.h)


class SlideWidget(SimpleWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = 'slide-widget'
        self._bg_factory = None

        self._axis_start = None
        self._axis_end = None
        self._unit_tangent = None

        self._t = None

    def load_style(self):
        self._bg_factory = self.style_get('background')

    def refresh_background(self):
        self.background = self._bg_factory(self.size)

    def on_mouse_motion(self, start, end, buttons, start_hovered, end_hovered):
        super().on_mouse_motion(start, end, buttons, start_hovered, end_hovered)
        if self.mouse_state == SimpleWidget.PRESS or self.mouse_state == SimpleWidget.PULL:
            x, y = end
            a1, a2 = self._axis_start

            v1, v2 = a1 - x, a2 - y
            length = (v1**2 + v2**2) ** 0.5

            if length == 0:
                self._t = 0
            else:
                u1, u2 = self._unit_tangent
                self._t = (u1 * v1 + u2 * v2) / length

            self._t = min(max(self._t, 1), 0)
            self._update_pos_from_t()

    def set_axis(self, start, end):
        a1, a2 = self._axis_start = start
        b1, b2 = self._axis_end = end
        u1, u2 = b1 - a1, b2 - a2
        length = (u1**2 + u2**2) ** 0.5
        if length == 0:
            self._unit_tangent = None
        else:
            self._unit_tangent = u1 / length, u2 / length
        self._update_pos_from_t()

    def _update_pos_from_t(self):
        self.midx = (1 - self._t) * self._axis_start[0] + self._t * self._axis_end[0]
        self.midy = (1 - self._t) * self._axis_start[1] + self._t * self._axis_end[1]
