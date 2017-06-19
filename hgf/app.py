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


import json
import os.path

import pygame
import pygame.freetype

from hgf.gui import window


pygame.freetype.init()


def load_json(filename):
    with open(filename + '.json') as f:
        return json.load(f)


class AppDirectory:
    def __init__(self, name):
        self.root_dir = os.path.join('appdata', name)
        self.dirs = dict()

    def get_path(self, dir_, name):
        return os.path.join(self.root_dir, self.dirs[dir_], name)

    def load(self):
        filename = os.path.join(self.root_dir, 'dir.json')
        with open(filename) as f:
            dir_json = json.load(f)
        for name, path in dir_json.items():
            self.dirs[name] = os.path.join(*path.split('/'))


class AppResources:
    def __init__(self, directory):
        self.directory = directory

        self.images = dict()
        self.fonts = dict()
        self.sounds = dict()
        self.music = dict()

    def load_fonts(self, info):
        for name, filename in info.items():
            try:
                font = pygame.freetype.Font(self.directory.get_path('fonts', filename))
            except OSError as err:
                raise FileNotFoundError('Unable to load font \'{}\''.format(filename)) from err
            else:
                self.fonts[name] = font

    def load_images(self, info):
        for name, filename in info.items():
            try:
                image = pygame.image.load(self.directory.get_path('images', filename))
            except OSError as err:
                raise FileNotFoundError('Unable to load image \'{}\''.format(filename)) from err
            else:
                self.images[name] = image

    def load_sounds(self, info):
        for name, filename in info.items():
            try:
                sound = pygame.mixer.Sound(self.directory.get_path('sounds', filename))
            except Exception as err:
                raise FileNotFoundError('Unable to load audio \'{}\''.format(filename)) from err
            else:
                self.sounds[name] = sound

    def load_music(self, info):
        for name, filename in info.items():
            try:
                music = pygame.mixer.music.load(self.directory.get_path('music', filename))
            except Exception as err:
                raise FileNotFoundError('Unable to load music \'{}\''.format(filename)) from err
            else:
                self.music[name] = music

    def load(self):
        self.load_fonts(load_json(self.directory.get_path('info', 'fonts')))
        self.load_images(load_json(self.directory.get_path('info', 'images')))
        self.load_sounds(load_json(self.directory.get_path('info', 'sounds')))
        self.load_music(load_json(self.directory.get_path('info', 'music')))


class AppConfig:
    def __init__(self, directory, resources):
        self.directory = directory
        self.resources = resources

        self.style = None
        self.options = None
        self.controls = None

        # Style building
        self.style_packs = dict()
        self.compose_style = lambda foundation: None

    def load(self):
        # Resource aliases
        self.load_resource_aliases(load_json(self.directory.get_path('config', 'resources')))

        # Configuration
        self.controls = self.load_controls(load_json(self.directory.get_path('config', 'controls')))
        self.options = self.load_options(load_json(self.directory.get_path('config', 'options')))
        self.style = self.load_style(load_json(self.directory.get_path('config', 'style')))
        self.compose_style(self)

    def load_resource_aliases(self, info):
        for resource, aliases in info.items():
            if resource == 'fonts':
                for alias, origin in aliases.items():
                    self.resources.fonts[alias] = self.resources.fonts[origin]
            elif resource == 'images':
                for alias, origin in aliases.items():
                    self.resources.images[alias] = self.resources.images[origin]
            elif resource == 'sounds':
                for alias, origin in aliases.items():
                    self.resources.sounds[alias] = self.resources.sounds[origin]
            elif resource == 'music':
                for alias, origin in aliases.items():
                    self.resources.music[alias] = self.resources.music[origin]

    def load_style(self, info):
        result = dict()
        for context, names in info.items():
            for name, attrs in names.items():
                if name not in result:
                    result[name] = dict()
                    result[name][context] = dict()
                elif context not in result[name]:
                    result[name][context] = dict()
                for attr_name, attr_value in attrs.items():
                    value = attr_value
                    if attr_value[0] == '@':
                        value = self.style_packs[attr_value[1:]][attr_name]
                    elif attr_value[0] == '$':
                        if attr_value.startswith('$font='):
                            value = self.resources.fonts[attr_value[6:]]
                        elif attr_value.startswith('$image='):
                            value = self.resources.images[attr_value[7:]]
                        elif attr_value.startswith('$sound='):
                            value = self.resources.sounds[attr_value[7:]]
                        elif attr_value.startswith('$music='):
                            value = self.resources.music[attr_value[7:]]
                    result[name][context][attr_name] = value
        return result

    def load_options(self, info):
        result = dict()
        for context, names in info.items():
            for name, attrs in names.items():
                if name not in result:
                    result[name] = dict()
                    result[name][context] = dict()
                elif context not in result[name]:
                    result[name][context] = dict()
                for attr_name, attr_value in attrs.items():
                    result[name][context][attr_name] = attr_value
        return result

    def load_controls(self, info):
        result = dict()
        for context, controls in info.items():
            if context not in result:
                result[context] = dict()
            for name, keys in controls.items():
                for key in keys:
                    result[context][key.lower()] = name
        return result

    def style_get(self, query, name=None, context=None):
        attempts = ('global', 'global'), (name, 'global'), ('global', context),\
                   (name, context),\
                   (name, 'default'), ('default', context), ('default', 'default')
        for try_name, try_context in attempts:
            try:
                return self.style[try_name][try_context][query]
            except KeyError:
                pass
        for try_name, try_context in attempts:
            try:
                return self.style_packs['default'][try_name][try_context][query]
            except KeyError:
                pass
        raise KeyError('Cannot find style \'{}\' for \'{}\' in context \'{}\''.format(query, name, context))

    def options_get(self, query, name=None, context=None):
        attempts = ('global', 'global'), (name, 'global'), ('global', context),\
                   (name, context),\
                   (name, 'default'), ('default', context), ('default', 'default')
        for try_name, try_context in attempts:
            try:
                return self.options[try_name][try_context][query]
            except KeyError:
                pass
        raise KeyError('Cannot find option \'{}\' for \'{}\' in context \'{}\''.format(query, name, context))

    def controls_get(self, query, context=None):
        attempts = 'global', context, 'default'
        for try_context in attempts:
            try:
                return self.controls[try_context][query]
            except KeyError:
                pass
        raise KeyError('Cannot find command for key \'{}\' in context \'{}\''.format(query, context))

    def style_add(self, query, name, context, value):
        if name not in self.style:
            self.style[name] = dict()
            self.style[name][context] = dict()
        elif context not in self.style[name]:
            self.style[name][context] = dict()
        self.style[name][context][query] = value


class App(window.Window):
    def __init__(self, manager, **kwargs):
        self.directory = manager.directory
        self.resources = manager.resources

        self.config = AppConfig(self.directory, self.resources)
        self.config.style_packs = manager.style_packs
        self.config.compose_style = manager.compose_style
        self.config.load()

        super().__init__(*self.config.options_get('size', 'window'), **kwargs)
        self.app = self

        self.focus_stack = []

        try:
            pygame.mixer.music.play(loops=-1)  # TODO: Handle music properly
        except pygame.error:
            pass

    def key_down(self, unicode, key, mod):
        try:
            self.focus_stack[-1].key_down(unicode, key, mod)
        except IndexError:
            pass
        super().key_down(unicode, key, mod)

    def give_focus(self, component):
        component.is_focused = True
        try:
            self.focus_stack[-1].is_focused = False
        except IndexError:
            pass
        try:
            self.focus_stack.remove(component)
        except ValueError:
            pass
        self.focus_stack.append(component)

    def remove_focus(self, component):
        component.is_focused = False
        self.focus_stack.remove(component)


class AppManager:
    def __init__(self, name, factory=App):
        self.name = name
        self._loaded = False

        # Shared data
        self.directory = AppDirectory(self.name)
        self.resources = AppResources(self.directory)

        # Style building
        self.style_packs = None
        self.compose_style = lambda config: None

        self.factory = factory

    def load(self):
        self.directory.load()
        self.resources.load()

        self._loaded = True

    def spawn_app(self):
        if not self._loaded:
            raise RuntimeError('Cannot launch app \'{}\' without loading its manager first'.format(self.name))
        app = self.factory(self)
        app._prepare()
        return app
