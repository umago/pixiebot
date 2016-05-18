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

import time

import irc.bot

from pixiesay import pixiesay
from failgraph import failgraph
from findspec import findspec
from log import get_logger

LOG = get_logger()


class PixieBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667, password=None):
        irc.bot.SingleServerIRCBot.__init__(
            self, [(server, port)], nickname, nickname)
        self.nickname = nickname
        self.channel = channel
        self.password = password

    def on_nicknameinuse(self, c, e):
        LOG.info('Nick previously in use, recovering')
        c.nick(c.get_nickname() + "_")
        if self.password is not None:
            c.privmsg('nickserv', 'identify %s' % self.password)
            c.privmsg('nickserv', 'ghost %s %s' % (self.nickname,
                                                   self.password))
            c.privmsg('nickserv', 'release %s %s' % (self.nickname,
                                                     self.password))
            time.sleep(1)

    def on_welcome(self, c, e):
        if self.password is not None:
            LOG.debug('Identifying with IRC server')
            c.privmsg('nickserv', 'identify %s' % self.password)
            LOG.debug('Identified with IRC server')

        c.join(self.channel)
        LOG.info('Joined channel %s', self.channel)
        time.sleep(0.5)

    def send(self, msg):
        try:
            self.connection.privmsg(self.channel, msg)
            time.sleep(0.5)
        except Exception as e:
            LOG.exception('Error sending a message to %(channel)s. '
                          'Error: %(error)s', {'channel': self.channel,
                                               'error': e})
            self.connection.reconnect()

    def on_pubmsg(self, c, e):
        nick = e.source.split('!')[0]
        auth = e.arguments[0][0]
        if auth == '#':
            try:
                args = e.arguments[0][1:].split()
                command = args.pop(0)
            except IndexError:
                return

            try:
                self.do_command(nick, command, args)
            except Exception as e:
                error_msg = 'Error executing the command #%s' % command
                LOG.exception(error_msg + '. Error: %s', e)
                self.send(pixiesay([error_msg], mood='dead'))

    def do_command(self, nick, command, args):
        if command == 'pixiesay':
            self.send(pixiesay(args, easter_eggs=True))
        if command == 'failgraph':
            msg = failgraph(args)
            self.send(msg)
        if command == 'findspec':
            msg = findspec(args)
            self.send(msg)

def main():
    # TODO(lucasagomes): Make it configurable :-)
    channel = '#openstack-ironic'
    nickname = 'PixieBoots'
    server = 'irc.freenode.net'
    port = 6667
    bot = PixieBot(channel, nickname, server, port)
    bot.start()

if __name__ == "__main__":
    main()
