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


class Gradient(TimingComponent):
    def __init__(self, message, start, end):
        super().__init__()
        self.message = message

        self.start = start
        self.end = end
        self._gap = start - end
        self.value = start

    def on_time_elapsed(self, before, after, elapsed):
        super().on_time_elapsed(before, after, elapsed)
        if after <= self.duration:
            self.value = self.start + self._gap * after / self.duration
        elif after > self.duration:
            self.value = self.end
            self.send_message(self.message)
