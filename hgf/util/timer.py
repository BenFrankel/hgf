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


# TODO: Handle negative time properly
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
        self._d = 0
        self._h = 0
        self._m = 0
        self._s = 0
        self._ms = 0

        self.d += d
        self.h += h
        self.m += m
        self.s += s
        self.ms += ms

    @property
    def d(self):
        return self._d

    @d.setter
    def d(self, days):
        self._d = int(days)
        h = (days % 1) * 24
        if h != 0:
            self.h += h

    @property
    def h(self):
        return self._h

    @h.setter
    def h(self, hours):
        self._h = int(hours % 24)
        m = (hours % 1) * 60
        if m != 0:
            self.m += m
        d = hours // 24
        if d != 0:
            self.d += d

    @property
    def m(self):
        return self._m

    @m.setter
    def m(self, minutes):
        self._m = int(minutes % 60)
        s = (minutes % 1) * 60
        if s != 0:
            self.s += s
        h = minutes // 60
        if h != 0:
            self.h += h

    @property
    def s(self):
        return self._s

    @s.setter
    def s(self, seconds):
        self._s = int(seconds % 60)
        ms = (seconds % 1) * 1000
        if ms != 0:
            self.ms += ms
        m = seconds // 60
        if m != 0:
            self.m += m

    @property
    def ms(self):
        return self._ms

    @ms.setter
    def ms(self, milliseconds):
        self._ms = int(milliseconds % 1000)
        s = milliseconds // 1000
        if s != 0:
            self.s += s

    def in_d(self):
        return self.in_ms() / 86400000

    def in_h(self):
        return self.in_ms() / 3600000

    def in_m(self):
        return self.in_ms() / 60000

    def in_s(self):
        return self.in_ms() / 1000

    def in_ms(self):
        return self.ms + (1000 * self.s) + (60000 * self.m) + (3600000 * self.h) + (86400000 * self.d)

    def __add__(self, other):
        return Time(self.d + other.d,
                    self.h + other.h,
                    self.m + other.m,
                    self.s + other.s,
                    self.ms + other.ms)

    def __sub__(self, other):
        return Time(self.d - other.d,
                    self.h - other.h,
                    self.m - other.m,
                    self.s - other.s,
                    self.ms - other.ms)

    def __mul__(self, other):
        return Time(self.d * other,
                    self.h * other,
                    self.m * other,
                    self.s * other,
                    self.ms * other)

    def __floordiv__(self, other):
        try:
            return self.in_ms() // other.in_ms()
        except KeyError:
            return Time(ms=self.in_ms() // other)

    def __mod__(self, other):
        return Time(ms=self.in_ms() % other.in_ms())

    def __lt__(self, other):
        return (self.d, self.h, self.m, self.s, self.ms) < (other.d, other.h, other.m, other.s, other.ms)

    def __gt__(self, other):
        return (self.d, self.h, self.m, self.s, self.ms) > (other.d, other.h, other.m, other.s, other.ms)

    def __str__(self):
        if self < Time(m=1):
            return '{}.{:03d}'.format(self.s, self.ms)
        elif self < Time(h=1):
            return '{}:{:02d}.{:03d}'.format(self.m, self.s, self.ms)
        elif self < Time(d=1):
            return '{}:{:02d}:{:02d}.{:03d}'.format(self.h, self.m, self.s, self.ms)
        else:
            return '{} day{}, {}:{:02d}:{:02d}.{:03d}'.format(self.d, '' if self.d == 1 else 's', self.h, self.m, self.s, self.ms)

    def __repr__(self):
        return 'Time(d={}, h={}, m={}, s={}, ms={})'.format(self.d, self.h, self.m, self.s, self.ms)


class Timer:
    def __init__(self):
        self._last_time = None
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
