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

####
# XXX this module should probably be at lanyard.utils, but can't exist there
# because the views fail to import it?
####

from repoze.bfg.url import model_url
from repoze.bfg.traversal import find_root
from repoze.bfg.chameleon_zpt import get_template


def get_base_data(context, request):
    main = get_template('../templates/master.pt')
    data = {'main': main, 'project': 'lanyard'}
    home_node = find_root(context)
    data['navitems'] = [{'href': model_url(home_node, request), 'title': 'Home', 'state':''},
                        {'href': model_url(home_node.slcs, request), 'title': home_node.slcs.__name__.upper(), 'state':('', 'current_page_item')[home_node.slcs == context]},
                        {'href': model_url(home_node.proxies, request), 'title': 'MyProxy', 'state':('', 'current_page_item')[home_node.proxies == context]},
                       ]
    return data


def get_shib_session(request):
    for i in request.cookies:
        if i.startswith('_shibsession_'):
            session = i + '=' + request.cookies[i]
            return session
    return None




