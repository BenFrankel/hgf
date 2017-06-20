from hgf.gui.menu import WidgetState

from .base import StructuralComponent
from .text import Text
from .menu import Widget
from ..util.timer import Timer

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
        self.on = True
        self.timer = Timer()

    def pause_hook(self):
        self.timer.pause()

    def unpause_hook(self):
        self.timer.unpause()

    def refresh(self):
        if self.on:
            self.background = self.style_get('background')(self.size)
        else:
            self.background.set_alpha(255)


class MinorTextField(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, focus=True, **kwargs)
        self.name = 'text_field'

        self.text = None
        self.cursor = None
        self.cursor_index = 0

    def load_hook(self):
        self.text = Text('', fontsize=self.h // 2, fgcolor=(0, 0, 0))
        self.register(self.text)
        self.text.load()

        self.cursor = Cursor(2, int(self.text.fontsize * 0.85))
        self.register(self.cursor)
        self.cursor.load()

    def widget_state_change_hook(self, before, after):
        if after == WidgetState.HOVER:
            pygame.mouse.set_cursor(*pygame.cursors.ball)
        elif before == WidgetState.HOVER:
            pygame.mouse.set_cursor(*pygame.cursors.arrow)
        self.refresh()

    def key_down(self, unicode, key, mod):
        self.cursor_index, self.text.text = edit(self.text.text, self.cursor_index, unicode, key, mod)
        print(repr(self.text.text), self.cursor_index)

    def refresh(self):
        self.background = self.style_get('background')(self.size, self.widget_state)

    def update_hook(self):
        self.text.midy = self.rel_rect().midy
        self.text.x = self.text.y

        if self.is_focused:
            self.cursor.show()
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
        else:
            self.cursor.hide()

        super().update_hook()
