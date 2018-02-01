#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2018 Christiaan Frans Rademan.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holders nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.

import os
import sys
import argparse
import site

if not sys.version_info >= (3,5):
    print('Requires python version 3.5 or higher')
    exit()

from tachyonic import metadata
from luxon import g
from luxon.core.config import Config
from luxon import db
from luxon import js
from luxon.exceptions import SQLError

from tachyonic.models.endpoints import endpoint as endpoint_model

def list_endpoints(conn, args):
    endpoints = endpoint_model()
    print(endpoints.to_json())

def new_endpoint(conn, args):
    endpoints = endpoint_model()
    new = endpoints.new()
    new['name'] = args.new_endpoint
    new['interface'] = args.interface
    new['region'] = args.region
    new['uri'] = args.uri
    endpoints.commit()
    print(new.to_json())

def delete_endpoint(conn, args):
    conn.execute('DELETE FROM endpoint WHERE id = %s',
                args.delete_endpoint_id)
    conn.commit()

def main(argv):
    description = metadata.description + ' ' + metadata.version
    print("%s\n" % description)

    parser = argparse.ArgumentParser(description=description)
    group = parser.add_mutually_exclusive_group(required=True)

    parser.add_argument('settings_ini',
                        help='Tachyonic settings.ini path')

    group.add_argument('-l',
                       dest='funcs',
                       action='append_const',
                       const=list_endpoints,
                       help='List endpoints')

    group.add_argument('-a',
                       dest='new_endpoint',
                       help='Add Endpoint')

    group.add_argument('-d',
                       dest='delete_endpoint_id',
                       help='Delete Endpoint by ID')

    parser.add_argument('--uri',
                       help='Absolute URI to Endpoint API',
                       default=None)

    parser.add_argument('--region',
                       help='Region name',
                       default='default')

    parser.add_argument('--interface',
                       help='(public|internal|admin)',
                       default='public')

    args = parser.parse_args()

    ini_file = os.path.abspath(args.settings_ini)
    g.config = Config()

    try:
        g.config.load(ini_file)
    except FileNotFoundError as e:
        print(e)
        exit()

    g.app_root = ini_file.replace('settings.ini','')

    try:
        with db() as conn:
            if args.funcs is not None:
                for func in args.funcs:
                    func(conn, args)

            if args.new_endpoint is not None:
                if args.uri is None:
                    print('Require URI for endpoint')
                    exit()
                new_endpoint(conn, args)

            if args.delete_endpoint_id is not None:
                delete_endpoint(conn, args)
    except SQLError as e:
        print(e)
        exit()


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()
