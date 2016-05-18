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

import re

from six.moves import urllib
from BeautifulSoup import BeautifulSoup
import tinyurl

from utils import ArgumentParser

BASE_URL = 'http://specs.openstack.org/openstack/ironic-specs/specs/%s/'

# TODO(lucasagomes): cache

def _list_specs(specs, url):
    html_page = urllib.request.urlopen(url)
    soup = BeautifulSoup(html_page)
    spec_list = []
    for link in soup.findAll('a', attrs={'href': re.compile('.html$')}):
        href = link.get('href')
        word_list = href.replace('.html', '').split('-')
        if all([True if w.lower() in word_list else False for w in specs]):
            spec_url = tinyurl.create_one(url + href)
            spec_list.append({'title': ' '.join(word_list), 'link': spec_url})
    return spec_list


def parse_args(args):
    parser = ArgumentParser()
    parser.add_argument('specs', nargs='+')
    parser.add_argument('-c', '--cycle', type=str, default='approved',
                        help='The name of the release cycle')
    return parser.parse_args(args)


def findspec(args):
    args = parse_args(args)
    specs = _list_specs(args.specs, BASE_URL % args.cycle)
    if not specs:
        return 'No specs found'

    msg = ''
    for n, s in enumerate(specs, 1):
        if msg:
           msg += ' | '
        msg +='"%(title)s": %(link)s ' % s

    return '%d spec(s) found: %s' % (len(specs), msg)
