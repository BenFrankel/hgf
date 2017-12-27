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

from .widget import SimpleWidget, Widget
from .text import TextBox
from .component import FlatComponent

from ..timing import Pulse
from ..util import Time, keyboard

import pygame
import pyperclip

import functools


def _backwards_word(s, index):
    start = index - 1
    while start >= 0 and not s[start].isalnum():
        start -= 1
    while start >= 0 and s[start].isalnum():
        start -= 1
    return start + 1


def _forwards_word(s, index):
    end = index
    while end < len(s) and not s[end].isalnum():
        end += 1
    while end < len(s) and s[end].isalnum():
        end += 1
    return end


def _edit(text, index, unicode, key, mod):
    if key == pygame.K_BACKSPACE:
        if index == 0:
            return index, text
        if mod & pygame.KMOD_CTRL:
            start = _backwards_word(text, index)
            return start, text[:start] + text[index:]
        return index - 1, text[:index - 1] + text[index:]
    if key == pygame.K_DELETE:
        if index == len(text):
            return index, text
        if mod & pygame.KMOD_CTRL:
            end = _forwards_word(text, index)
            return index, text[:index] + text[end:]
        return index, text[:index] + text[index + 1:]

    if unicode == '\t':
        unicode = '    '
    return index + len(unicode), text[:index] + unicode + text[index:]


def _edit_region(text, start, end, unicode, key, mod):
    if key == pygame.K_BACKSPACE or key == pygame.K_DELETE:
        return start, text[:start] + text[end:]

    if unicode == '\t':
        unicode = '    '

    return start + len(unicode), text[:start] + unicode + text[end:]


class Cursor(FlatComponent):
    BLINK_RATE = '0.500'

    MSG_BLINK = 'blink'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.blinker = None
        self._bg_factory = None

    def on_load(self):
        self.blinker = Pulse(Cursor.MSG_BLINK)
        self.register_load(self.blinker)

    def load_style(self):
        self._bg_factory = self.parent.style_get('cursor-bg')

    def load_options(self):
        self.blinker.frequency = Time.parse(self.parent.options_get('cursor-blink-rate',
                                                                    Cursor.BLINK_RATE))

    def refresh_background(self):
        self.w = max(self.parent.line_height // 10, 1)
        self.h = self.parent.line_height
        self.background = self._bg_factory(self.size)

    def on_activate(self):
        self.blinker.start()

    def start(self):
        if not self.is_paused:
            self.show()
            self.blinker.start()

    def handle_message(self, sender, message, **params):
        if message == Cursor.MSG_BLINK:
            self.toggle_show()
        else:
            super().handle_message(sender, message, **params)


class Highlight(FlatComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start = (0, 0)
        self.end = (0, 0)
        self.bgcolor = None

    def load_style(self):
        self.bgcolor = self.parent.style_get('highlight-bg-color')

    def refresh_background(self):
        lh = self.parent.line_height
        surf = pygame.Surface(self.size, pygame.SRCALPHA)
        if self.start[1] == self.end[1]:
            pygame.draw.rect(surf,
                             self.bgcolor,
                             pygame.Rect(self.start[0],
                                         self.start[1],
                                         self.end[0] - self.start[0],
                                         lh))
        else:
            pygame.draw.rect(surf,
                             self.bgcolor,
                             pygame.Rect(self.start[0],
                                         self.start[1],
                                         self.w - self.start[0],
                                         lh))
            inbetween = (self.end[1] - self.start[1]) // lh - 1
            if inbetween > 0:
                pygame.draw.rect(surf,
                                 self.bgcolor,
                                 pygame.Rect(0,
                                             self.start[1] + lh,
                                             self.w,
                                             lh * inbetween))
            pygame.draw.rect(surf,
                             self.bgcolor,
                             pygame.Rect(0,
                                         self.end[1],
                                         self.end[0],
                                         lh))
        self.background = surf


@functools.total_ordering
class CursorPlacement:
    def __init__(self, index=0, row=0, col=0, raw_x=0, raw_y=0, x=0, y=0):
        # Index in text (for horizontal navigation & editing)
        self.index = index

        # Row and column in the wrapped text
        self.row = row
        self.col = col

        # Ideal x, y position (for vertical navigation)
        self.raw_x = raw_x
        self.raw_y = raw_y

        # Actual x, y position (for displaying cursor)
        self.x = x
        self.y = y

    @property
    def pos(self):
        return self.x, self.y

    @pos.setter
    def pos(self, other):
        self.x, self.y = other

    def copy(self):
        return CursorPlacement(self.index, self.row, self.col, self.raw_x, self.raw_y, self.x, self.y)

    def __lt__(self, other):
        return self.index < other.index

    def __eq__(self, other):
        try:
            return self.index == other.index
        except AttributeError:
            return False

    def __repr__(self):
        return 'CursorPlacement(index={}, row={}, col={}, raw_x={}, raw_y={}, x={}, y={})'\
            .format(self.index, self.row, self.col, self.raw_x, self.raw_y, self.x, self.y)

    __str__ = __repr__


# TODO: Undo
# TODO: Double click to highlight word, triple to highlight line
class TextEntryBox(Widget, TextBox):
    MSG_UNDO = 'text-undo'
    MSG_HIGHLIGHT_ALL = 'text-highlight-all'
    MSG_CUT = 'text-cut'
    MSG_COPY = 'text-copy'
    MSG_PASTE = 'text-paste'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Cursor
        self.cursor = None
        self._cursor_place = CursorPlacement()

        # Highlighting
        self.highlight = None
        self._hl_cursor_place = None

    def on_load(self):
        super().on_load()
        self.cursor = Cursor(z=10, active=False)
        self.register_load(self.cursor)

        self.highlight = Highlight(z=-10, active=False)
        self.register_load(self.highlight)

    def refresh_proportions(self):
        super().refresh_proportions()
        self.highlight.w = self.w - 2 * self.margin
        self.highlight.h = self.h - 2 * self.margin

    def refresh_layout(self):
        super().refresh_layout()
        self.highlight.pos = self.margin, self.margin

    def on_focus(self):
        self.cursor.activate()
        self._place_cursor_by_index(self._cursor_place, self._cursor_place.index)

    def on_unfocus(self):
        super().on_unfocus()
        self.cursor.deactivate()

    def on_mouse_down(self, pos, button, hovered):
        super().on_mouse_down(pos, button, hovered)
        if not pygame.key.get_mods() & pygame.KMOD_SHIFT:
            self._hl_cursor_place = None
        elif self._hl_cursor_place is None:
            self._hl_cursor_place = self._cursor_place.copy()

        self._place_cursor_by_pos(self._cursor_place, pos)

        # Shift-clicked where the cursor already is
        if self._hl_cursor_place is not None and self._hl_cursor_place == self._cursor_place:
            self._hl_cursor_place = None
        self.cursor.start()

    def on_mouse_motion(self, start, end, buttons, start_hovered, end_hovered):
        super().on_mouse_motion(start, end, buttons, start_hovered, end_hovered)
        if self.mouse_state == SimpleWidget.PRESS:
            started_highlighting = False
            if self._hl_cursor_place is None:
                started_highlighting = True
                self._hl_cursor_place = self._cursor_place.copy()
            self._place_cursor_by_pos(self._cursor_place, end)
            if started_highlighting and self._hl_cursor_place == self._cursor_place:
                self._hl_cursor_place = None

    def _handle_key(self, unicode, key, mod):
        prev_index = self._cursor_place.index
        if key in keyboard.navigation_keys:
            if self._hl_cursor_place is not None and not mod & pygame.KMOD_SHIFT:
                self._navigate_region(key, mod)
                self._hl_cursor_place = None
            else:
                self._navigate(key, mod)

            if not mod & pygame.KMOD_SHIFT:
                self._hl_cursor_place = None
            elif self._hl_cursor_place is None:
                self._hl_cursor_place = CursorPlacement()
                self._place_cursor_by_index(self._hl_cursor_place, prev_index)
            try:
                if self._hl_cursor_place.index == self._cursor_place.index:
                    self._hl_cursor_place = None
            except AttributeError:
                pass
        elif key in keyboard.editing_keys:
            if self._hl_cursor_place is None:
                index, text = _edit(self.text, self._cursor_place.index, unicode, key, mod)
            else:
                start = min(self._hl_cursor_place.index, self._cursor_place.index)
                end = max(self._hl_cursor_place.index, self._cursor_place.index)
                index, text = _edit_region(self.text, start, end, unicode, key, mod)
                self._hl_cursor_place = None
            if self.set_text(text):
                if index != self._cursor_place.index:
                    self._place_cursor_by_index(self._cursor_place, index)
        self.cursor.start()

    def on_key_down(self, unicode, key, mod):
        super().on_key_down(unicode, key, mod)
        self._handle_key(unicode, key, mod)

    def handle_message(self, sender, message, **params):
        if message == TextEntryBox.MSG_UNDO:
            pass  # TODO: Undo
        elif message == TextEntryBox.MSG_CUT:
            self.handle_message(sender, TextEntryBox.MSG_COPY, **params)
            self._handle_key(None, pygame.K_DELETE, 0)
        elif message == TextEntryBox.MSG_COPY:
            if self._hl_cursor_place is not None:
                left, right = self._hl_cursor_place, self._cursor_place
                if left > right:
                    left, right = right, left
                pyperclip.copy(self.text[left.index:right.index])
        elif message == TextEntryBox.MSG_PASTE:
            self._handle_key(pyperclip.paste(), None, 0)
        elif message == TextEntryBox.MSG_HIGHLIGHT_ALL:
            self._hl_cursor_place = CursorPlacement()
            self._place_cursor_by_index(self._hl_cursor_place, 0)
            self._place_cursor_by_index(self._cursor_place, len(self.text))
        else:
            super().handle_message(sender, message, **params)

    def _navigate(self, key, mod):
        cursor = self._cursor_place

        if key == pygame.K_DOWN:
            if cursor.row < self._num_active_lines - 1:
                self._place_cursor_by_pos(cursor, (cursor.raw_x, cursor.raw_y + self.line_height))
        elif key == pygame.K_UP:
            if cursor.row > 0:
                self._place_cursor_by_pos(cursor, (cursor.raw_x, cursor.raw_y - self.line_height))

        elif key == pygame.K_LEFT:
            if mod & pygame.KMOD_CTRL:
                self._place_cursor_by_index(cursor, _backwards_word(self.text, cursor.index))
            elif cursor.index > 0:
                self._place_cursor_by_index(cursor, cursor.index - 1)
        elif key == pygame.K_RIGHT:
            if mod & pygame.KMOD_CTRL:
                self._place_cursor_by_index(cursor, _forwards_word(self.text, cursor.index))
            elif cursor.index < len(self.text):
                self._place_cursor_by_index(cursor, cursor.index + 1)

        elif key == pygame.K_HOME:
            if mod & pygame.KMOD_CTRL:
                self._place_cursor_by_index(cursor, 0)
            else:
                self._place_cursor_by_index(cursor, cursor.index - cursor.col)
        elif key == pygame.K_END:
            if mod & pygame.KMOD_CTRL:
                self._place_cursor_by_index(cursor, len(self.text))
            else:
                self._place_cursor_by_index(cursor, cursor.index + len(self.lines[cursor.row].text) - cursor.col)

    def _navigate_region(self, key, mod):
        cursor = self._cursor_place

        if key == pygame.K_DOWN:
            if cursor.row < self._num_active_lines - 1:
                self._place_cursor_by_pos(cursor, (cursor.raw_x, cursor.raw_y + self.line_height))
        elif key == pygame.K_UP:
            if cursor.row > 0:
                self._place_cursor_by_pos(cursor, (cursor.raw_x, cursor.raw_y - self.line_height))

        elif key == pygame.K_LEFT:
            self._place_cursor_by_index(cursor, min(cursor.index, self._hl_cursor_place.index))
        elif key == pygame.K_RIGHT:
            self._place_cursor_by_index(cursor, max(cursor.index, self._hl_cursor_place.index))

        elif key == pygame.K_HOME:
            if mod & pygame.KMOD_CTRL:
                self._place_cursor_by_index(cursor, 0)
            else:
                self._place_cursor_by_index(cursor, cursor.index - cursor.col)
        elif key == pygame.K_END:
            if mod & pygame.KMOD_CTRL:
                self._place_cursor_by_index(cursor, len(self.text))
            else:
                self._place_cursor_by_index(cursor, cursor.index + len(self.lines[cursor.row].text) - cursor.col)

        self.cursor.start()

    def _place_cursor_by_pos(self, cursor, pos):
        # Raw x, y is given
        cursor.raw_x, cursor.raw_y = pos

        # Set row to `rel_y // line_height`, bounded between `0` and `len(lines) - 1`
        cursor.row = min(max((cursor.raw_y - self.margin) // self.line_height, 0), self._num_active_lines - 1)

        # Binary search to find which column was clicked on
        col = 0
        hi = len(self.lines[cursor.row].text)
        while col < hi:
            mid = (col + hi) // 2
            metrics = self.font.get_metrics(self.lines[cursor.row].text[mid])[0]
            pivot = self._grid_pos(cursor.row, mid)[0] + (metrics[0] + metrics[1]) // 2
            if cursor.raw_x > pivot:
                col = mid + 1
            else:
                hi = mid
        cursor.col = col

        cursor.index = self._grid_index(cursor.row, cursor.col)
        cursor.pos = self._grid_pos(cursor.row, cursor.col)

    def _place_cursor_by_index(self, cursor, index):
        # Index is given
        cursor.index = index

        length = 0
        for row, line in enumerate(self.lines[:self._num_active_lines]):
            length += len(line.text)
            if length >= index:
                length -= len(line.text)
                cursor.row = row
                break
            length += (row < self._num_active_lines - 1 and self.text[length].isspace())
        else:
            cursor.row = self._num_active_lines - 1
        cursor.col = index - length

        cursor.raw_x, cursor.raw_y = cursor.pos = self._grid_pos(cursor.row, cursor.col)

    # TODO: Go over all the on_tick (& tick, & tick_hook) methods. Maybe they no longer match the intended purpose.
    # TODO: Implement some kind of notion of "focus"
    # def on_tick(self, elapsed):
    #     super().on_tick(elapsed)
    #     if self.is_focused:
    #         if self._hl_cursor_place is not None:
    #             if not self.highlight.is_visible:
    #                 self.highlight.activate()
    #                 self.cursor.deactivate()
    #             left, right = self._hl_cursor_place, self._cursor_place
    #             if left > right:
    #                 left, right = right, left
    #             if self.highlight.start != left.pos or self.highlight.end != right.pos:
    #                 self.highlight.start = left.x - self.margin, left.y - self.margin
    #                 self.highlight.end = right.x - self.margin, right.y - self.margin
    #                 self.highlight.refresh_background_flag = True
    #             else:
    #                 self.highlight.start = left.x - self.margin, left.y - self.margin
    #                 self.highlight.end = right.x - self.margin, right.y - self.margin
    #         elif self.highlight.is_visible:
    #             self.highlight.deactivate()
    #             self.cursor.activate()
    #         self.cursor.midtop = self._cursor_place.pos


class TextField(TextEntryBox):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_key_down(self, unicode, key, mod):
        if key == pygame.K_RETURN and not mod & pygame.KMOD_SHIFT:
            self.send_message('text-entry', text=self.text)
        else:
            super().on_key_down(unicode, key, mod)
