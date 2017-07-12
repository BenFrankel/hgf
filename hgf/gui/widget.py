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

from ..timing import Delay
from ..util import Time

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
    MSG_LONG_KEY_DOWN = 'long-key-down'
    MSG_LONG_HOVER = 'long-hover'
    MSG_MULTIPLE_CLICK = 'multiple-click'

    LONG_KEY_DOWN_DELAY = '0.450'
    LONG_HOVER_DELAY = '0.450'
    MULTIPLE_CLICK_DELAY = '0.250'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Long key down
        self._long_key_down_active = False
        self._long_key_down_timer = None
        self._last_key_down = None

        # Long mouse hover
        self._long_hover_active = False
        self._long_hover_timer = None

        # Double / triple click
        self._multiple_click_count = 0
        self._multiple_click_timer = None

    def long_key_down_hook(self, unicode, key, mod): pass

    def long_key_down_end_hook(self): pass

    def long_hover_hook(self, pos): pass

    def long_hover_end_hook(self): pass

    def double_click_hook(self, pos): pass

    def triple_click_hook(self, pos): pass

    def multiple_click_hook(self, pos, count): pass

    def load_hook(self):
        super().load_hook()
        self._long_key_down_timer = Delay(Widget.MSG_LONG_KEY_DOWN)
        self.register_load(self._long_key_down_timer)

        self._long_hover_timer = Delay(Widget.MSG_LONG_HOVER)
        self.register_load(self._long_hover_timer)

        self._multiple_click_timer = Delay(Widget.MSG_MULTIPLE_CLICK)
        self.register_load(self._multiple_click_timer)

    def load_options(self):
        super().load_options()
        self._long_key_down_timer.delay = Time.parse(self.options_get('long-key-down-delay',
                                                                      Widget.LONG_KEY_DOWN_DELAY))
        self._long_hover_timer.delay = Time.parse(self.options_get('long-hover-delay',
                                                                   Widget.LONG_HOVER_DELAY))
        self._multiple_click_timer.delay = Time.parse(self.options_get('multiple-click-delay',
                                                                       Widget.MULTIPLE_CLICK_DELAY))

    def _long_key_down(self, unicode, key, mod):
        self._long_key_down_active = True
        self.long_key_down_hook(unicode, key, mod)

    def _long_key_down_end(self):
        if self._long_key_down_active:
            self._long_key_down_active = False
            self._last_key_down = None
            self._long_key_down_timer.reset()
            self.long_key_down_end_hook()

    def _long_hover(self, pos):
        self._long_hover_active = True
        self.long_hover_hook(pos)

    def _long_hover_end(self):
        if self._long_hover_active:
            self._long_hover_active = False
            self._long_hover_timer.reset()
            self.long_hover_end_hook()

    def hide_hook(self):
        super().hide_hook()
        self._long_hover_end()

    def lose_focus_hook(self):
        super().lose_focus_hook()
        self._long_key_down_active = False
        self._long_key_down_timer.reset()

    def key_down_hook(self, unicode, key, mod):
        super().key_down_hook(unicode, key, mod)
        self._long_key_down_end()
        self._long_key_down_timer.start()
        self._last_key_down = (unicode, key, mod)

    def key_up_hook(self, key, mod):
        super().key_up_hook(key, mod)
        self._long_key_down_end()

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
            self._multiple_click_timer.start()
            if self._multiple_click_timer.is_running or self._multiple_click_count == 0:
                self._multiple_click_count += 1
            if self._multiple_click_count == 2:
                self.double_click_hook(pos)
            elif self._multiple_click_count == 3:
                self.triple_click_hook(pos)
            self.multiple_click_hook(pos, self._multiple_click_count)

    def mouse_motion_hook(self, start, end, buttons):
        super().mouse_motion_hook(start, end, buttons)
        if self.is_visible:
            if self._long_hover_active:
                self._long_hover_end()
            self._long_hover_timer.start()

    def handle_message(self, sender, message, **params):
        if message == Widget.MSG_LONG_KEY_DOWN:
            self._long_key_down(*self._last_key_down)
        elif message == Widget.MSG_LONG_HOVER:
            self._long_hover(pygame.mouse.get_pos())
        elif message == Widget.MSG_MULTIPLE_CLICK:
            self._multiple_click_count = 0
        else:
            super().handle_message(self, message, **params)
