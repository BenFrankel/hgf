from .menu import Widget
from .text import TextBox
from .base import StructuralComponent
from ..util import Time, Timer, CountdownTimer

import pygame

import functools


def backwards_word(s, index):
    start = index - 1
    while start >= 0 and not s[start].isalnum():
        start -= 1
    while start >= 0 and s[start].isalnum():
        start -= 1
    return start + 1


def forwards_word(s, index):
    end = index
    while end < len(s) and not s[end].isalnum():
        end += 1
    while end < len(s) and s[end].isalnum():
        end += 1
    return end


def edit(text, index, unicode, key, mod):
    if key == pygame.K_BACKSPACE:
        if index == 0:
            return index, text
        if mod & pygame.KMOD_CTRL:
            start = backwards_word(text, index)
            return start, text[:start] + text[index:]
        return index - 1, text[:index - 1] + text[index:]
    if key == pygame.K_DELETE:
        if index == len(text):
            return index, text
        if mod & pygame.KMOD_CTRL:
            end = forwards_word(text, index)
            return index, text[:index] + text[end:]
        return index, text[:index] + text[index + 1:]

    if unicode == '\t':
        unicode = '    '
    return index + len(unicode), text[:index] + unicode + text[index:]


def edit_region(text, start, end, unicode, key, mod):
    if key == pygame.K_BACKSPACE or key == pygame.K_DELETE:
        return start, text[:start] + text[end:]

    if unicode == '\t':
        unicode = '    '

    return start + len(unicode), text[:start] + unicode + text[end:]


class Cursor(StructuralComponent):
    BLINK_RATE = Time(ms=500)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = 'cursor'
        self.timer = CountdownTimer()

    def pause_hook(self):
        self.timer.pause()

    def unpause_hook(self):
        self.timer.unpause()

    def activate_hook(self):
        self.timer.start(Cursor.BLINK_RATE)

    def restart(self):
        if not self.is_paused:
            self.timer.restart(Cursor.BLINK_RATE)
            self.show()

    def tick_hook(self):
        if not self.timer.is_running:
            self.toggle_show()
            self.timer.start(Cursor.BLINK_RATE)

    def refresh(self):
        self.background = self.style_get('background')(self.size)


class Highlight(StructuralComponent):
    def __init__(self, line_height, w, h, **kwargs):
        super().__init__(w, h, **kwargs)
        self.line_height = line_height
        self.start = (0, 0)
        self.end = (0, 0)
        self.bgcolor = None

    def refresh(self):
        surf = pygame.Surface(self.size, pygame.SRCALPHA)
        if self.start[1] == self.end[1]:
            pygame.draw.rect(surf,
                             self.bgcolor,
                             pygame.Rect(self.start[0],
                                         self.start[1],
                                         self.end[0] - self.start[0],
                                         self.line_height))
        else:
            pygame.draw.rect(surf,
                             self.bgcolor,
                             pygame.Rect(self.start[0],
                                         self.start[1],
                                         self.w - self.start[0],
                                         self.line_height))
            inbetween = (self.end[1] - self.start[1]) // self.line_height - 1
            if inbetween > 0:
                pygame.draw.rect(surf,
                                 self.bgcolor,
                                 pygame.Rect(0,
                                             self.start[1] + self.line_height,
                                             self.w,
                                             self.line_height * inbetween))
            pygame.draw.rect(surf,
                             self.bgcolor,
                             pygame.Rect(0,
                                         self.end[1],
                                         self.end[0],
                                         self.line_height))
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

    def copy(self):
        return CursorPlacement(self.index, self.row, self.col, self.raw_x, self.raw_y, self.x, self.y)

    def __lt__(self, other):
        return self.index < other.index

    def __eq__(self, other):
        return self.index == other.index

    def __repr__(self):
        return 'CursorPlacement(index={}, row={}, col={}, raw_x={}, raw_y={}, x={}, y={})'\
            .format(self.index, self.row, self.col, self.raw_x, self.raw_y, self.x, self.y)

    __str__ = __repr__


# TODO: Copy & Paste
class TextEntryBox(TextBox, Widget):
    LONG_PRESS_DELAY = Time(ms=400)
    LONG_PRESS_RATE = Time(ms=40)

    NAVIGATE_KEYS = [
        pygame.K_LEFT,
        pygame.K_RIGHT,
        pygame.K_UP,
        pygame.K_DOWN,
        pygame.K_HOME,
        pygame.K_END,
    ]

    EDIT_KEYS = [
        pygame.K_BACKSPACE,
        pygame.K_DELETE,
    ]

    def __init__(self, w, h, **kwargs):
        super().__init__(w, h, focus=True, **kwargs)
        # Cursor
        self.cursor = None
        self.cursor_place = CursorPlacement()

        # Highlighting
        self.hl_cursor_place = None
        self.highlight = None

        # Long press
        self.long_press_delay = Timer()
        self.long_press_rate = CountdownTimer()
        self.last_pressed = None

    def load_hook(self):
        super().load_hook()
        self.cursor = Cursor(max(self.line_height // 10, 1), self.line_height)
        self.cursor.z = 10
        self.register_load(self.cursor)
        self.cursor.deactivate()

        self.highlight = Highlight(self.line_height, self.w - 2 * self.gap, self.h - 2 * self.gap)
        self.highlight.z = -10
        self.highlight.pos = self.gap, self.gap
        self.highlight.bgcolor = self.style_get('highlight-bgcolor')
        self.register_load(self.highlight)
        self.highlight.deactivate()

    def take_focus_hook(self):
        self.cursor.activate()
        self._place_cursor_by_index(self.cursor_place, self.cursor_place.index)

    def lose_focus_hook(self):
        self.cursor.deactivate()

    def mouse_down_hook(self, pos, button):
        super().mouse_down_hook(pos, button)

        if not pygame.key.get_mods() & pygame.KMOD_SHIFT:
            self.hl_cursor_place = None
        elif self.hl_cursor_place is None:
            self.hl_cursor_place = self.cursor_place.copy()

        self._place_cursor_by_pos(self.cursor_place, pos)

        # Shift-clicked where the cursor already is
        if self.hl_cursor_place is not None and self.hl_cursor_place == self.cursor_place:
            self.hl_cursor_place = None

        self.cursor.restart()

    def mouse_motion_hook(self, start, end, buttons):
        if self.widget_state == Widget.PRESS:
            started_highlighting = False
            if self.hl_cursor_place is None:
                started_highlighting = True
                self.hl_cursor_place = self.cursor_place.copy()
            self._place_cursor_by_pos(self.cursor_place, end)
            if started_highlighting and self.hl_cursor_place == self.cursor_place:
                self.hl_cursor_place = None
            self.cursor.restart()

    def key_down_hook(self, unicode, key, mod):
        self._handle_key_down(unicode, key, mod)

        self.long_press_delay.start()
        self.last_pressed = (unicode, key, mod)

    def key_up_hook(self, key, mod):
        self.long_press_delay.reset()
        self.last_pressed = None

    def _navigate(self, key, mod):
        cursor = self.cursor_place

        if key == pygame.K_DOWN:
            if cursor.row < len(self.lines) - 1:
                self._place_cursor_by_pos(cursor, (cursor.raw_x, cursor.raw_y + self.line_height))
        elif key == pygame.K_UP:
            if cursor.row > 0:
                self._place_cursor_by_pos(cursor, (cursor.raw_x, cursor.raw_y - self.line_height))

        elif key == pygame.K_LEFT:
            if mod & pygame.KMOD_CTRL:
                self._place_cursor_by_index(cursor, backwards_word(self.text, cursor.index))
            elif cursor.index > 0:
                self._place_cursor_by_index(cursor, cursor.index - 1)
        elif key == pygame.K_RIGHT:
            if mod & pygame.KMOD_CTRL:
                self._place_cursor_by_index(cursor, forwards_word(self.text, cursor.index))
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
        cursor = self.cursor_place

        if key == pygame.K_DOWN:
            if cursor.row < len(self.lines) - 1:
                self._place_cursor_by_pos(cursor, (cursor.raw_x, cursor.raw_y + self.line_height))
        elif key == pygame.K_UP:
            if cursor.row > 0:
                self._place_cursor_by_pos(cursor, (cursor.raw_x, cursor.raw_y - self.line_height))

        elif key == pygame.K_LEFT:
            self._place_cursor_by_index(cursor, min(cursor.index, self.hl_cursor_place.index))
        elif key == pygame.K_RIGHT:
            self._place_cursor_by_index(cursor, max(cursor.index, self.hl_cursor_place.index))

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

    def _handle_key_down(self, unicode, key, mod):
        prev_index = self.cursor_place.index
        if key in TextEntryBox.NAVIGATE_KEYS:
            if self.hl_cursor_place is not None and not mod & pygame.KMOD_SHIFT:
                self._navigate_region(key, mod)
                self.hl_cursor_place = None
            else:
                self._navigate(key, mod)
            if not mod & pygame.KMOD_SHIFT:
                self.hl_cursor_place = None

            elif self.hl_cursor_place is None:
                self.hl_cursor_place = CursorPlacement()
                self._place_cursor_by_index(self.hl_cursor_place, prev_index)
            elif self.hl_cursor_place.index == self.cursor_place.index:
                self.hl_cursor_place = None
        elif key in TextEntryBox.EDIT_KEYS or (unicode and (unicode.isprintable() or unicode.isspace())):
            if self.hl_cursor_place is None:
                index, text = edit(self.text, self.cursor_place.index, unicode, key, mod)
            else:
                start = min(self.hl_cursor_place.index, self.cursor_place.index)
                end = max(self.hl_cursor_place.index, self.cursor_place.index)
                index, text = edit_region(self.text, start, end, unicode, key, mod)
                self.hl_cursor_place = None
            if self.set_text(text):
                if index != self.cursor_place.index:
                    self._place_cursor_by_index(self.cursor_place, index)

        self.cursor.restart()

    def _place_cursor_by_pos(self, cursor, pos):
        # Raw x, y is given
        cursor.raw_x, cursor.raw_y = pos

        # Set row to `rel_y // line_height`, bounded between `0` and `len(lines) - 1`
        cursor.row = min(max((cursor.raw_y - self.gap) // self.line_height, 0), len(self.lines) - 1)

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
        cursor.x, cursor.y = self._grid_pos(cursor.row, cursor.col)

    def _place_cursor_by_index(self, cursor, index):
        # Index is given
        cursor.index = index

        length = 0
        for row, line in enumerate(self.lines):
            length += len(line.text)
            if length >= index:
                length -= len(line.text)
                cursor.row = row
                break
            length += (row < len(self.lines) - 1 and self.text[length].isspace())
        else:
            cursor.row = len(self.lines) - 1
        cursor.col = index - length

        cursor.raw_x, cursor.raw_y = cursor.x, cursor.y = self._grid_pos(cursor.row, cursor.col)

    def tick_hook(self):
        if self.is_focused:
            if self.long_press_delay.time > TextEntryBox.LONG_PRESS_DELAY:
                if not self.long_press_rate.is_running:
                    self.long_press_rate.start(TextEntryBox.LONG_PRESS_RATE)
                    self._handle_key_down(*self.last_pressed)
            if self.hl_cursor_place is not None:
                if not self.highlight.is_visible:
                    self.highlight.activate()
                    self.cursor.deactivate()
                left, right = self.cursor_place, self.hl_cursor_place
                if self.hl_cursor_place < self.cursor_place:
                    left, right = self.hl_cursor_place, self.cursor_place
                if self.highlight.start != (left.x, left.y) or self.highlight.end != (right.x, right.y):
                    self.highlight.start = left.x - self.gap, left.y - self.gap
                    self.highlight.end = right.x - self.gap, right.y - self.gap
                    self.highlight.refresh()
                else:
                    self.highlight.start = left.x - self.gap, left.y - self.gap
                    self.highlight.end = right.x - self.gap, right.y - self.gap
            elif self.highlight.is_visible:
                self.highlight.deactivate()
                self.cursor.activate()
            self.cursor.pos = self.cursor_place.x - self.cursor.w // 2, self.cursor_place.y
        super().tick_hook()
