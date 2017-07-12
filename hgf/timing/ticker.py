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

from .component import TimingComponent
from ..util import Time


class Ticker(TimingComponent):
    def __init__(self, message):
        super().__init__()
        self.message = message

    def trigger(self):
        self.send_message(self.message)


class Pulse(Ticker):
    def __init__(self, *args, period=Time(s=1)):
        super().__init__(*args)
        self.period = period

    def time_shift_hook(self, before, after):
        num = after // self.period - before // self.period
        for _ in range(num):
            self.trigger()


class Delay(Ticker):
    def __init__(self, *args, delay=Time(s=1)):
        super().__init__(*args)
        self.delay = delay

    def time_shift_hook(self, before, after):
        if after > self.delay:
            self.trigger()
            self.reset()
