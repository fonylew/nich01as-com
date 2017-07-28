import logging
import webapp2
import jinja2
import os

from handlers.index import IndexHandler
from handlers.login import LoginHandler
from handlers.debug import SystemInfoHandler
from apps.toefl import configs as toefl_config
from apps.kreader import configs as kreader_config

handlers = [('/', IndexHandler), 
            ('/debug', SystemInfoHandler),
            ('/login', LoginHandler)]
handlers = handlers 

logging.info(handlers)

app = webapp2.WSGIApplication(handlers, debug=True)
