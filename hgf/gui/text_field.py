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


from .menu import Widget
from .text import Text
from .base import StructuralComponent
from ..util import Time, CountdownTimer

import pygame


def edit(s, index, unicode, key, mod):
    if key == pygame.K_BACKSPACE:
        if index == 0:
            return index, s
        if mod & pygame.KMOD_CTRL:
            # TODO: Delete word behind
            return index - 1, s[:index-1] + s[index:]
        return index - 1, s[:index-1] + s[index:]
    if key == pygame.K_DELETE:
        if index == len(s):
            return index, s
        if mod & pygame.KMOD_CTRL:
            # TODO: Delete word ahead
            return index, s[:index] + s[index+1:]
        return index, s[:index] + s[index+1:]

    if key == pygame.K_RIGHT:
        return min(index + 1, len(s)), s
    if key == pygame.K_LEFT:
        return max(index - 1, 0), s

    if unicode:
        return index + 1, s[:index] + unicode + s[index:]

    return index, s


class Cursor(StructuralComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'cursor'
        self.timer = CountdownTimer()
        self.blink_rate = Time(ms=500)

    def pause_hook(self):
        self.timer.pause()

    def unpause_hook(self):
        self.timer.unpause()

    def activate_hook(self):
        self.timer.start(self.blink_rate)

    def restart(self):
        self.timer.restart(self.blink_rate)
        self.show()

    def update_hook(self):
        if not self.timer.is_running:
            self.toggle_show()
            self.timer.start(self.blink_rate)

    def refresh(self):
        self.background = self.style_get('background')(self.size)


class MinorTextField(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, focus=True, **kwargs)
        self.name = 'text-field'
        self.text = None
        self.cursor = None
        self.cursor_index = 0

    def load_hook(self):
        self.text = Text('', fontsize=self.h // 2, fgcolor=(0, 0, 0))
        self.register(self.text)
        self.text.load()

        self.cursor = Cursor(2, self.text.fontsize)
        self.register(self.cursor)
        self.cursor.load()
        self.cursor.deactivate()

    def widget_state_change_hook(self, before, after):
        if after == Widget.HOVER:
            pygame.mouse.set_cursor(*pygame.cursors.ball)
        elif before == Widget.HOVER:
            pygame.mouse.set_cursor(*pygame.cursors.arrow)

    def key_down_hook(self, unicode, key, mod):
        if key == pygame.K_RETURN:
            self.send_message('text-entry', text=self.text.text)
            return
        self.cursor_index, self.text.text = edit(self.text.text, self.cursor_index, unicode, key, mod)
        self.cursor.restart()

    def take_focus_hook(self):
        self.cursor.activate()

    def release_focus_hook(self):
        self.cursor.deactivate()

    def refresh(self):
        self.background = self.style_get('background')(self.size, self.widget_state)

    def update_hook(self):
        self.text.midy = self.rel_rect().midy
        self.text.x = self.text.y

        if self.is_focused:
            self.cursor.midy = self.text.midy
            if len(self.text.text) == 0:
                self.cursor.x = (self.h - self.text.get_rect('x').h) // 2
            elif self.cursor_index == 0:
                self.cursor.x = self.text.x
            elif self.cursor_index == len(self.text.text):
                self.cursor.x = self.text.right
            else:
                metrics = self.text.get_metrics()
                self.cursor.x = self.text.x + sum(m[4] for m in metrics[:self.cursor_index])
