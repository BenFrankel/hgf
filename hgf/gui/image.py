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

from ..double_buffer import double_buffer
from .component import FlatComponent


class Image(FlatComponent):
    def __init__(self, image_name):
        super().__init__(hover=False, click=False)
        self.image_name = image_name

    @double_buffer
    class image_name:
        def on_transition(self):
            self.refresh_background_flag = True

    def refresh_background(self):
        self.background = self._app.get_image(self.image_name)
