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

from webob.exc import HTTPFound

from binascii import unhexlify
from arcs.gsi.slcs import slcs_handler, SLCSException
from StringIO import StringIO
from M2Crypto import RSA
from Crypto.Cipher import AES

from repoze.bfg.url import model_url
from repoze.bfg.settings import get_settings

from utils import get_shib_session, get_base_data
import json


def default(context, request):
    session = get_shib_session(request)
    data = get_base_data(context, request)
    if session:
        cert = context.get(session)
        data['certificate'] = cert
        if cert:
            not_before, not_after = data['certificate'].get_times()
            data['not_after'] = not_after.get_datetime()
            data['cn'] = cert.get_dn().split(',')[-1:][0].strip()

    return data


def request(context, request):
    request.environ['wsgi.url_scheme'] = 'https'
    return HTTPFound(location='https://slcstest.arcs.org.au/SLCS/token?service=' + model_url(context, request) + 'response.html')


def response(context, request):
    req = request
    slcsResp = req.POST['CertificateRequestData']
    session_key = req.POST['SessionKey']

    # Decrpyt session Key with host private key (RSA)
    encrypted = unhexlify(session_key)

    priv_key = RSA.load_key(get_settings()['host_privkey'])
    session_key = priv_key.private_decrypt(encrypted, RSA.pkcs1_padding)

    # Decrypt message with session key (AES)
    a = AES.new(session_key)
    plaintext = a.decrypt(unhexlify(slcsResp))

    # remove AES padding
    n = ord(plaintext[-1]) # last byte contains number of padding bytes
    if n > AES.block_size or n > len(plaintext):
        raise Exception('invalid padding')

    try:
        certificate = slcs_handler(StringIO(plaintext[:-n]))
    except SLCSException, e:
        # TODO add error handling
        pass
        #return template(simple_page,title='Error - %s' % e.expression, body='<h1>%s</h1><pre>%s</pre>' % (e.expression, e.message))

    session = get_shib_session(request)
    context.store(session, certificate)

    return HTTPFound(location=model_url(context, request))


def json_default(context, request):
    data = {}
    if not (request.host.startswith('localhost:')) or (request.host.startswith('127.0.0.1:')):
        return {'response': 'Error', 'message': 'invalid request'}

    if request.method == 'POST':
        try:
            args = json.loads(request.body)
        except ValueError:
            return {'response': 'Error', 'message': 'invalid request'}

        cert = context.get(args['session'])
        if cert:
            data['response'] = 'Ok'
            data['certificate'] = repr(cert)
            data['key'] = str(cert.get_key())
        else:
            data['response'] = 'No Certificate'
    return data

