# -*- coding: utf-8 -*-
import urllib2 as u2
import socket
import httplib
import ssl
import logging
from suds.transport.http import HttpTransport

_logger = logging.getLogger(__name__)


class HTTPSConnection(httplib.HTTPConnection):
        "This class allows communication via SSL."

        default_port = httplib.HTTPS_PORT

        def __init__(self, host, port=None, key_file=None, cert_file=None,
                     strict=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                     source_address=None, ssl_version=ssl.PROTOCOL_TLSv1):
            # Fix error for python 2.6
            try:
                super(HTTPSConnection, self).__init__(
                    host, port, strict, timeout, source_address)
            except:
                httplib.HTTPConnection.__init__(
                    self, host, port, strict, timeout)
            self.key_file = key_file
            self.cert_file = cert_file
            self.ssl_version = ssl_version

        def connect(self):
            "Connect to a host on a given (SSL) port."
            # Fix error for python 2.6
            try:
                sock = socket.create_connection(
                    (self.host, self.port),
                    self.timeout, self.source_address)
            except:
                sock = socket.create_connection(
                    (self.host, self.port),
                    self.timeout)
            if self._tunnel_host:
                self.sock = sock
                self._tunnel()
            self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file,
                                        ssl_version=self.ssl_version)


class HTTPS(httplib.HTTP):
    """Compatibility with 1.5 httplib interface

    Python 1.5.2 did not have an HTTPS class, but it defined an
    interface for sending http requests that is also useful for
    https.
    """

    _connection_class = HTTPSConnection

    def __init__(self, host='', port=None, key_file=None, cert_file=None,
                 strict=None, ssl_version=ssl.PROTOCOL_SSLv23):
        # provide a default host, pass the X509 cert info

        # urf. compensate for bad input.
        if port == 0:
            port = None
        self._setup(self._connection_class(
            host, port, key_file, cert_file, strict, ssl_version=ssl_version))

        # we never actually use these for anything, but we keep them
        # here for compatibility with post-1.5.2 CVS.
        self.key_file = key_file
        self.cert_file = cert_file


class HTTPSHandler(u2.HTTPSHandler):

    def https_open(self, req):
        return self.do_open(HTTPSConnection, req)

    https_request = u2.AbstractHTTPHandler.do_request_


class HttpsTransport(HttpTransport):
    def __init__(self, *args, **kwargs):
        HttpTransport.__init__(self, *args, **kwargs)

    def u2handlers(self):
        r = HttpTransport.u2handlers(self)
        r.append(HTTPSHandler())
        return r

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
