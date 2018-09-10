#!/usr/bin/env python3
# author: Adrien Giner - adrien.giner@kudelskisecurity.com
#
# config files generator for Hyperledger Fabric (HLF)
#
# Copyright (c) 2018 Nagravision SA
#

import os
import sys
from jinja2 import Environment, FileSystemLoader, exceptions
from docopt import docopt

NAME = 'hlf-gen.py'
VERSION = '0.1'
TEMPLATEDIR = 'templates'
CFGDIR = 'configs'
PROJECT = 'hlftest'
MAXPORT = (2**16)-1

USAGE = '''
HLF config files generator

Usage:
    {0} gen [-p] [--nborg=<nborg>] [--nbpeer=<nbpeer>]
              [--nborderer=<nbord>] [--domain=<domain>]
              [--nbuser=<nbuser>] [--nbcli=<nbcli>]
              [--peerport=<port>] [--peerportincr=<nb>]
              [--peereventport=<port>] [--peereventportincr=<nb>]
              [--ordport=<port>] [--ordportincr=<nb>]
              [--cliport=<port>] [--cliportincr=<nb>]
    {0} --help
    {0} --version

Options:
    --nborg=<nborg>             Number of organization [default: 2].
    --nbpeer=<nbpeer>           Number of peer per org [default: 2].
    --nborderer=<nbord>         Number of orderers [default: 4].
    --nbuser=<nbuser>           Number of user [default: 1].
    --nbcli=<nbcli>             Number of fabric-cli [default: 1].
    --peerport=<port>           First peer service port [default: 7051].
    --peerportincr=<nb>         Peer service port increment [default: 100].
    --peereventport=<port>      First peer event service port [default: 7053].
    --peereventportincr=<nb>    Event service port increment [default: 100].
    --ordport=<port>            First orderer port [default: 7050].
    --ordportincr=<nb>          Orderer port increment [default: 1000].
    --cliport=<port>            Cli port [default: 8000].
    --cliportincr=<nb>          Cli port increment [default: 100].
    --domain=<domain>           The domain to use [default: example.com].
    -p --persistence            peers and couchdb persistence [default: False].
    -v --version                Show version.
    -h --help                   Show this screen.
'''.format(NAME)


class Org:
    '''represent an organization'''
    def __init__(self, id, nbuser):
        self.id = id
        self.peers = []
        self.nbuser = nbuser

    def add_peer(self, peer):
        self.peers.append(peer)


class Peer:
    '''represent a peer'''
    def __init__(self, id, service, event):
        self.id = id
        self.service = service
        self.event = event


class Cli:
    '''represent a fabric-cli'''
    def __init__(self, id, port):
        self.id = id
        self.port = port


class Ord:
    '''represent an orderer'''
    def __init__(self, id, port):
        self.id = id
        self.port = port


######################################################################
# diverse helpers
######################################################################
def _get_env():
    '''get jinja2 env'''
    loader = FileSystemLoader(TEMPLATEDIR)
    env = Environment(loader=loader,
                      trim_blocks=True,
                      lstrip_blocks=True,
                      keep_trailing_newline=True)
    return env


def generate(env, src, dst, domain, orgs, clis, ords, persistence):
    '''generate src (template) to dst'''
    print('\ngenerating {} to {}'.format(src, dst))
    content = gen(env, src, domain, orgs, clis, ords, persistence)
    if not content:
        return
    write(dst, content)
    if dst.endswith('.sh'):
        chmodx(dst)


def gen(env, path, domain, orgs, clis, ords, persistence):
    '''template generation using jinja2'''
    try:
        template = env.get_template(path)
    except exceptions.TemplateNotFound:
        print('[ERROR] {} not found'.format(path))
        return ''
    content = template.render(env=os.environ,
                              domain=domain,
                              orgs=orgs,
                              clis=clis,
                              ords=ords,
                              persistence=persistence,
                              project=PROJECT)
    return content


def write(path, content):
    '''write file to path'''
    with open(path, 'w') as fd:
        fd.write(content)
    print('{} written'.format(path))


def chmodx(path):
    '''chmod +x path'''
    st = os.stat(path)
    os.chmod(path, st.st_mode | 0o111)


def get_nb(args, opt):
    '''parse argument to valid int'''
    tmp = int(args[opt])
    if tmp < 1:
        print('[ERROR] bad option {}: {}'.format(opt, tmp))
        sys.exit(1)
    return tmp


def get_port(args, opt):
    '''parse argument to valid port'''
    tmp = int(args[opt])
    if tmp < 1 or tmp > MAXPORT:
        print('[ERROR] bad option {}: {}'.format(opt, tmp))
        sys.exit(1)
    return tmp


def main():
    '''entry point'''
    args = docopt(USAGE, version=VERSION)
    domain = args['--domain']
    pers = args['--persistence']

    # how many instances
    nborg = get_nb(args, '--nborg')
    nbpeer = get_nb(args, '--nbpeer')
    nbord = get_nb(args, '--nborderer')
    nbuser = get_nb(args, '--nbuser')
    nbcli = get_nb(args, '--nbcli')

    # peer service port
    peerport = get_port(args, '--peerport')
    peerportincr = get_port(args, '--peerportincr')

    # peer event port
    peereventport = get_port(args, '--peereventport')
    peereventportincr = get_port(args, '--peereventportincr')

    # orderer port
    ordport = get_port(args, '--ordport')
    ordportincr = get_port(args, '--ordportincr')

    # cli port
    cliport = get_port(args, '--cliport')
    cliportincr = get_port(args, '--cliportincr')

    # lists of orgs/peers/clis
    orgs = []
    peers = []
    clis = []
    ords = []

    env = _get_env()

    for i in range(nbord):
        ords.append(Ord(i, ordport))
        ordport += ordportincr

    for i in range(nbcli):
        clis.append(Cli(i+1, cliport))
        cliport += cliportincr

    for i in range(nborg):
        # org
        org = Org(i+1, nbuser)
        orgs.append(org)
        # peers
        for i in range(nbpeer):
            peer = Peer(i, peerport, peereventport)
            org.add_peer(peer)
            peerport += peerportincr
            peereventport += peerportincr

    files = {
            'configtx.yaml.j2': 'configtx.yaml',
            'channels.sh.j2': 'channels.sh',
            'crypto-config.yaml.j2': 'crypto-config.yaml',
            'docker-compose.yml.j2': 'docker-compose.yml',
            'start.sh.j2': 'start.sh',
            'stop.sh.j2': 'stop.sh',
            'generate.sh.j2': 'generate.sh'
            }

    if not os.path.exists(CFGDIR):
        os.mkdir(CFGDIR)
    for src, dst in files.items():
        dstf = os.path.join(CFGDIR, dst)
        if os.path.exists(dstf):
            print('[ERROR] {} exists, will not overwrite!'.format(dstf))
            continue
        generate(env, src, dstf, domain, orgs, clis, ords, pers)

    print('\nConfig files generated in {}'.format(CFGDIR))

    return True


if __name__ == '__main__':
    '''entry point'''
    if main():
        sys.exit(0)
    sys.exit(1)
