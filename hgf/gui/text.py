#!/usr/bin/env python

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


from . import base


class Text(base.Entity):
    def __init__(self, text='', font=None, fontsize=1, fgcolor=None):
        super().__init__(0, 0, hoverable=False, clickable=False)
        self._text = text
        self._font = font
        self._fontsize = fontsize
        self._font = font
        self.fgcolor = fgcolor
        if fgcolor is None:
            self.fgcolor = (0, 0, 0)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, other):
        if self._text != other:
            self._text = other
            self.reload()

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, other):
        if self._font != other:
            self._font = other
            self.reload()

    @property
    def fontsize(self):
        return self._fontsize

    @fontsize.setter
    def fontsize(self, other):
        if self._fontsize != other:
            self._fontsize = other
            self.reload()

    def reload(self):
        if self._font is None:
            self._font = self.style_get('font')
        self.background = self.font.render(self.text, fgcolor=self.fgcolor, size=self.fontsize)[0]
