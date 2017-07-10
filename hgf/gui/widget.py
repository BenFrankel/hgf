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

from .component import GraphicalComponent
from ..util import Time, Timer, CountdownTimer

import pygame


class SimpleWidget(GraphicalComponent):
    IDLE = 0
    HOVER = 1
    PUSH = 2
    PRESS = 3
    PULL = 4

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mouse_state = SimpleWidget.IDLE

    def mouse_state_change_hook(self, before, after): pass

    @property
    def mouse_state(self):
        return self._mouse_state

    @mouse_state.setter
    def mouse_state(self, other):
        if self._mouse_state != other:
            before = self._mouse_state
            self._mouse_state = other
            self.mouse_state_change_hook(before, other)
            self.refresh()

    def pause_hook(self):
        super().pause_hook()
        self.mouse_state = SimpleWidget.IDLE

    def mouse_enter_hook(self, start, end, buttons):
        super().mouse_enter_hook(start, end, buttons)
        if self.is_visible:
            if self.mouse_state == SimpleWidget.IDLE:
                if buttons[0]:
                    self.mouse_state = SimpleWidget.PUSH
                else:
                    self.mouse_state = SimpleWidget.HOVER
            elif self.mouse_state == SimpleWidget.PULL:
                self.mouse_state = SimpleWidget.PRESS

    def mouse_exit_hook(self, start, end, buttons):
        super().mouse_exit_hook(start, end, buttons)
        if self.is_visible:
            if self.mouse_state == SimpleWidget.HOVER or self.mouse_state == SimpleWidget.PUSH:
                self.mouse_state = SimpleWidget.IDLE
            elif self.mouse_state == SimpleWidget.PRESS:
                self.mouse_state = SimpleWidget.PULL

    def mouse_down_hook(self, pos, button):
        super().mouse_down_hook(pos, button)
        if self.is_visible and button == 1:
            if self.mouse_state != SimpleWidget.HOVER:
                self.mouse_state = SimpleWidget.HOVER
            self.mouse_state = SimpleWidget.PRESS

    def mouse_up_hook(self, pos, button):
        super().mouse_up_hook(pos, button)
        if self.is_visible and button == 1:
            if self.mouse_state == SimpleWidget.PRESS or self.mouse_state == SimpleWidget.PUSH:
                self.mouse_state = SimpleWidget.HOVER
            elif self.mouse_state == SimpleWidget.PULL:
                self.mouse_state = SimpleWidget.IDLE

    def track_hook(self):
        super().track_hook()
        if self.is_visible and self.mouse_state == SimpleWidget.PULL and not pygame.mouse.get_pressed()[0]:
            self.mouse_state = SimpleWidget.IDLE


# TODO: Drag hook?
# TODO: Scroll hook?
class Widget(SimpleWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Long key down
        self._long_key_down_active = False
        self._long_key_down_delay = None
        self._long_key_down_timer = Timer()
        self._last_pressed = None

        # Long mouse hover
        self._long_hover_active = False
        self._long_hover_delay = None
        self._long_hover_timer = Timer()

        # Double / triple click
        self._multiple_click_count = 0
        self._multiple_click_delay = None
        self._multiple_click_timer = CountdownTimer()

    def long_key_down_hook(self, unicode, key, mod): pass

    def long_key_down_end_hook(self): pass

    def long_hover_hook(self, pos): pass

    def long_hover_end_hook(self): pass

    def double_click_hook(self): pass

    def triple_click_hook(self): pass

    def _long_hover_end(self):
        self._long_hover_timer.reset()
        self.long_hover_end_hook()
        self._long_hover_active = False

    def hide_hook(self):
        super().hide_hook()
        self._long_hover_end()

    def lose_focus_hook(self):
        super().lose_focus_hook()
        self._long_key_down_timer.reset()
        self._long_key_down_active = False

    def load_options(self):
        super().load_options()
        self._long_key_down_delay = Time.parse(self.options_get('long-key-down-delay'))
        self._long_hover_delay = Time.parse(self.options_get('long-hover-delay'))
        self._multiple_click_delay = Time.parse(self.options_get('multiple-click-delay'))

    def key_down_hook(self, unicode, key, mod):
        super().key_down_hook(unicode, key, mod)
        self._long_key_down_timer.start()
        self._last_pressed = (unicode, key, mod)
        if self._long_key_down_active:
            self._long_key_down_active = False
            self.long_key_down_end_hook()

    def key_up_hook(self, key, mod):
        super().key_up_hook(key, mod)
        self._long_key_down_timer.reset()
        self._last_pressed = None
        if self._long_key_down_active:
            self._long_key_down_active = False
            self.long_key_down_end_hook()

    def mouse_state_change_hook(self, before, after):
        super().mouse_state_change_hook(before, after)
        if after == SimpleWidget.HOVER:
            self._long_hover_timer.start()
        elif before == SimpleWidget.HOVER:
            self._long_hover_timer.reset()

    def mouse_down_hook(self, pos, button):
        super().mouse_down_hook(pos, button)
        if not self.is_visible:
            return

        if self._long_hover_active:
            self._long_hover_end()

        if button == 1:
            if self._multiple_click_timer.is_running or self._multiple_click_count == 0:
                self._multiple_click_count += 1
            if self._multiple_click_count == 2:
                self.double_click_hook()
            elif self._multiple_click_count == 3:
                self.triple_click_hook()
            self._multiple_click_timer.start(self._multiple_click_delay)

    def mouse_motion_hook(self, start, end, buttons):
        super().mouse_motion_hook(start, end, buttons)
        if self.is_visible:
            if self._long_hover_active:
                self._long_hover_end()
            self._long_hover_timer.start()

    def tick_hook(self):
        super().tick_hook()
        if not self._long_key_down_active\
                and self._long_key_down_timer.is_running\
                and self._long_key_down_timer.time > self._long_key_down_delay:
            self.long_key_down_hook(*self._last_pressed)
            self._long_key_down_timer.pause()
            self._long_key_down_active = True

        if not self._long_hover_active\
                and self._long_hover_timer.is_running\
                and self._long_hover_timer.time > self._long_hover_delay:
            self.long_hover_hook(pygame.mouse.get_pos())
            self._long_hover_timer.pause()
            self._long_hover_active = True

        if self._multiple_click_count > 0\
                and self._multiple_click_timer.is_paused:
            self._multiple_click_count = 0
