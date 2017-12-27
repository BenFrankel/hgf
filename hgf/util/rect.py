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

import pygame


class Rect:
    def __init__(self, x=0, y=0, w=0, h=0, **kwargs):
        # Multiple inheritance compatibility
        super().__init__(**kwargs)
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @property
    def size(self):
        return self.w, self.h

    @size.setter
    def size(self, other):
        self.w, self.h = other

    @property
    def pos(self):
        return self.x, self.y

    @pos.setter
    def pos(self, other):
        self.x, self.y = other

    topleft = pos

    @property
    def left(self):
        return self.x

    @left.setter
    def left(self, other):
        self.x = other

    @property
    def top(self):
        return self.y

    @top.setter
    def top(self, other):
        self.y = other

    @property
    def midx(self):
        return self.x + self.w // 2

    @midx.setter
    def midx(self, other):
        self.x = other - self.w // 2

    @property
    def right(self):
        return self.x + self.w

    @right.setter
    def right(self, other):
        self.x = other - self.w

    @property
    def midy(self):
        return self.y + self.h // 2

    @midy.setter
    def midy(self, other):
        self.y = other - self.h // 2

    @property
    def bottom(self):
        return self.y + self.h

    @bottom.setter
    def bottom(self, other):
        self.y = other - self.h

    @property
    def midtop(self):
        return self.midx, self.top

    @midtop.setter
    def midtop(self, other):
        self.midx, self.top = other

    @property
    def topright(self):
        return self.right, self.top

    @topright.setter
    def topright(self, other):
        self.right, self.top = other

    @property
    def midleft(self):
        return self.x, self.y + self.h // 2

    @midleft.setter
    def midleft(self, other):
        self.left, self.midy = other

    @property
    def center(self):
        return self.midx, self.midy

    @center.setter
    def center(self, other):
        self.midx, self.midy = other

    @property
    def midright(self):
        return self.right, self.midy

    @midright.setter
    def midright(self, other):
        self.right, self.midy = other

    @property
    def bottomleft(self):
        return self.left, self.bottom

    @bottomleft.setter
    def bottomleft(self, other):
        self.left, self.bottom = other

    @property
    def midbottom(self):
        return self.midx, self.bottom

    @midbottom.setter
    def midbottom(self, other):
        self.midx, self.bottom = other

    @property
    def bottomright(self):
        return self.right, self.bottom

    @bottomright.setter
    def bottomright(self, other):
        self.right, self.bottom = other

    @property
    def relbottom(self):
        return self.h

    @property
    def relright(self):
        return self.w

    @property
    def reltop(self):
        return 0

    relleft = reltop

    @property
    def relpos(self):
        return 0, 0

    reltopleft = relpos

    @property
    def relmidx(self):
        return self.w // 2

    @property
    def relmidy(self):
        return self.h // 2

    @property
    def relmidtop(self):
        return self.w // 2, 0

    @property
    def reltopright(self):
        return self.w, 0

    @property
    def relmidleft(self):
        return 0, self.h // 2

    @property
    def relcenter(self):
        return self.w // 2, self.h // 2

    @property
    def relbottomleft(self):
        return 0, self.h

    @property
    def relmidbottom(self):
        return self.w // 2, self.h

    @property
    def relbottomright(self):
        return self.w, self.h

    @property
    def area(self):
        return self.w * self.h

    def collide_point(self, point):
        return self.left <= point[0] < self.right and self.top <= point[1] < self.bottom

    def collide_rect(self, rect):
        return self.left < rect.right and rect.left < self.right and self.top < rect.bottom and rect.top < self.bottom

    def intersect(self, rect):
        result = Rect(max(self.x, rect.x), max(self.y, rect.y))
        result.w = min(self.right, rect.right) - result.x
        result.h = min(self.bottom, rect.bottom) - result.y
        if result.w < 0 or result.h < 0:
            return None
        return result

    def as_pygame_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def rel_rect(self):
        return Rect(0, 0, self.w, self.h)

    def copy(self):
        return Rect(self.x, self.y, self.w, self.h)

    def __eq__(self, other):
        try:
            return self.x == other.x and self.y == other.y and self.w == other.w and self.h == other.h
        except AttributeError:
            return False

    def __str__(self):
        return '{}({}, {}, {}, {})'.format(self.__class__.__name__, self.x, self.y, self.w, self.h)

    __repr__ = __str__
