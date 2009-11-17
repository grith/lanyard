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

import string
from random import choice
from myproxy import client

from repoze.bfg.settings import get_settings

class Base(object):
    """
    Base object to handle setting the required __parent__ and __name__ attributes
    """
    def __init__(self,parent = None,name = None):
        self.__parent__ = parent
        self.__name__ = self.__class__.__name__.lower()

class SLCS(Base):
    """
    SLCS object
    """
    def __init__(self, parent=None, name=None):
        Base.__init__(self, parent, name)
        self._certificates = {}

    def store(self, session, certificate):
        self._certificates[session] = certificate

    def get(self, session):
        if self._certificates.has_key(session):
            return self._certificates[session]
        return None


class Proxies(Base):
    """
    Proxies Object
    """
    def __init__(self, parent=None, name=None):
        Base.__init__(self, parent, name)
        self._proxies = {}

    def store(self, session, name, credname, dn, passphrase):

        if not self._proxies.has_key(session):
            self._proxies[session] = {}
        self._proxies[session][name] = (name, credname, dn, passphrase)

    def get(self, session):
        if self._proxies.has_key(session):
            return self._proxies[session]
        return None


    def myproxy_info(self, certificate):
        myproxy_srv = get_settings()['myproxy']
        myproxy_dn = get_settings()['myproxy-dn']

        c = client.MyProxyClient(hostname=myproxy_srv, serverDN=myproxy_dn)

        passphrase = ''
        dn = certificate.get_dn()
        username = dn.split(',')[-1:][0].strip().split('=',1)[1].replace(' ','_')

        respCode, errorTxt, field = c.info(username, certificate, certificate.get_key()._key, lambda *a: passphrase)
        return field


    def myproxy_destroy(self, certificate, credname):
        myproxy_srv = get_settings()['myproxy']
        myproxy_dn = get_settings()['myproxy-dn']

        c = client.MyProxyClient(hostname=myproxy_srv, serverDN=myproxy_dn)

        passphrase = ''
        dn = certificate.get_dn()
        username = dn.split(',')[-1:][0].strip().split('=',1)[1].replace(' ','_')

        c.destroy(username, certificate, certificate.get_key()._key, lambda *a: passphrase, credname)


    def myproxy_put(self, session, certificate, credname=None, password=None):
        myproxy_srv = get_settings()['myproxy']
        myproxy_dn = get_settings()['myproxy-dn']

        c = client.MyProxyClient(hostname=myproxy_srv, serverDN=myproxy_dn)

        size = 12
        passphrase = password or ''.join([choice(string.letters + string.digits) for i in range(size)])
        dn = certificate.get_dn()
        username = dn.split(',')[-1:][0].strip().split('=',1)[1].replace(' ','_')

        c.put(username, passphrase, certificate, certificate.get_key()._key, lambda *a: passphrase, retrievers='*', credname=credname)


class Root(Base):
    """
    Root object which has a foo attribute and a bar attribute, and implements __getitem__
    """
    __parent__ = None
    __name__ = None
    def __init__(self):
        self.slcs = SLCS(self)
        self.proxies = Proxies(self)


    def __getitem__(self,key):
        if hasattr(self,str(key)):
            return getattr(self,key,None)
        else:
            raise KeyError, key

root = Root()


def get_root(request):
    return root
