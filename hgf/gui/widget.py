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

import pygame

from hgf.double_buffer import double_buffer
from .component import LayeredComponent
from ..timing import Delay, Pulse
from ..util import Time, keyboard


class SimpleWidget(LayeredComponent):
    IDLE = 0
    HOVER = 1
    PUSH = 2
    PRESS = 3
    PULL = 4

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mouse_state = SimpleWidget.IDLE

    @double_buffer
    class mouse_state:
        def on_transition(self):
            self.refresh_background_flag = True

    def on_mouse_motion(self, start, end, buttons, start_hovered, end_hovered):
        super().on_mouse_motion(start, end, buttons, start_hovered, end_hovered)
        if end_hovered:
            if buttons[0]:
                if self.mouse_state == SimpleWidget.PULL:
                    self.mouse_state = SimpleWidget.PRESS
                elif self.mouse_state != SimpleWidget.PRESS:
                    self.mouse_state = SimpleWidget.PUSH
            else:
                self.mouse_state = SimpleWidget.HOVER
        elif not buttons[0]:
            self.mouse_state = SimpleWidget.IDLE
        elif start_hovered:
            if self.mouse_state == SimpleWidget.PUSH:
                self.mouse_state = SimpleWidget.IDLE
            else:
                self.mouse_state = SimpleWidget.PULL

    def on_mouse_down(self, pos, button, hovered):
        super().on_mouse_down(pos, button, hovered)
        if button == 1 and hovered:
            self.mouse_state = SimpleWidget.PRESS

    def on_mouse_up(self, pos, button, hovered):
        super().on_mouse_up(pos, button, hovered)
        if button == 1:
            if hovered:
                self.mouse_state = SimpleWidget.HOVER
            else:
                self.mouse_state = SimpleWidget.IDLE

    def _debug_str(self):
        return '{} {}.{}'.format(super()._debug_str(), __class__.__name__, {
            SimpleWidget.IDLE: 'IDLE',
            SimpleWidget.HOVER: 'HOVER',
            SimpleWidget.PUSH: 'PUSH',
            SimpleWidget.PRESS: 'PRESS',
            SimpleWidget.PULL: 'PULL',
        }[self.mouse_state])


# TODO: Drag hook?
# TODO: Scroll hook?
class Widget(SimpleWidget):
    # Messages
    MSG_KEY_REPEAT_START = 'key-repeat-start'
    MSG_KEY_REPEAT = 'key-repeat'
    MSG_LONG_HOVER = 'long-hover'
    MSG_MULTIPLE_CLICK = 'multiple-click'

    # Default values
    KEY_REPEAT_DELAY = '0.450'
    KEY_REPEAT_RATE = '0.050'
    LONG_HOVER_DELAY = '0.450'
    MULTIPLE_CLICK_DELAY = '0.250'

    def __init__(self, key_repeat=True, **kwargs):
        super().__init__(**kwargs)
        # Key repeat when held down
        self._key_repeat = key_repeat
        self._key_repeat_ticker = None
        self._key_repeat_pulse = None
        self._last_key = None

        # Long mouse hover
        self._long_hover_active = False
        self._long_hover_timer = None

        # Double / triple click
        self._multiple_click_count = 0
        self._multiple_click_timer = None

    def on_load(self):
        super().on_load()
        self._key_repeat_ticker = Delay(Widget.MSG_KEY_REPEAT_START)
        self.register_load(self._key_repeat_ticker)

        self._key_repeat_pulse = Pulse(Widget.MSG_KEY_REPEAT)
        self.register_load(self._key_repeat_pulse)

        self._long_hover_timer = Delay(Widget.MSG_LONG_HOVER)
        self.register_load(self._long_hover_timer)

        self._multiple_click_timer = Delay(Widget.MSG_MULTIPLE_CLICK)
        self.register_load(self._multiple_click_timer)

    def load_options(self):
        super().load_options()
        self._key_repeat_ticker.frequency = Time.parse(self.options_get('key-repeat-delay',
                                                                        Widget.KEY_REPEAT_DELAY))
        self._key_repeat_pulse.frequency = Time.parse(self.options_get('key-repeat-rate',
                                                                       Widget.KEY_REPEAT_RATE))
        self._long_hover_timer.frequency = Time.parse(self.options_get('long-hover-delay',
                                                                       Widget.LONG_HOVER_DELAY))
        self._multiple_click_timer.frequency = Time.parse(self.options_get('multiple-click-delay',
                                                                           Widget.MULTIPLE_CLICK_DELAY))

    def on_long_hover(self, pos): pass

    def on_long_hover_end(self): pass

    def on_double_click(self, pos): pass

    def on_triple_click(self, pos): pass

    def on_multiple_click(self, pos, count): pass

    def _long_hover(self, pos):
        self._long_hover_active = True
        self.on_long_hover(pos)

    def _long_hover_end(self):
        if self._long_hover_active:
            self._long_hover_active = False
            self._long_hover_timer.reset()
            self.on_long_hover_end()

    def on_hide(self):
        super().on_hide()
        self._long_hover_end()

    def on_key_down(self, unicode, key, mod):
        super().on_key_down(unicode, key, mod)
        if self._last_key != (unicode, key) and key not in keyboard.command_keys:
            self._last_key = (unicode, key)
            self._key_repeat_ticker.start()
            self._key_repeat_pulse.reset()

    def on_key_up(self, key, mod):
        super().on_key_up(key, mod)
        if self._last_key is not None and key == self._last_key[1]:
            self._last_key = None
            self._key_repeat_ticker.reset()
            self._key_repeat_pulse.reset()

    def on_mouse_state_transition(self):
        super().on_mouse_state_transition()
        if self.mouse_state == SimpleWidget.HOVER:
            self._long_hover_timer.start()
        elif self.old_mouse_state == SimpleWidget.HOVER:
            self._long_hover_timer.reset()

    def on_mouse_down(self, pos, button, hovered):
        super().on_mouse_down(pos, button, hovered)
        if self._long_hover_active:
            self._long_hover_end()
        if button == 1:
            self._multiple_click_timer.start()
            if self._multiple_click_timer.is_running or self._multiple_click_count == 0:
                self._multiple_click_count += 1
            if self._multiple_click_count == 2:
                self.on_double_click(pos)
            elif self._multiple_click_count == 3:
                self.on_triple_click(pos)
            self.on_multiple_click(pos, self._multiple_click_count)

    def on_mouse_motion(self, start, end, buttons, start_hovered, end_hovered):
        super().on_mouse_motion(start, end, buttons, start_hovered, end_hovered)
        if self._long_hover_active:
            self._long_hover_end()
        self._long_hover_timer.start()

    def handle_message(self, sender, message, **params):
        if message == Widget.MSG_KEY_REPEAT_START:
            self._key_repeat_pulse.start()
        elif message == Widget.MSG_KEY_REPEAT:
            self._key_down(*self._last_key, pygame.key.get_mods())
        elif message == Widget.MSG_LONG_HOVER:
            self._long_hover(pygame.mouse.get_pos())
        elif message == Widget.MSG_MULTIPLE_CLICK:
            self._multiple_click_count = 0
        else:
            super().handle_message(sender, message, **params)
