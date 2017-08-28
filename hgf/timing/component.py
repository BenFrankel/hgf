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

from ..component import Component
from ..util import Timer, CountdownTimer


class TimingComponent(Component):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._duration = None
        self._expiration_timer = CountdownTimer()

        self._timer = Timer()
        self.is_running = False

    @property
    def time(self):
        return self._timer.time

    def time_shift_hook(self, before, after): pass

    def trigger(self): pass

    def freeze_hook(self):
        self._timer.pause()
        self._expiration_timer.pause()

    def unfreeze_hook(self):
        self._timer.unpause()
        self._expiration_timer.unpause()

    def start(self, duration=None):
        if not self.is_frozen:
            self.is_running = True
            self.unpause()
            self._timer.start()
            self._duration = duration
            if duration is not None:
                self._expiration_timer.start(duration)

    def reset(self):
        if not self.is_frozen:
            self.is_running = False
            self._timer.reset()
            self._expiration_timer.reset()

    def tick_hook(self):
        if self.is_running:
            if self._duration is not None and self._expiration_timer.is_paused:
                self.is_running = False
                self.time_shift_hook(self._timer.last_updated, self._duration)
                self.reset()
            else:
                self.time_shift_hook(self._timer.last_updated, self._timer.time)

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self._timer.time)
