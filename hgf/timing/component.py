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
from ..util import Time


class TimingComponent(Component):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time = None
        self.duration = None
        self.is_running = False

    def on_time_elapsed(self, before, after, elapsed): pass

    def trigger(self): pass

    def start(self, duration=None):
        self.time = Time()
        self.duration = duration
        self.is_running = True
        self.unpause()

    def reset(self):
        self.time = None
        self.duration = None
        self.is_running = False

    def on_tick(self, elapsed):
        super().on_tick(elapsed)
        if not self.is_running:
            return

        before = self.time.copy()
        self.time.ms += elapsed

        if self.duration is not None and self.time >= self.duration:
            self.is_running = False
            self.reset()
        else:
            self.on_time_elapsed(before, self.time, elapsed)

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self.time)
