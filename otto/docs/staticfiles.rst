Serving static files
====================

Most applications have to server CSS, images and other static
files. To make this easy a static controller is provided. This can be
used to easily and securily serve files from a directory.

The application shown below demonstrates the usage of the static
controller.

.. code-block:: python

  #!/usr/bin/env python2.6

  import os
  import inspect
  import wsgiref.simple_server

  import webob
  import otto
  from otto import static

  MEDIA_DIR = os.path.abspath(
      os.path.join(os.path.dirname(inspect.getfile(otto)), 'tests'))

  app = otto.Application()
  media = static.StaticFactory(MEDIA_DIR)

  @app.route("/media/*", factory=media)
  def staticmedia(file_, request):
      return file_(request)

  wsgiref.simple_server.make_server('', 8080, app).serve_forever()

The code above makes it possible to get a file.

::

  /media/hello.txt

.. -> url

This shows the file contents.

::

  World

.. -> output

  >>> from otto.tests.mock.simple_server import assert_response
  >>> assert_response(url, app, output)

Factory details
---------------

The factory will raise a 404 exception for non existing files.

  >>> media('world.txt')
  Traceback (most recent call last):
  ...
  HTTPNotFound: 404 Not Found
  ...

Access to files is restricted to the root directory given when
creating a factory.

  >>> media('../../setup.py')
  Traceback (most recent call last):
  ...
  HTTPForbidden: 403 Forbidden
  ...

File details
------------

The content type is set automatically.

  >>> from otto.static import File
  >>> from webob import Request
  >>> staticfile = File(os.path.join(MEDIA_DIR, 'hello.txt'))
  >>> response = staticfile(Request.blank('/'))
  >>> response.headers['content-type']
  'text/plain'

