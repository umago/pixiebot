# coding: utf-8
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from utils import ArgumentParser


DEFAULT_PIXIE_FACE = u'ʕ•͡ᴥ•ʔ'
HAPPY_PIXIE_FACE = u'ʕ^ᴥ^ʔ'
DEAD_PIXIE_FACE = u'ʕxᴥxʔ'
ANGRY_PIXIE_FACE = u'ʕᗒᴥᗕʔ՞'
CRYING_PIXIE_FACE = u'ʕTᴥTʔ'
RNR_PIXIE_FACE = u'\m/ʕ>ᴥ<ʔ\m/'
LIKEABOSS_PIXIE_FACE = u'ʕ▀̿ᴥ▀̿ʔ'
CONFUSED_PIXIE_FACE = u'ʕ๏ᴥ๏ʔ'
FLEXING_PIXIE_FACE = u'ᕙʕ⇀ᴥ⇀ʔᕗ'
MEH_PIXIE_FACE = u'¯\_(ツ)_/¯'

MOODS = {
    'default': DEFAULT_PIXIE_FACE,
    'happy': HAPPY_PIXIE_FACE,
    'dead': DEAD_PIXIE_FACE,
    'angry': ANGRY_PIXIE_FACE,
    'crying': CRYING_PIXIE_FACE,
    'rnr': RNR_PIXIE_FACE,
    'likeaboss': LIKEABOSS_PIXIE_FACE,
    'confused': CONFUSED_PIXIE_FACE,
    'flexing': FLEXING_PIXIE_FACE,
    'meh': MEH_PIXIE_FACE,
}

EASTER_EGGS = {
    int('134768204000606796628033739460070953806'): {
        'msg': int('871540041431104408514262753275752520425037051678'
                   '921827321670896650374903806660820899694784768119'),
        'mood': 'meh',
    },
}

s = lambda _, __: chr(__ % int(1 << 8)) + _(_, __ // 0o400) if __ else ''
s_ = lambda _, __: _(_, __)
s__ = lambda _: s_(s, _)


def parse_args(args):
    parser = ArgumentParser()
    parser.add_argument('msg', nargs='*', default='')
    parser.add_argument('-m', '--mood', type=str, default='default',
                        help='PixieBoots mood')
    return parser.parse_known_args(args)


def pixiesay(args, easter_eggs=False, mood=None):
    args, _ = parse_args(args)

    mood = mood or args.mood
    msg = ' '.join(args.msg)

    if easter_eggs:
        for ee in EASTER_EGGS:
            if s__(ee).lower() in msg.lower():
                mood = EASTER_EGGS[ee]['mood']
                msg = s__(EASTER_EGGS[ee]['msg'])
                break

    pixie = MOODS.get(mood, MOODS['default'])
    delimiter = ':' if msg else ''
    return u'%s%s %s' % (pixie, delimiter, msg)
