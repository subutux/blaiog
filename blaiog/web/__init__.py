from blaiog.db.engine import Engine
from blaiog.web.authentication import DBAuthorizationPolicy
from blaiog.db import models
from .utils import get_pages, md
from . import admin
from . import edit
from . import post
from . import page
import asyncio
from aiohttp import web
import aiohttp_jinja2
import jinja2

import aiohttp_session
try:
    from aioredis import create_pool
    from aiohttp_session.redis_storage import RedisStorage
    USE_REDIS = True
except Exception as e:
    print("Will not use redis pool")
    USE_REDIS = False

import base64
from cryptography import fernet
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from aiohttp_security import setup as setup_security, authorized_userid
from aiohttp_security import SessionIdentityPolicy
from sqlalchemy.sql import select, and_
import logging
log = logging.getLogger('blaiog.web')
log_access = logging.getLogger('blaiog.web.access')
log.addHandler(logging.NullHandler())


class index(web.View):

    @asyncio.coroutine
    @aiohttp_jinja2.template('blog_overview.tmpl.html')
    def get(self):
        session = yield from aiohttp_session.get_session(self.request)
        with (yield from self.request.app.db.engine) as conn:
            # fetch the blogs & there sort body
            where = models.Post.c.writer_id == models.User.c.id
            q_posts = select([models.Post.c.title, models.Post.c.url_title,
                             models.Post.c.short_body,
                             models.Post.c.last_update,
                             models.User.c.login],
                             use_labels=True).where(where)
            q_posts = q_posts.limit(10)
            r_posts = yield from conn.execute(q_posts)
            posts = yield from r_posts.fetchall()
            pages = yield from get_pages(self.request.app.db.engine)

        data = {
            "posts": posts,
            "pages": pages,
            "session": None,
            "a": "home"
        }

        username = yield from authorized_userid(self.request)
        if "user_info" in session:
            data["session"] = session
        return data


class Web(object):
    def __init__(self, config, loop=None):
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop

        self._config = config
        self.app = None
        self.handler = None

    @asyncio.coroutine
    def handle(self, request):
        name = request.match_info.get('name', "Anonymous")
        text = "Hello, " + name
        return web.Response(text=text)

    @asyncio.coroutine
    def start(self):
        port = self._config["web"]["transport"]["ipv4"]["port"]
        listen = self._config["web"]["transport"]["ipv4"]["listen"]

        log.info("Launching web on {}:{}".format(listen, port))
        # theme handling
        theme = self._config['blog']['theme']
        if theme.startswith('/'):
            log.info("Using theme from {}".format(theme))
            static = '{}/static'.format(theme)
            templates = '{}/templates'.format(theme)
        else:
            log.info("Using theme {}".format(theme))
            static = '{}/themes/{}/static'.format(__path__[0], theme)
            templates = '{}/themes/{}/templates'.format(__path__[0], theme)

        self.app = web.Application(loop=self.loop)
        aiohttp_jinja2.setup(self.app,
                             loader=jinja2.FileSystemLoader(templates))
        self.app.db = Engine(self._config)
        yield from self.app.db.connect()
        # session
        if self._config["web"]["session"]["use_redis"] and USE_REDIS:
            # setup redis pool
            redis_cfg = self._config["web"]["session"]["redis"]
            redis_pool = yield from create_pool((redis_cfg["host"],
                                                 int(redis_cfg["port"])))
            aiohttp_session.setup(self.app, RedisStorage(redis_pool))

        else:
            # use secure key
            fernet_key = fernet.Fernet.generate_key()
            secret_key = base64.urlsafe_b64decode(fernet_key)
            aiohttp_session.setup(self.app, EncryptedCookieStorage(secret_key))
        # authentication
        setup_security(self.app,
                       SessionIdentityPolicy(),
                       DBAuthorizationPolicy(self.app.db.engine))
        self.app.router.add_get('/', index)
        admin.register(self.app)
        edit.register(self.app)
        post.register(self.app)
        page.register(self.app)
        self.app.router.add_static('/static', static)
        self.handler = self.app.make_handler(logger=log, access_log=log_access)
        self._server = self.loop.create_server(self.handler, listen, port)
        # srv = loop.run_until_complete(f)
        yield from self._server
        # web.run_app(app,port=port)

    @asyncio.coroutine
    def stop(self):
        log.warning("Stopping Web")
        yield from self.app.shutdown()
        yield from self.app.cleanup()
