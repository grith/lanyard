import unittest

from repoze.bfg import testing

class ViewTests(unittest.TestCase):
    def test_default(self):
        from lanyard.views import default
        context = testing.DummyModel()
        request = testing.DummyRequest()
        info = default(context, request)
        self.assertEqual(info['project'], 'lanyard')

    def test_slcs_request(self):
        from lanyard.views import slcs_request
        from lanyard.models import get_root
        context = testing.DummyModel()
        request = testing.DummyRequest()
        root = get_root(request)
        info = slcs_request(root.slcs, request)
        self.assertEqual(info.location, 'https://slcstest.arcs.org.au/SLCS/token?service=http://example.com/slcs/response.html')


