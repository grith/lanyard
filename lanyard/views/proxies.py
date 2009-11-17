#############################################################################
#
# Copyright (c) 2009 Victorian Partnership for Advanced Computing Ltd and
# Contributors.
# All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
import socket

from webob.exc import HTTPFound
from zope.httpform import parse
from repoze.bfg.traversal import find_root
from repoze.bfg.url import model_url
from utils import get_shib_session, get_base_data


def default(context, request):
    data = get_base_data(context, request)
    session = get_shib_session(request)
    if session:
        root = find_root(context)
        certificate = root.slcs.get(session)
        data['myproxyinfo'] = None
        if certificate:
            myproxyinfo = context.myproxy_info(certificate)
            if myproxyinfo:
                # XXX dirty hack to support nameless creds
                if not myproxyinfo.has_key('CRED_NAME'): myproxyinfo['CRED_NAME'] = ''
                creds = [{'CRED_START_TIME':myproxyinfo['CRED_START_TIME'],
                          'CRED_END_TIME': myproxyinfo['CRED_END_TIME'],
                          'CRED_OWNER': myproxyinfo['CRED_OWNER'],
                          'CRED_NAME': myproxyinfo['CRED_NAME'],
                          'CRED_RETRIEVER': myproxyinfo['CRED_RETRIEVER'],}]
                if myproxyinfo.has_key('ADDL_CREDS'):
                    for cred in myproxyinfo['ADDL_CREDS'].split(','):
                        creds.append({'CRED_START_TIME':myproxyinfo['CRED_%s_START_TIME' % cred],
                                      'CRED_END_TIME': myproxyinfo['CRED_%s_END_TIME' % cred],
                                      'CRED_NAME': cred,
                                      'CRED_OWNER': myproxyinfo['CRED_%s_OWNER' % cred],
                                      'CRED_RETRIEVER': myproxyinfo['CRED_%s_RETRIEVER' % cred],})
                data['myproxyinfo'] = creds

        proxies = context.get(session)
        data['proxies'] = proxies

    hostname = socket.getfqdn()
    return data


def put(context, request):
    session = get_shib_session(request)
    data = get_base_data(context, request)
    if request.params:
        info = parse(request.environ, request.environ['wsgi.input'])
        proxy = info['proxy']

        root = find_root(context)
        certificate = root.slcs.get(session)

        cred_name = proxy.name or None
        password = proxy.password or None

        context.myproxy_put(session, certificate, cred_name, password)

        return HTTPFound(location=model_url(context, request))
    return data


def destroy(context, request):
    session = get_shib_session(request)
    data = get_base_data(context, request)
    root = find_root(context)
    certificate = root.slcs.get(session)

    credname = request.params['credname']

    context.myproxy_destroy(certificate, credname)

    return HTTPFound(location=model_url(context, request))



