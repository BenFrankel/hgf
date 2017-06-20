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


from .text import Text
from .base import StructuralComponent
from ..util import Rect

import pygame


class Widget(StructuralComponent):
    IDLE = 0
    HOVER = 1
    PUSH = 2
    PRESS = 3
    PULL = 4

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'widget'

        self._widget_state = Widget.IDLE

    @property
    def widget_state(self):
        return self._widget_state

    @widget_state.setter
    def widget_state(self, other):
        if self._widget_state != other:
            before = self._widget_state
            self._widget_state = other
            self.widget_state_change_hook(before, other)
            self.refresh()

    def widget_state_change_hook(self, before, after):
        pass

    def pause_hook(self):
        self.widget_state = Widget.IDLE

    def mouse_enter_hook(self, start, end, buttons):
        if self._is_visible:
            if self.widget_state == Widget.IDLE:
                if buttons[0]:
                    self.widget_state = Widget.PUSH
                else:
                    self.widget_state = Widget.HOVER
            elif self.widget_state == Widget.PULL:
                self.widget_state = Widget.PRESS

    def mouse_exit_hook(self, start, end, buttons):
        if self._is_visible:
            if self.widget_state == Widget.HOVER or self.widget_state == Widget.PUSH:
                self.widget_state = Widget.IDLE
            elif self.widget_state == Widget.PRESS:
                self.widget_state = Widget.PULL

    def mouse_down_hook(self, pos, button):
        if button == 1 and self._is_visible:
            if self.widget_state != Widget.HOVER:
                self.widget_state = Widget.HOVER
            self.widget_state = Widget.PRESS

    def mouse_up_hook(self, pos, button):
        if button == 1 and self._is_visible:
            if self.widget_state == Widget.PRESS or self.widget_state == Widget.PUSH:
                self.widget_state = Widget.HOVER
            elif self.widget_state == Widget.PULL:
                self.widget_state = Widget.IDLE

    def track_hook(self):
        if self._is_visible and self.widget_state == Widget.PULL and not pygame.mouse.get_pressed()[0]:
            self.widget_state = Widget.IDLE


class Button(Widget):
    def __init__(self, label_name, message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'button'

        self._label_name = label_name
        self.message = message

        self.label = None

    def load_hook(self):
        self.label = Text(self._label_name, fontsize=max(self.h // 3, 14), fgcolor=(255, 255, 255))
        self.label.center = self.rel_rect().center
        self.register(self.label)
        self.label.load()

    @property
    def label_name(self):
        return self._label_name

    @label_name.setter
    def label_name(self, other):
        if self._label_name != other:
            self._label_name = other
            self.label.text = other

    def widget_state_change_hook(self, before, after):
        if before == Widget.PRESS and after == Widget.HOVER:
            self.send_message(self.message)

    def update_hook(self):
        self.label.center = self.rel_rect().center
        if self.widget_state == Widget.PRESS:
            self.label.x -= 1
            self.label.y += 1

    def refresh(self):
        self.background = self.style_get('background')(self.size, self.widget_state)


class Menu(StructuralComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'menu'

        self._button_info = []
        self.buttons = []

        self.button_gap = self.h // 50
        self.button_w = self.w // 5
        self.button_h = self.h // 10

    def add_button(self, name, message):
        self._button_info.append((name, message))

    def load_hook(self):
        for button_info in self._button_info:
            self.buttons.append(Button(*button_info, self.button_w, self.button_h))
            self.register(self.buttons[-1])
            self.buttons[-1].load()
        del self._button_info

    def update_hook(self):
        buttons_rect = Rect(w=self.button_w,
                            h=len(self.buttons) * (self.button_h + self.button_gap) - self.button_gap)
        button_x = self.midx - buttons_rect.midx
        button_y = self.midy - buttons_rect.midy
        for button in self.buttons:
            button.x = button_x
            button.y = button_y
            button_y += button.h + self.button_gap
