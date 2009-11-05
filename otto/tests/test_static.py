import unittest
import os
import tempfile

class TestFile(unittest.TestCase):

    def get_file(self, filename):
        import pkg_resources
        return pkg_resources.resource_filename('otto.tests', filename)

    def test_content_length(self):
        from otto.static import File
        from webob import Request
        file = File(self.get_file('hello.txt'))
        response = file(Request.blank('/'))
        self.assertEqual(response.headers['Content-Length'], '6')

    def test_announce_range_support(self):
        from otto.static import File
        from webob import Request
        file = File(self.get_file('hello.txt'))
        response = file(Request.blank('/'))
        self.assertEqual(response.headers['Accept-Ranges'], 'bytes')

    def test_range_request(self):
        from otto.static import File
        from webob import Request
        request = Request.blank('/', headers={'Range': 'bytes=1-3'})
        file = File(self.get_file('hello.txt'))
        response = file(request)
        self.assertEqual(response.body, 'or')
        self.assertEqual(response.headers['Content-Range'], 'bytes 1-3/6')
        self.assertEqual(response.headers['Content-Length'], '2')
        self.assertEqual(response.status, '206 Partial Content')

    def test_read_beond_end_range(self):
        from otto.static import File
        from webob import Request
        request = Request.blank('/', headers={'Range': 'bytes=0-370'})
        file = File(self.get_file('hello.txt'))
        response = file(request)
        self.assertEqual(response.body, 'World\n')
        self.assertEqual(response.headers['Content-Range'], 'bytes 0-6/6')
        self.assertEqual(response.headers['Content-Length'], '6')
        self.assertEqual(response.status, '206 Partial Content')

    def test_read_beond_start_range(self):
        from otto.static import File
        from webob import Request
        request = Request.blank('/', headers={'Range': 'bytes=370-415'})
        file = File(self.get_file('hello.txt'))
        response = file(request)
        self.assertEqual(response.status,
                         '416 Requested Range Not Satisfiable')

    def test_no_end_range(self):
        from otto.static import File
        from webob import Request
        request = Request.blank('/', headers={'Range': 'bytes=1-'})
        file = File(self.get_file('hello.txt'))
        response = file(request)
        self.assertEqual(response.body, 'orld\n')
        self.assertEqual(response.headers['Content-Range'], 'bytes 1-6/6')
        self.assertEqual(response.headers['Content-Length'], '5')

    def test_no_start_range(self):
        from otto.static import File
        from webob import Request
        request = Request.blank('/', headers={'Range': 'bytes=-3'})
        file = File(self.get_file('hello.txt'))
        response = file(request)
        self.assertEqual(response.body, 'Wor')
        self.assertEqual(response.headers['Content-Range'], 'bytes 0-3/6')
        self.assertEqual(response.headers['Content-Length'], '3')

    def test_allow_only_get(self):
        from otto.static import File
        from webob import Request
        file = File(self.get_file('hello.txt'))
        for method in ('PUT', 'POST', 'DELETE'):
            request = Request.blank('/', method='PUT')
            response = file(request)
            self.assertEqual(response.status, '405 Method Not Allowed')

    def test_etag(self):
        from otto.static import File
        from webob import Request
        testfile = tempfile.NamedTemporaryFile(prefix='otto')
        file = File(testfile.name)
        response1 = file(Request.blank('/'))
        response2 = file(Request.blank('/'))
        self.assertEqual(response1.headers['Etag'],
                         response2.headers['Etag'])
        testfile.write('test data')
        testfile.flush()
        response3 = file(Request.blank('/'))
        self.assertNotEqual(response1.headers['Etag'],
                            response3.headers['Etag'])

