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

import unittest

from repoze.bfg import testing

def dummy_model_factory():
    context = testing.DummyModel()
    context.slcs = testing.DummyModel(__name__='slcs', __parent__=context)
    context.myproxy = testing.DummyModel(__name__='myproxy', __parent__=context)
    return context

class MockDataTests(unittest.TestCase):
    def test_slcs_request(self):
        from repoze.bfg.traversal import find_root
        context = dummy_model_factory()
        root = find_root(context.slcs)
        self.assertEqual(root, context)


class ViewTests(unittest.TestCase):
    def test_default(self):
        from lanyard.views.lanyard import default
        context = dummy_model_factory()
        request = testing.DummyRequest()
        info = default(context, request)
        self.assertEqual(info['project'], 'lanyard')


    def test_slcs_request(self):
        from lanyard.views.slcs import request as request_html
        context = dummy_model_factory()
        request = testing.DummyRequest()
        info = request_html(context.slcs, request)
        self.assertEqual(info.location, 'https://slcstest.arcs.org.au/SLCS/token?service=http://example.com/slcs/response.html')


    def test_json_post(self):
        from lanyard.views.slcs import json_default
        context = testing.DummyModel()

        # Invalid request
        request = testing.DummyRequest(headers="Accept: application/json\nContent-Type: application/json", post="true")
        request.body = "{'session':'sdf'}"
        request.host = 'localhost:80'
        info = json_default(context, request)
        self.assertEqual(info['response'], 'Error')

        # Valid request
        request = testing.DummyRequest(headers="Accept: application/json\nContent-Type: application/json", post="true")
        request.body = '{"session":"sdf"}'
        request.host = 'localhost:80'
        info = json_default(context, request)
        self.assertEqual(info['response'], 'No Certificate')

        # Invalid host request
        request = testing.DummyRequest(headers="Accept: application/json\nContent-Type: application/json", post="true")
        request.body = '{"session":"sdf"}'
        request.host = 'example.com:80'
        info = json_default(context, request)
        self.assertEqual(info['response'], 'Error')

