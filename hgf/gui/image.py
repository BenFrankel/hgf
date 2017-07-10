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

from .component import GraphicalComponent


class Image(GraphicalComponent):
    def __init__(self, image_name):
        super().__init__(hover=False, click=False)
        self._image = None
        self.image_name = image_name

    def load_hook(self):
        self.image = self._app.get_image(self.image_name)

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, other):
        self.image = other
        self.background = self.image
