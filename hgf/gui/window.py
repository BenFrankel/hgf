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

from .component import GraphicalComponent

import pygame


class Window(GraphicalComponent):
    MSG_EXIT = 'exit'

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.type = 'window'

        self.args = args
        self.surf = None

        self.bg_color = None
        self.title = 'hgf Window'

    def load_style(self):
        self.bg_color = self.style_get('bg-color')

    def load_options(self):
        self.title = self.options_get('title')

    def refresh(self):
        pygame.display.set_caption(self.title)

    def launch(self, fps=60):
        fps_clock = pygame.time.Clock()
        self.surf = pygame.display.set_mode(self.size, *self.args)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

                self.handle_event(event)

            self.step()
            fps_clock.tick(fps)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self._key_down(event.unicode, event.key, event.mod)
        elif event.type == pygame.KEYUP:
            self._key_up(event.key, event.mod)
        elif event.type == pygame.MOUSEMOTION:
            start = (event.pos[0] - event.rel[0], event.pos[1] - event.rel[1])
            self._mouse_motion(start, event.pos, event.buttons)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._mouse_down(event.pos, event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            self._mouse_up(event.pos, event.button)

    def handle_message(self, sender, message, **params):
        if message == Window.MSG_EXIT:
            exit()
        # TODO: Warn about unhandled message?

    def _prepare_display(self):
        if super()._prepare_display():
            self.surf.fill(self.bg_color)
            self.surf.blit(self._display, (0, 0))
            pygame.display.update()
