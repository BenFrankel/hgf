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

from .drag import SlideWidget
from .widget import SimpleWidget
from .component import GraphicalComponent


# TODO
class Scrollbar(SimpleWidget):
    def __init__(self, length=0.5, **kwargs):
        super().__init__(**kwargs)
        self.type = 'scrollbar'

        self._drag_bar = None
        self._drag_bar_length = length

    def load_hook(self):
        self._drag_bar = SlideWidget(w=self.w, h=self._drag_bar_length)
        rel = self.rel_rect()
        self._drag_bar.set_axis(rel.midtop, rel.midbottom)


# TODO
class Frame(GraphicalComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


# TODO
# class TextFrame
