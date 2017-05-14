#!/usr/bin/env python

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


from enum import Enum

import pygame

from hgf.gui import base, text


class WidgetState(Enum):
    IDLE = 0
    HOVER = 1
    PUSH = 2
    PRESS = 3
    PULL = 4


class Widget(base.Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, hoverable=True, clickable=True, typable=False, **kwargs)
        self.name = 'widget'

        self._widget_state = WidgetState.IDLE

    @property
    def widget_state(self):
        return self._widget_state

    @widget_state.setter
    def widget_state(self, other):
        if self._widget_state != other:
            before = self._widget_state
            self._widget_state = other
            self.widget_state_change(before, other)

    def widget_state_change(self, before, after):
        pass

    def pause(self):
        self.widget_state = WidgetState.IDLE
        super().pause()

    def mouse_enter(self, start, end, buttons):
        if self._visible:
            if self.widget_state == WidgetState.IDLE:
                if buttons[0]:
                    self.widget_state = WidgetState.PUSH
                else:
                    self.widget_state = WidgetState.HOVER
            elif self.widget_state == WidgetState.PULL:
                self.widget_state = WidgetState.PRESS
        super().mouse_enter(start, end, buttons)

    def mouse_exit(self, start, end, buttons):
        if self._visible:
            if self.widget_state == WidgetState.HOVER or self.widget_state == WidgetState.PUSH:
                self.widget_state = WidgetState.IDLE
            elif self.widget_state == WidgetState.PRESS:
                self.widget_state = WidgetState.PULL
        super().mouse_exit(start, end, buttons)

    def mouse_down(self, pos, button):
        if button == 1 and self._visible:
            if self.widget_state != WidgetState.HOVER:
                self.widget_state = WidgetState.HOVER
            self.widget_state = WidgetState.PRESS
        super().mouse_down(pos, button)

    def mouse_up(self, pos, button):
        if button == 1 and self._visible:
            if self.widget_state == WidgetState.PRESS or self.widget_state == WidgetState.PUSH:
                self.widget_state = WidgetState.HOVER
            elif self.widget_state == WidgetState.PULL:
                self.widget_state = WidgetState.IDLE
        super().mouse_up(pos, button)

    def track(self):
        if self._visible and self.widget_state == WidgetState.PULL and not pygame.mouse.get_pressed()[0]:
            self.widget_state = WidgetState.IDLE


class Button(Widget):
    def __init__(self, label_name, message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'button'

        self._label_name = label_name
        self.message = message

        self.label = text.Text(label_name, fontsize=max(self.h // 3, 14), fgcolor=(255, 255, 255))
        self.register(self.label)

    @property
    def label_name(self):
        return self._label_name

    @label_name.setter
    def label_name(self, other):
        if self._label_name != other:
            self._label_name = other
            self.label.text = other

    def widget_state_change(self, before, after):
        if before == WidgetState.PRESS and after == WidgetState.HOVER:
            self.send_message(self.message)
        self.reload()

    def reload(self):
        self.background = self.style_get('button')(self.size, self.widget_state)

    def update(self):
        self.label.center = self.rel_rect().center
        if self.widget_state == WidgetState.PRESS:
            self.label.x -= 1
            self.label.y += 1
        super().update()


class Menu(base.Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'menu'

        self.buttons = []

    def add_button(self, name, message):
        # TODO: Something smarter than this...
        button_w = self.w // 5
        button_h = self.h // 10
        button = Button(name, message, button_w, button_h)
        self.buttons.append(button)
        self.register(button)

    def update(self):
        # TODO: Smarter than this too..
        button_y = 10
        for button in self.buttons:
            button.x = 10
            button.y = button_y + 200
            button_y += button.h + 10
