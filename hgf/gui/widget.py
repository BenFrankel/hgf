from .base import StructuralComponent
from ..util import Time, Timer, CountdownTimer

import pygame


class SimpleWidget(StructuralComponent):
    IDLE = 0
    HOVER = 1
    PUSH = 2
    PRESS = 3
    PULL = 4

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mouse_state = SimpleWidget.IDLE

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

    def mouse_state_change_hook(self, before, after):
        pass

    def pause_hook(self):
        self.mouse_state = SimpleWidget.IDLE

    def mouse_enter_hook(self, start, end, buttons):
        if self.is_visible:
            if self.mouse_state == SimpleWidget.IDLE:
                if buttons[0]:
                    self.mouse_state = SimpleWidget.PUSH
                else:
                    self.mouse_state = SimpleWidget.HOVER
            elif self.mouse_state == SimpleWidget.PULL:
                self.mouse_state = SimpleWidget.PRESS

    def mouse_exit_hook(self, start, end, buttons):
        if self.is_visible:
            if self.mouse_state == SimpleWidget.HOVER or self.mouse_state == SimpleWidget.PUSH:
                self.mouse_state = SimpleWidget.IDLE
            elif self.mouse_state == SimpleWidget.PRESS:
                self.mouse_state = SimpleWidget.PULL

    def mouse_down_hook(self, pos, button):
        if button == 1 and self.is_visible:
            if self.mouse_state != SimpleWidget.HOVER:
                self.mouse_state = SimpleWidget.HOVER
            self.mouse_state = SimpleWidget.PRESS

    def mouse_up_hook(self, pos, button):
        if button == 1 and self.is_visible:
            if self.mouse_state == SimpleWidget.PRESS or self.mouse_state == SimpleWidget.PUSH:
                self.mouse_state = SimpleWidget.HOVER
            elif self.mouse_state == SimpleWidget.PULL:
                self.mouse_state = SimpleWidget.IDLE

    def track_hook(self):
        if self.is_visible and self.mouse_state == SimpleWidget.PULL and not pygame.mouse.get_pressed()[0]:
            self.mouse_state = SimpleWidget.IDLE


# TODO: Long key press
# TODO: Long mouse hover
# TODO: Repeated mouse clicks (double click, etc)
# TODO: Drag hook?
# TODO: Scroll hook?
#
class Widget(SimpleWidget):
    LONG_PRESS_DELAY = Time(ms=400)
    LONG_PRESS_RATE = Time(ms=40)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._long_press_delay = Timer()
        self._long_press_rate = CountdownTimer()
        self._last_pressed = None

    def key_down_hook(self, unicode, key, mod):
        # Prevent self-interference when long press calls key down
        if self._last_pressed is None or self._last_pressed[1] != key:
            self._long_press_delay.start()
            self._last_pressed = (unicode, key, mod)

    def key_up_hook(self, key, mod):
        self._long_press_delay.reset()
        self._last_pressed = None

    def tick_hook(self):
        if self._long_press_delay.time > Widget.LONG_PRESS_DELAY:
            if not self._long_press_rate.is_running:
                self._long_press_rate.start(Widget.LONG_PRESS_RATE)
                self._key_down(*self._last_pressed)
