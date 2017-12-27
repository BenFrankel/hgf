###############################################################################
#                                                                             #
#   Copyright 2017 Ben Frankel                                                #
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

from .component import LayeredComponent

import pygame

import logging


class Window(LayeredComponent):
    MSG_EXIT = 'exit'

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.type = 'window'

        self.args = args
        self._display = None

        self.bg_color = None
        self.title = 'hgf Window'

    def load_style(self):
        self.bg_color = self.style_get('bg-color')

    def load_options(self):
        self.title = self.options_get('title')

    def refresh_proportions(self):
        super().refresh_proportions()
        self._display = pygame.display.set_mode(self.size, *self.args)

    def refresh_background(self):
        super().refresh_background()
        pygame.display.set_caption(self.title)
        self.background.fill(self.bg_color)

    def launch(self, fps=None, debug=False):
        if debug:
            logging.getLogger().setLevel(logging.WARNING)
        else:
            logging.disable(logging.NOTSET)

        main_clock = pygame.time.Clock()
        latest_mouse_motion = None
        hovered_component = self
        frame = 1

        while True:
            mouse_moved = False

            # Pygame event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif debug and event.type == pygame.KEYDOWN and event.key == pygame.K_F9:
                    print(self._recursive_debug_str())
                elif event.type == pygame.MOUSEMOTION:
                    latest_mouse_motion = event
                    mouse_moved = True
                self.handle_event(event)

            # Track mouse motion missed by pygame
            if latest_mouse_motion is not None and latest_mouse_motion.pos != pygame.mouse.get_pos():
                pos = pygame.mouse.get_pos()
                latest_mouse_motion = pygame.event.Event(pygame.MOUSEMOTION, {
                    'pos': pos,
                    'rel': (pos[0] - latest_mouse_motion.pos[0], pos[1] - latest_mouse_motion.pos[1]),
                    'buttons': pygame.mouse.get_pressed(),
                })
                self.handle_event(latest_mouse_motion)

            prev_hovered_component, hovered_component = hovered_component, self._frontmost_at(pygame.mouse.get_pos())
            if hovered_component.is_frozen:
                hovered_component = None
            if not mouse_moved and prev_hovered_component is not hovered_component:
                if prev_hovered_component is not None:
                    prev_hovered_component.on_mouse_motion(pygame.mouse.get_pos(),
                                                           pygame.mouse.get_pos(),
                                                           pygame.mouse.get_pressed(),
                                                           True, False)
                if hovered_component is not None:
                    hovered_component.on_mouse_motion(pygame.mouse.get_pos(),
                                                      pygame.mouse.get_pos(),
                                                      pygame.mouse.get_pressed(),
                                                      False, True)

            if fps is None:
                main_clock.tick()
            else:
                main_clock.tick(fps)

            # Frame pipeline
            self._recursive_step(main_clock.get_time())
            logging.info('Showing frame {}'.format(frame))
            frame += 1

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self._key_down(event.unicode, event.key, event.mod)
        elif event.type == pygame.KEYUP:
            self._key_up(event.key, event.mod)
        elif event.type == pygame.MOUSEMOTION:
            start = (event.pos[0] - event.rel[0], event.pos[1] - event.rel[1])
            self._mouse_motion(start,
                               event.pos,
                               event.buttons,
                               self._frontmost_at(start),
                               self._frontmost_at(event.pos))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._mouse_down(event.pos,
                             event.button,
                             self._frontmost_at(event.pos))
        elif event.type == pygame.MOUSEBUTTONUP:
            self._mouse_up(event.pos,
                           event.button,
                           self._frontmost_at(event.pos))

    def handle_message(self, sender, message, **params):
        if message == Window.MSG_EXIT:
            exit()
        logging.warning('Unhandled message: "{}"'.format(message), params)

    def _step_output(self):
        if super()._step_output():
            pygame.display.update()
