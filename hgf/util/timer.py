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

import time
import functools


@functools.total_ordering
class Time:
    @staticmethod
    def now():
        return Time(s=time.monotonic())

    @staticmethod
    def parse(text):
        result = Time()
        chunks = text.split(':', 2)

        secs = chunks[-1].split('.', 1)
        result.s = int(secs[0])
        try:
            result.ms = int(secs[1])
        except IndexError:
            pass

        try:
            result.m = int(chunks[-2])
        except IndexError:
            pass

        try:
            hours = chunks[-3]
            try:
                d, _, h = hours.split(' ', 2)
                result.d = int(d)
                result.h = int(h)
            except KeyError:
                pass
        except IndexError:
            pass

        return result

    def __init__(self, d=0, h=0, m=0, s=0, ms=0):
        self._t = 0

        self.d = d
        self.h = h
        self.m = m
        self.s = s
        self.ms = ms

    @property
    def d(self):
        return self._t // 86_400_000

    @d.setter
    def d(self, days):
        self._t += int((days - self.d) * 86_400_000)

    @property
    def h(self):
        return (self._t // 3_600_000) % 24

    @h.setter
    def h(self, hours):
        self._t += int((hours - self.h) * 3_600_000)

    @property
    def m(self):
        return (self._t // 60_000) % 60

    @m.setter
    def m(self, minutes):
        self._t += int((minutes - self.m) * 60_000)

    @property
    def s(self):
        return (self._t // 1000) % 60

    @s.setter
    def s(self, seconds):
        self._t += int((seconds - self.s) * 1000)

    @property
    def ms(self):
        return self._t % 1000

    @ms.setter
    def ms(self, milliseconds):
        self._t += int(milliseconds - self.ms)

    def in_d(self):
        return self._t / 86400000

    def in_h(self):
        return self._t / 3600000

    def in_m(self):
        return self._t / 60000

    def in_s(self):
        return self._t / 1000

    def in_ms(self):
        return self._t

    def copy(self):
        return Time(d=self.d, h=self.h, m=self.m, s=self.s, ms=self.ms)

    def __add__(self, other):
        return Time(ms=self._t + other._t)

    def __neg__(self):
        return Time(ms=-self._t)

    def __sub__(self, other):
        return Time(ms=self._t - other._t)

    def __mul__(self, other):
        return Time(ms=self._t * other)

    def __floordiv__(self, other):
        try:
            return self._t // other._t
        except AttributeError:
            return Time(ms=self._t // other)

    def __mod__(self, other):
        return Time(ms=self._t % other._t)

    def __lt__(self, other):
        return self._t < other._t

    def __gt__(self, other):
        return self._t > other._t

    def __str__(self):
        if self._t < 0:
            return 'negative {}'.format(-self)
        if self._t < 60_000:
            return '{}.{:03d}'.format(self.s, self.ms)
        elif self._t < 3_600_000:
            return '{}:{:02d}.{:03d}'.format(self.m, self.s, self.ms)
        elif self._t < 86_400_000:
            return '{}:{:02d}:{:02d}.{:03d}'.format(self.h, self.m, self.s, self.ms)
        else:
            d = self.d
            return '{} day{}, {}:{:02d}:{:02d}.{:03d}'.format(d, '' if d == 1 else 's', self.h, self.m, self.s, self.ms)

    def __repr__(self):
        if self._t < 0:
            neg = -self
            return 'Time(d={}, h={}, m={}, s={}, ms={})'.format(-neg.d, -neg.h, -neg.m, -neg.s, -neg.ms)
        return 'Time(d={}, h={}, m={}, s={}, ms={})'.format(self.d, self.h, self.m, self.s, self.ms)


class Timer:
    def __init__(self):
        self._last_time = None
        self.last_updated = Time()
        self._time = Time()
        self._is_paused = True

    @property
    def time_paused(self):
        if self.is_paused:
            return Time.now() - self._last_time
        return Time()

    @property
    def time(self):
        if self._is_paused:
            return self._time
        self.update()
        return self._time

    @time.setter
    def time(self, other):
        self._time = other

    @property
    def is_paused(self):
        if self._is_paused:
            return True
        self.update()
        return self._is_paused

    @is_paused.setter
    def is_paused(self, other):
        self._is_paused = other

    @property
    def is_running(self):
        return not self.is_paused

    @is_running.setter
    def is_running(self, other):
        self._is_paused = not other

    def start(self, start_time=Time()):
        self.time = start_time
        self._last_time = Time.now()
        self._is_paused = False

    def update(self):
        if not self._is_paused:
            current_time = Time.now()
            self._time += current_time - self._last_time
            self.last_updated = self._time
            self._last_time = current_time

    def pause(self):
        self.update()
        self._is_paused = True

    def unpause(self):
        self._last_time = Time.now()
        self._is_paused = False

    def reset(self):
        self._last_time = None
        self.time = Time()
        self._is_paused = True

    def __str__(self):
        return '{}({}, is_running={})'.format(self.__class__.__name__, self.time, self.is_running)


class CountdownTimer(Timer):
    def update(self):
        if not self._is_paused:
            current_time = Time.now()
            self._time -= current_time - self._last_time
            self._last_time = current_time
            if self._time < Time():
                self.reset()
