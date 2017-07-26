# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the 'License'); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an 'AS IS' BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
This module was heavily based on https://github.com/sdague/failopotamus/
"""

import json
import urllib

import requests
import tinyurl

from utils import ArgumentParser

COLORS = (
    ('ff0000', 'b00000'),
    ('0000ff', '0000b0'),
    ('00ff00', '00b000'),
)


def graphite_base_url(since=200, avg=12):
    ylabel = urllib.quote('Failure Rate in Percent')
    title = urllib.quote('Test failure rates over last %s hours '
                         '(%s hour rolling average)' % (since, avg))
    return ('http://graphite.openstack.org/render/?from=-%dhours'
            '&height=500&until=now&width=800&bgcolor=ffffff'
            '&fgcolor=000000&yMax=100&yMin=0&vtitle=%s'
            '&title=%s&drawNullAsZero=true'
            ) % (since, ylabel, title)


def failrate(job, queue, color, width=1, avg=12):
    title = urllib.quote('%s (%s)' % (job, queue))
    return ('target=lineWidth(color('
            'alias('
            'movingAverage('
            'asPercent('
            'transformNull('
            'stats_counts.zuul.pipeline.%(queue)s.job.%(job)s.FAILURE),'
            'transformNull(sum(stats_counts.zuul.pipeline.%(queue)s.'
            'job.%(job)s.{SUCCESS,FAILURE})))'
            ',%%27%(time)shours%%27),%%20%%27%(title)s%%27),'
            '%%27%(color)s%%27),'
            '%(width)s)' %
            {'job': job, 'queue': queue, 'time': avg,
             'color': color, 'title': title, 'width': width})


def target_in_pipeline(target, pipeline):
    json_data = ('http://graphite.openstack.org/render?target='
                 'stats.zuul.pipeline.%(pipeline)s.job'
                 '.%(target)s.*&format=json' %
                 {'pipeline': pipeline, 'target': target})
    resp = requests.get(json_data)
    data = json.loads(resp.content)
    # if the data is blank, this doesn't exist on the graphite server
    # at all
    return True if data else False


def get_targets(target, colors, avg=12):
    targets = []
    color = 0
    width = 1
    for pipeline in ('check', 'gate'):
        if target_in_pipeline(target, pipeline):
            targets.append(
                failrate(target, pipeline, colors[color], width, avg))
            width += 1
            color += 1
    return targets


def parse_args(args):
    parser = ArgumentParser()
    parser.add_argument('tests', nargs='+')
    parser.add_argument('-d', '--duration', type=int, default=200,
                        help='Graph over duration hours (default 200)')
    parser.add_argument('-s', '--smoothing', type=int, default=12,
                        help='Rolling average hours (defaults to 12)')
    return parser.parse_args(args)


def failgraph(args):
    args = parse_args(args)
    targetlist = ''
    colorpairs = 0
    targets = None
    for target in args.tests:
        targets = get_targets(target, COLORS[colorpairs % len(COLORS)],
                              avg=args.smoothing)
        colorpairs += 1
        subtarglist = '&'.join(targets)
        targetlist = '&'.join([targetlist, subtarglist])

    if not targets:
        return 'No data'

    url = '&'.join((graphite_base_url(since=args.duration,
                                      avg=args.smoothing), targetlist))
    return tinyurl.create_one(url)
