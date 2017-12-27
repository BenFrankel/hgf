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

from hgf.double_buffer import double_buffer, responsive
from ..component import Component
from ..util import Rect, keyboard


class GraphicalComponent(Rect, Component):
    def __init__(self,
                 x=0, y=0, w=0, h=0, z=0,
                 show=True, hover=True, solid=True, click=True,
                 opacity=2, bgcolor=None,
                 **kwargs):
        super().__init__(x=x, y=y, w=w, h=h, pause=False, **kwargs)

        # User interaction enabling flags
        self.can_hover = hover
        self.can_click = click
        self.is_solid = solid

        # Visual flags
        self.is_visible = show

        # Input flags
        self.is_hovered = False

        # Rendering
        self._opacity = opacity
        self._colorkey = (0, 0, 0) if self.is_opaque else (0, 0, 0, 0) if self.is_translucent else None
        self._bgcolor = bgcolor
        self._background = None

        # Dirty state
        self._dirty_flag = True

        self._graphical_children = []
        self.z = z

    def on_show(self): pass

    def on_hide(self): pass

    def on_key_down(self, unicode, key, mods): pass

    def on_key_up(self, key, mods): pass

    def on_mouse_motion(self, start, end, buttons, start_hovered, end_hovered): pass

    def on_mouse_down(self, pos, button, hovered): pass

    def on_mouse_up(self, pos, button, hovered): pass

    @responsive(init=True)
    def refresh_background(self): pass

    @double_buffer
    class w: pass

    @double_buffer
    class h: pass

    @double_buffer
    class x: pass

    @double_buffer
    class y: pass

    @double_buffer
    class z:
        def on_transition(self):
            if not self.is_root:
                self.parent._on_child_changed_z(self)

    @property
    def is_transparent(self):
        return self._opacity == 0

    @property
    def is_translucent(self):
        return self._opacity == 1

    @property
    def is_opaque(self):
        return self._opacity == 2

    @property
    def colorkey(self):
        return self._colorkey

    @colorkey.setter
    def colorkey(self, other):
        self._colorkey = other
        self._background.set_colorkey(other)

    @property
    def background(self):
        return self._background

    @background.setter
    def background(self, other):
        if self._background is None or self._background.get_size() != other.get_size():
            self.size = other.get_size()
        self._background = other
        if self._colorkey is not None:
            self._background.set_colorkey(self._colorkey)
        self._set_dirty(True)

    def on_disown(self):
        if self.old_is_visible and self.old_w is not None:
            self.parent._add_dirty_rect(Rect(self.old_x, self.old_y, self.old_w, self.old_h))
        self._set_dirty(self.is_visible)

    def on_is_visible_transition(self):
        super().on_is_visible_transition()
        self._set_dirty(True)

    def on_is_active_transition(self):
        super().on_is_active_transition()
        self._set_dirty(True)

    def abs_pos(self):
        if self.is_root:
            return self.pos
        px, py = self.parent.abs_pos()
        return px + self.x, py + self.y

    def abs_rect(self):
        return Rect(*self.abs_pos(), self.w, self.h)

    def _frontmost_at(self, pos):
        for child in self._graphical_children:
            if child.is_active and child.is_solid and child.collide_point(pos):
                return child._frontmost_at((pos[0] - child.pos[0],
                                            pos[1] - child.pos[1]))
        return self if self.is_solid else None

    def _key_down(self, unicode, key, mod):
        try:
            self.handle_message(self, self.controls_get(keyboard.name_from_pygame(key, mod)))
        except KeyError:
            pass
        self.on_key_down(unicode, key, mod)

    # TODO: What about message for release by name in controls? (as in _key_down)
    def _key_up(self, key, mods):
        self.on_key_up(key, mods)

    def _mouse_motion(self, start, end, buttons, start_component, end_component):
        self.on_mouse_motion(start, end, buttons, start_component is self, end_component is self)

    def _mouse_down(self, pos, button, component):
        self.on_mouse_down(pos, button, component is self)

    def _mouse_up(self, pos, button, component):
        self.on_mouse_up(pos, button, component is self)

    def _transition_rects(self):
        if self.old_is_active and self.is_active and self.old_is_visible and self.is_visible:
            old = Rect(self.old_x, self.old_y, self.old_w, self.old_h)
            comb = Rect(min(self.x, old.x), min(self.y, old.y))
            comb.w = max(self.right, old.right) - comb.x
            comb.h = max(self.bottom, old.bottom) - comb.y
            if self.area + old.area > comb.area:
                return [comb]
            else:
                return [old, Rect.copy(self)]
        elif self.old_is_active and self.old_is_visible:
            return [Rect(self.old_x, self.old_y, self.old_w, self.old_h)]
        elif self.is_active and self.is_visible:
            return [Rect.copy(self)]
        return []

    def _set_dirty(self, other):
        self._dirty_flag = other

    def _step_reset(self):
        self._dirty_rects = []
        self._dirty_area = 0
        self._set_dirty(False)
        super()._step_reset()

    def _debug_str(self):
        return '{} [state: {}{}{}{}, interaction: {}{}, opacity: {}]'.format(
            self,
            'a' if self.is_active else '-',
            'p' if self.is_paused else '-',
            'f' if self.is_frozen else '-',
            'v' if self.is_visible else '-',
            'c' if self.can_click else '-',
            'h' if self.can_hover else '-',
            self._opacity,
        )

    def _recursive_debug_str(self, depth=0):
        return '{}{}\n{}'.format(
            '| ' * depth,
            self._debug_str(),
            ''.join(child._recursive_debug_str(depth + 1) for child in self._graphical_children if child.is_loaded)
        )


class FlatComponent(GraphicalComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def register(self, *children):
        if any(isinstance(child, GraphicalComponent) for child in children):
            raise TypeError('{} cannot register GraphicalComponent as a child'.format(self.__class__.__name__))
        super().register(*children)

    _display = GraphicalComponent.background


class LayeredComponent(GraphicalComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Rendering
        self._display = None

        # Dirty rectangles state
        self._dirty_area = 0
        self._dirty_rects = []

    @responsive(init=True, priority=-1)
    def refresh_proportions(self):
        if self.is_translucent:
            self._background = pygame.Surface(self.size, pygame.SRCALPHA)
            self._display = pygame.Surface(self.size, pygame.SRCALPHA)
        elif self.is_opaque:
            self._background = pygame.Surface(self.size)
            self._display = pygame.Surface(self.size)
        if self._colorkey is not None:
            self._background.set_colorkey(self._colorkey)
            self._display.set_colorkey(self._colorkey)
            if self.is_opaque and self._bgcolor is None:
                self._bgcolor = (255, 255, 255)
        if not self.is_transparent and self._bgcolor is not None:
            self._background.fill(self._bgcolor)

    @responsive(init=True, children_first=True)
    def refresh_layout(self): pass

    @GraphicalComponent.background.setter
    def background(self, other):
        if self.is_transparent:
            raise ValueError('Cannot set background for transparent component: {}'.format(self))
        if self.is_opaque and (other.get_flags() & pygame.SRCALPHA or other.get_alpha() is not None):
            raise ValueError('Cannot set translucent background for opaque component: {}'.format(self))
        if self._background.get_size() != other.get_size():
            self.size = other.get_size()
            if self.is_translucent:
                self._display = pygame.Surface(other.get_size(), pygame.SRCALPHA)
            elif self.is_opaque:
                self._display = pygame.Surface(other.get_size())
        if self._colorkey is not None:
            self._background.set_colorkey(self._colorkey)
            self._display.set_colorkey(self._colorkey)
        self._background = other
        self._set_dirty(True)

    @GraphicalComponent.colorkey.setter
    def colorkey(self, other):
        self._colorkey = other
        self._background.set_colorkey(other)
        self._display.set_colorkey(other)

    def on_x_transition(self):
        self._set_dirty(True)

    def on_y_transition(self):
        self._set_dirty(True)

    def on_w_transition(self):
        self.refresh_proportions_flag = True

    def on_h_transition(self):
        self.refresh_proportions_flag = True

    def _on_child_changed_z(self, child):
        self._graphical_children.remove(child)
        for i, other in enumerate(self._graphical_children):
            if other.z > child.z:
                self._graphical_children.insert(i, child)
        self._graphical_children.append(child)

    def register(self, *children):
        super().register(*children)
        for child in children:
            if isinstance(child, GraphicalComponent):
                for i, other in enumerate(self._graphical_children):
                    if child.z > other.z:
                        self._graphical_children.insert(i, child)
                        break
                else:
                    self._graphical_children.append(child)

    def unregister(self, *children):
        super().unregister(*children)
        for child in children:
            if isinstance(child, GraphicalComponent):
                try:
                    self._graphical_children.remove(child)
                except ValueError:
                    pass

    def on_disown(self):
        super().on_disown()
        for rect in self._dirty_rects:
            self._clean_dirty_rects(rect)

    def _mouse_motion(self, start, end, buttons, start_component, end_component):
        super()._mouse_motion(start, end, buttons, start_component, end_component)
        for child in self._graphical_children:
            if child.is_active and child.can_hover and not child.is_frozen:
                rel_start = (start[0] - child.x, start[1] - child.y)
                rel_end = (end[0] - child.x, end[1] - child.y)
                child._mouse_motion(rel_start, rel_end, buttons, start_component, end_component)

    def _mouse_down(self, pos, button, component):
        super()._mouse_down(pos, button, component)
        for child in self._graphical_children:
            if child.can_click and not child.is_frozen:
                rel_pos = (pos[0] - child.x, pos[1] - child.y)
                child._mouse_down(rel_pos, button, component)

    def _mouse_up(self, pos, button, component):
        super()._mouse_up(pos, button, component)
        for child in self._graphical_children:
            if child.can_click and not child.is_frozen:
                rel_pos = (pos[0] - child.x, pos[1] - child.y)
                child._mouse_up(rel_pos, button, component)

    def _set_dirty(self, other):
        super()._set_dirty(other)
        if other and not self.is_root:
            for rect in self._dirty_rects:
                self._clean_dirty_rects(rect)

    def _add_dirty_rect(self, rect):
        if self._dirty_flag or rect in self._dirty_rects:
            return
        area = rect.area
        if area + self._dirty_area > self.area:
            self._set_dirty(True)
        else:
            self._dirty_area += area
            self._dirty_rects.append(rect)
            if not self.is_root:
                self.parent._add_dirty_rect(Rect(self.x + rect.x, self.y + rect.y, rect.w, rect.h))

    def _clean_dirty_rects(self, rect):
        self._dirty_rects.remove(rect)
        self._dirty_area -= rect.area
        if not self.is_root:
            self.parent._clean_dirty_rects(Rect(self.x + rect.x, self.y + rect.y, rect.w, rect.h))

    def _redraw_area(self, rect):
        pyrect = rect.as_pygame_rect()
        if self.is_translucent:
            self._display.fill(self.colorkey, pyrect)
        self._display.blit(self._background, rect.pos, pyrect)
        can_see = lambda child: child.is_active and child.is_visible
        children = list(filter(can_see, self._graphical_children))
        for child in children:
            if child.is_transparent:
                children.extend(filter(can_see, child._graphical_children))
                continue
            # FIXME: What if child comes from an offset transparent child?
            # FIXME: Its rect will be relative to the transparent child.
            area = rect.intersect(child)
            if area is None or area.w <= 0 or area.h <= 0:
                continue
            self._display.blit(child._display,
                               area.pos,
                               pygame.Rect(area.x - child.x,
                                           area.y - child.y,
                                           area.w,
                                           area.h))

    def _step_output(self):
        super()._step_output()
        # Identify dirty rectangles
        if not self._dirty_flag:
            for child in self._graphical_children:
                if (child.old_is_active and child.old_is_visible or child.is_active and child.is_visible) and child._dirty_flag:
                    for rect in child._transition_rects():
                        self._add_dirty_rect(rect)

        # Redraw dirty rectangles
        if not self.is_transparent:
            if self._dirty_flag:
                self._redraw_area(self.rel_rect())
            else:
                for rect in self._dirty_rects:
                    self._redraw_area(rect)

        return self._dirty_flag or self._dirty_rects
