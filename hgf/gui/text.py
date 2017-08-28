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
from .hook import transition


class Text(GraphicalComponent):
    def __init__(self, text='', font=None, fontsize=14, fgcolor=None, parent_style=False, **kwargs):
        super().__init__(hover=False, click=False, opacity=1, **kwargs)
        self.text = text
        self.font = font
        self.fontsize = fontsize
        self.font = font
        self.fgcolor = (0, 0, 0) if fgcolor is None else fgcolor
        self._parent_style = parent_style

    def layout_hook(self):
        self.size = self.get_rect().size

    def load_style(self):
        if self._parent_style:
            self.font = self.parent.style_get('font')
        else:
            self.font = self.style_get('font')

    def refresh(self):
        self.background = self.font.render(self.text, fgcolor=self.fgcolor, size=self.fontsize)[0]

    @transition
    def text(self):
        self.size = self.get_rect().size

    @transition
    def font(self):
        self.size = self.get_rect().size

    @transition
    def fontsize(self):
        self.size = self.get_rect().size

    @transition
    def fgcolor(self):
        self.is_stale = True

    def get_metrics(self):
        return self.font.get_metrics(self.text, self.fontsize)

    def get_rect(self, text=None):
        return self.font.get_rect(self.text if text is None else text, size=self.fontsize)

    def __repr__(self):
        return 'Text(\'{}\')'.format(self.text)

    __str__ = __repr__


class TextBox(GraphicalComponent):
    def __init__(self, text='', justify='left', margin=3, **kwargs):
        super().__init__(opacity=1, **kwargs)
        self.type = 'text-box'
        self._bg_factory = None

        self.margin = margin
        self.justify = justify
        self.font = None
        self.fgcolor = None

        self.text = text

        self.line_height = None
        self.lines = []
        self._num_active_lines = 1

    def load_style(self):
        self.font = self.style_get('font')
        self.font.size = self.options_get('font-size')
        self.line_height = self.font.get_sized_height()
        self.fgcolor = self.style_get('fg-color')
        self._bg_factory = self.style_get('background')

    def refresh(self):
        self.background = self._bg_factory(self.size, self.margin)
        self.set_text(self.text)
        for line in self.lines:
            line.font = self.font
            line.fgcolor = self.fgcolor

    def layout_hook(self):
        self.lines = [Text('', parent_style=True) for _ in range((self.h - 2 * self.margin) // self.line_height)]
        self.register_prepare(*self.lines)
        self.set_text(self.text)

    @transition
    def justify(self, after):
        y = self.margin
        for line in self.lines:
            if after == 'left':
                line.left = self.margin
            elif after == 'center':
                line.midx = self.relmidx
            else:
                line.right = self.relright - self.margin
            line.y = y
            y += self.line_height

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
        if len(lines) > len(self.lines):
            return False
        self._num_active_lines = len(lines)
        for old_line, new_line_text in zip(self.lines, lines):
            old_line.text = new_line_text
        for old_line in self.lines[len(lines):]:
            old_line.text = ''
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
