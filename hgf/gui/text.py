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


from .base import StructuralComponent


class Text(StructuralComponent):
    def __init__(self, text='', font=None, fontsize=14, fgcolor=None):
        super().__init__(0, 0, hover=False, click=False)
        self._text = text
        self._font = font
        self._fontsize = fontsize
        self._font = font
        self.fgcolor = (0, 0, 0) if fgcolor is None else fgcolor

    def load_style_hook(self):
        self._font = self.style_get('font')

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, other):
        if self._text != other:
            self._text = other
            self.refresh()

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, other):
        if self._font != other:
            self._font = other
            self.refresh()

    @property
    def fontsize(self):
        return self._fontsize

    @fontsize.setter
    def fontsize(self, other):
        if self._fontsize != other:
            self._fontsize = other
            self.refresh()

    def get_metrics(self):
        return self.font.get_metrics(self.text, self.fontsize)

    def get_rect(self, text=None):
        return self.font.get_rect(self.text if text is None else text, size=self.fontsize)

    def refresh(self):
        self.background = self.font.render(self.text, fgcolor=self.fgcolor, size=self.fontsize)[0]

    def __str__(self):
        return self.text

    def __repr__(self):
        return 'Text(\'{}\')'.format(self.text)


class TextBox(StructuralComponent):
    def __init__(self, w, h, text='', justify='left', margin=3, **kwargs):
        super().__init__(w, h, **kwargs)
        self.type = 'text-box'

        self.margin = margin
        self.justify = justify
        self.font = None
        self.fgcolor = None

        self.line_height = None
        self.text = text
        self.lines = []

        self._bg_factory = None

    def load_style_hook(self):
        self.font = self.style_get('font')
        self.font.size = self.options_get('font-size')
        self.line_height = self.font.get_sized_height()
        self.fgcolor = self.style_get('fg-color')
        self.set_text(self.text)
        self._bg_factory = self.style_get('background')

    def _wrap_paragraph(self, text):
        if text == '':
            return ['']

        w = self.w - 2 * self.margin

        words = text.split(' ')
        lines = []
        line = ''
        for i, word in enumerate(words):
            if i != len(words) - 1:
                word = word + ' '
            # If the unit won't fit on the current line
            if self.font.get_rect(line + word).w > w:
                if self.font.get_rect(word).w <= w:
                    lines.append(line)
                    line = word
                # If the unit won't even fit alone on a line, it must be split
                else:
                    if line:
                        lines.append(line)
                    while self.font.get_rect(word).w > w:
                        lo = 0
                        hi = len(word)
                        while lo < hi:
                            mid = (lo + hi) // 2
                            if w < self.font.get_rect(word[:mid]).w:
                                hi = mid
                            else:
                                lo = mid + 1
                        lines.append(word[:lo - 1])
                        word = word[lo - 1:]
                    line = word
            else:
                line += word

        # Trim a single trailing space from each word wrapped line
        for i, l in enumerate(lines):
            if l[-1] == ' ':
                lines[i] = l[:-1]

        # Append last line
        if line:
            lines.append(line)

        return lines

    def _wrap(self, text):
        # Handle newlines recursively
        return [line for paragraph in text.split('\r') for line in self._wrap_paragraph(paragraph)]

    def set_text(self, text):
        lines = self._wrap(text)
        if len(lines) > (self.h - 2 * self.margin) // self.line_height:
            return False
        while len(self.lines) > len(lines):
            self.unregister(self.lines[-1])
            del self.lines[-1]
        while len(lines) > len(self.lines):
            self.lines.append(Text(font=self.font, fontsize=self.font.size, fgcolor=self.fgcolor))
            self.register_load(self.lines[-1])
        for old_line, line in zip(self.lines, lines):
            old_line.text = line
        self.text = text
        return True

    def _row_height(self, row):
        return self.margin + row * self.line_height

    def _grid_pos(self, row, col):
        line = self.lines[row]

        if col < len(line.text) and not line.text[col].isspace():
            off = self.font.get_rect(line.text[:col + 1]).w - self.font.get_metrics(line.text[col])[0][4]
        else:
            off = self.font.get_rect(line.text[:col]).w

        if self.justify == 'left':
            return self.margin + off, self._row_height(row)
        elif self.justify == 'right':
            line_w = self.font.get_rect(line.text).w
            return off + self.w - self.margin - line_w, self._row_height(row)
        elif self.justify == 'center':
            line_w = self.font.get_rect(line.text).w
            return self.w / 2 - line_w / 2 + off, self._row_height(row)

    def _grid_index(self, row, col):
        return sum(len(line.text) + 1 for line in self.lines[:row]) + col

    def tick_hook(self):
        y = self.margin
        for line in self.lines:
            if self.justify == 'left':
                line.left = self.margin
            elif self.justify == 'center':
                line.left = (self.w - self.font.get_rect(line.text).w) / 2
            elif self.justify == 'right':
                line.right = self.w - self.margin
            line.y = y
            y += self.line_height
        super().tick_hook()

    def refresh(self):
        self.background = self._bg_factory(self.size, self.margin)
