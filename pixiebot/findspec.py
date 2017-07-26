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

import datetime
import re

from BeautifulSoup import BeautifulSoup
from six.moves import urllib

from log import get_logger
from utils import ArgumentParser

LOG = get_logger()

BASE_URL = 'http://specs.openstack.org/openstack/ironic-specs/specs/%s/'

_CACHE = {}


def _update_cache(release):
    LOG.debug('Updating cache for the release "%s"', release)
    url = BASE_URL % release
    html_page = urllib.request.urlopen(url)
    soup = BeautifulSoup(html_page)
    specs = {}
    for link in soup.findAll('a', attrs={'href': re.compile('.html$')}):
        href = link.get('href')
        title = ' '.join(href.replace('.html', '').split('-'))
        link = url + href
        specs[title] = link

    _CACHE[release] = {}
    _CACHE[release]['specs'] = specs
    _CACHE[release]['updated_at'] = datetime.datetime.utcnow()
    LOG.info('Cache updated for the release "%s"', release)


def find_specs(words, release):
    if release not in _CACHE:
        _update_cache(release)

    # Check for cache invalidation
    time_now = datetime.datetime.utcnow()
    updated_delta = time_now - _CACHE[release]['updated_at']
    # FIXME(lucasagomes): do not hardcode the cache expiration time
    if updated_delta > datetime.timedelta(hours=5):
        _update_cache(release)

    cached_release = _CACHE[release]
    spec_list = []
    for title in cached_release['specs']:
        word_list = title.split()
        if all([True if w.lower() in word_list else False for w in words]):
            spec_list.append({'title': title,
                              'link': cached_release['specs'][title]})
    return spec_list


def parse_args(args):
    parser = ArgumentParser()
    parser.add_argument('words', nargs='+')
    parser.add_argument('-r', '--release', type=str, default='approved',
                        help='The name or version of the release')
    return parser.parse_args(args)


def findspec(args):
    args = parse_args(args)
    specs = find_specs(args.words, args.release)
    if not specs:
        return 'No specs found'

    msg = ''
    for n, s in enumerate(specs, 1):
        if msg:
            msg += ' | '
        msg += '"%(title)s": %(link)s ' % s

    return '%d spec(s) found: %s' % (len(specs), msg)
