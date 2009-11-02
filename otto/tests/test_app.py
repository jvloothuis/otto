import unittest

class ApplicationCase(unittest.TestCase):
    def test_not_found(self):
        from otto import Application
        from otto.tests.utils import get_response
        app = Application()
        self.assertEqual(get_response(app, '/path'), ['Page not found.'])

    def test_forbidden(self):
        from otto import Application
        from otto.tests.utils import get_response
        app = Application(lambda: {'path': u"Access was granted."})
        import webob.exc
        @app.route('/*')
        def controller_with(context, request):
            return webob.Response(context)
        self.assertEqual(get_response(app, '/path'), ['Access was granted.'])
        @app.on_traverse
        def handler(context, name):
            raise webob.exc.HTTPForbidden("Traversal disabled.")
        self.assertEqual(get_response(app, '/path'), ['Access was denied.'])

