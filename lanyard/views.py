from webob.exc import HTTPFound

from binascii import unhexlify
from arcs.gsi.slcs import slcs_handler, SLCSException
from StringIO import StringIO
from M2Crypto import RSA
from Crypto.Cipher import AES

from repoze.bfg.url import model_url
from repoze.bfg.traversal import find_root
from repoze.bfg.chameleon_zpt import get_template
from repoze.bfg.settings import get_settings


import time, calendar

from repoze.bfg.view import static
static_view = static('templates/static')

def get_base_data(context, request):
    main = get_template('templates/master.pt')
    data = {'main': main, 'project': 'lanyard'}
    home_node = find_root(context)
    data['navitems'] = [{'href': model_url(home_node, request), 'title': 'Home', 'state':''},
                        {'href': model_url(home_node.slcs, request), 'title': home_node.slcs.__name__.upper(), 'state':('', 'current_page_item')[home_node.slcs == context]},
                        {'href': model_url(home_node.myproxy, request), 'title': 'MyProxy', 'state':('', 'current_page_item')[home_node.myproxy == context]},
                       ]
    return data


def get_shib_session(request):
    for i in request.cookies:
        if i.startswith('_shibsession_'):
            session = i + '=' + request.cookies[i]
            return session
    return None


def default(context, request):
    data = get_base_data(context, request)
    return data

def slcs(context, request):
    main = get_template('templates/master.pt')
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

def slcs_request(context, request):

    request.environ['wsgi.url_scheme'] = 'https'
    return HTTPFound(location='https://slcstest.arcs.org.au/SLCS/token?service=' + model_url(context, request) + 'response.html')

def slcs_response(context, request):
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

def myproxy(context, request):
    data = get_base_data(context, request)
    return data

