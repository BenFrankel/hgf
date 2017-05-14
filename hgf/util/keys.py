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


import pygame


mods = {
    pygame.KMOD_CTRL: 'ctrl',
    pygame.KMOD_ALT: 'alt',
    pygame.KMOD_SHIFT: 'shift'
}


keys = {
    pygame.K_0: '0',
    pygame.K_1: '1',
    pygame.K_2: '2',
    pygame.K_3: '3',
    pygame.K_4: '4',
    pygame.K_5: '5',
    pygame.K_6: '6',
    pygame.K_7: '7',
    pygame.K_8: '8',
    pygame.K_9: '9',
    pygame.K_a: 'a',
    pygame.K_b: 'b',
    pygame.K_c: 'c',
    pygame.K_d: 'd',
    pygame.K_e: 'e',
    pygame.K_f: 'f',
    pygame.K_g: 'g',
    pygame.K_h: 'h',
    pygame.K_i: 'i',
    pygame.K_j: 'j',
    pygame.K_k: 'k',
    pygame.K_l: 'l',
    pygame.K_m: 'm',
    pygame.K_n: 'n',
    pygame.K_o: 'o',
    pygame.K_p: 'p',
    pygame.K_q: 'q',
    pygame.K_r: 'r',
    pygame.K_s: 's',
    pygame.K_t: 't',
    pygame.K_u: 'u',
    pygame.K_v: 'v',
    pygame.K_w: 'w',
    pygame.K_x: 'x',
    pygame.K_y: 'y',
    pygame.K_z: 'z',
    pygame.K_F1: 'f1',
    pygame.K_F2: 'f2',
    pygame.K_F3: 'f3',
    pygame.K_F4: 'f4',
    pygame.K_F5: 'f5',
    pygame.K_F6: 'f6',
    pygame.K_F7: 'f7',
    pygame.K_F8: 'f8',
    pygame.K_F9: 'f9',
    pygame.K_F10: 'f10',
    pygame.K_F11: 'f11',
    pygame.K_F12: 'f12',
    pygame.K_F13: 'f13',
    pygame.K_F14: 'f14',
    pygame.K_F15: 'f15',
    pygame.K_UP: 'up',
    pygame.K_DOWN: 'down',
    pygame.K_LEFT: 'left',
    pygame.K_RIGHT: 'right',
    pygame.K_SPACE: 'space',
    pygame.K_RETURN: 'return',
    pygame.K_ESCAPE: 'esc'
}


def key_name(key, mod):
    result = ''
    for pure_mod, name in mods.items():
        if mod & pure_mod:
            result += name + '-'
    result += keys[key]
    return result
