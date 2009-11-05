import os
import mmap
import hashlib
from mimetypes import guess_type
from webob import Response
from webob.exc import HTTPForbidden
from webob.exc import HTTPNotFound

class File(object):
    def __init__(self, path):
        self.path = path

    def __call__(self, request):
        # FIXME: etags etc.
        # FIXME: if modified since -> 304
        # FIXME: (IOError, OSError)
        # If-Modified-Since: Sat, 29 Oct 1994 19:43:31 GMT
        if request.method != 'GET':
            return Response(status=405)
        path = self.path
        content_type, charset = guess_type(path)
        stat = os.stat(path)
        file = open(path)
        filesize = stat.st_size
        etag_hash = hashlib.sha256()
        etag_hash.update(str(stat.st_mtime))
        etag_hash.update(str(filesize))
        response = Response(
                        content_type=content_type,
                        charset=charset,
                        etag=etag_hash.hexdigest(),
                        accept_ranges='bytes')

        content_range = request.headers.get('Range')
        if content_range:
            # FIXME: multiple byte ranges should also be supported:
            # bytes=0-2,4-6
            range_type, sizes = content_range.split('=')
            assert range_type == 'bytes'
            start, end = map(str.strip, sizes.split('-'))
            start = 0 if not start else int(start)
            if start > filesize:
                return Response(status=416)
            end = filesize if not end else int(end)
            end = end if end <= filesize else filesize
            mfile = mmap.mmap(file.fileno(), end, prot=mmap.PROT_READ)
            # create an iterator that will only read requested part
            def file_iter():
                mfile.seek(start)
                while True:
                    data = mfile.read(stat.st_blksize)
                    if not data:
                        return
                    yield data
            response.app_iter = file_iter()
            response.status = 206
            response.content_range = 'bytes %s-%s/%s' % (start, end, filesize)
        else:
            response.app_iter = file
            response.content_length = stat.st_size
        return response

class StaticFactory(object):

    def __init__(self, root):
        self.root = root

    def __call__(self, subpath):
        path = os.path.abspath(os.path.join(self.root, subpath))
        if not path.startswith(self.root):
            raise HTTPForbidden('Access to: %s is denied.' % subpath)
        if not os.path.exists(path):
            raise HTTPNotFound
        return File(path)

