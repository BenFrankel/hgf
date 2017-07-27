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


# Key-to-name dictionary
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
}


# Modifier-to-name dictionary
modifiers = {
    pygame.KMOD_CTRL: 'ctrl',
    pygame.KMOD_ALT: 'alt',
    pygame.KMOD_SHIFT: 'shift',
    pygame.KMOD_META: 'meta',
    pygame.KMOD_NUM: 'num',
    pygame.KMOD_CAPS: 'caps',
}


modifier_keys = (
    pygame.K_LCTRL,
    pygame.K_RCTRL,
    pygame.K_LALT,
    pygame.K_RALT,
    pygame.K_LSHIFT,
    pygame.K_RSHIFT,
    pygame.K_LMETA,
    pygame.K_RMETA,
    pygame.K_LSUPER,
    pygame.K_RSUPER,
)


lock_keys = (
    pygame.K_CAPSLOCK,
    pygame.K_NUMLOCK,
    pygame.K_SCROLLOCK,
)


command_keys = modifier_keys + lock_keys + (
    pygame.K_MENU,
)


arrow_keys = (
    pygame.K_UP,
    pygame.K_DOWN,
    pygame.K_LEFT,
    pygame.K_RIGHT,
)


navigation_keys = arrow_keys + (
    pygame.K_PAGEUP,
    pygame.K_PAGEDOWN,
    pygame.K_HOME,
    pygame.K_END,
)


function_keys = (
    pygame.K_F1,
    pygame.K_F2,
    pygame.K_F3,
    pygame.K_F4,
    pygame.K_F5,
    pygame.K_F6,
    pygame.K_F7,
    pygame.K_F8,
    pygame.K_F9,
    pygame.K_F10,
    pygame.K_F11,
    pygame.K_F12,
    pygame.K_F13,
    pygame.K_F14,
    pygame.K_F15,
)


alphabetic_keys = (
    pygame.K_a,
    pygame.K_b,
    pygame.K_c,
    pygame.K_d,
    pygame.K_e,
    pygame.K_f,
    pygame.K_g,
    pygame.K_h,
    pygame.K_i,
    pygame.K_j,
    pygame.K_k,
    pygame.K_l,
    pygame.K_m,
    pygame.K_n,
    pygame.K_o,
    pygame.K_p,
    pygame.K_q,
    pygame.K_r,
    pygame.K_s,
    pygame.K_t,
    pygame.K_u,
    pygame.K_v,
    pygame.K_w,
    pygame.K_x,
    pygame.K_y,
    pygame.K_z,
)


numeric_keys = (
    pygame.K_0,
    pygame.K_1,
    pygame.K_2,
    pygame.K_3,
    pygame.K_4,
    pygame.K_5,
    pygame.K_6,
    pygame.K_7,
    pygame.K_8,
    pygame.K_9,
)


punctuation_keys = (
    pygame.K_QUOTE,
    pygame.K_BACKQUOTE,
    pygame.K_MINUS,
    pygame.K_PLUS,
    pygame.K_LEFTBRACKET,
    pygame.K_RIGHTBRACKET,
    pygame.K_SLASH,
    pygame.K_BACKSLASH,
    pygame.K_COMMA,
    pygame.K_PERIOD,
    pygame.K_SEMICOLON,
    pygame.K_SPACE,
    pygame.K_RETURN,
    pygame.K_KP_MULTIPLY,
    pygame.K_KP_DIVIDE,
    pygame.K_KP_PLUS,
    pygame.K_KP_MINUS,
    pygame.K_KP_PERIOD,
    pygame.K_KP_EQUALS,
)


alphanumeric_keys = alphabetic_keys + numeric_keys


character_keys = alphanumeric_keys + punctuation_keys


text_entry_keys = character_keys + (
    pygame.K_RETURN,
    pygame.K_KP_ENTER,
)


editing_keys = text_entry_keys + (
    pygame.K_BACKSPACE,
    pygame.K_DELETE,
)


def name_from_pygame(key, mod):
    result = ''
    for pure_mod, name in modifiers.items():
        if mod & pure_mod:
            result += name + '-'
    result += keys[key]
    return result
