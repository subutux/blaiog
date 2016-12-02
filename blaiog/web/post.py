from blaiog.db import models
from aiohttp_jinja2 import template
from aiohttp_session import get_session
from aiohttp_security import remember, forget, authorized_userid, permits
from sqlalchemy.sql.functions import now
from sqlalchemy.sql import select, and_
import asyncio
from aiohttp import web
from .utils import get_pages, md
import unicodedata
import copy
import markdown2
import re
import logging
log = logging.getLogger('blaiog.web.post')
log.addHandler(logging.NullHandler())


class Post(web.View):

    @asyncio.coroutine
    @template('blog.tmpl.html')
    def get(self):

        session = yield from get_session(self.request)
        url = self.request.match_info['post']
        where_post = models.Post.c.url_title == url
        where_user = models.Post.c.writer_id == models.User.c.id
        q = select([models.Post, models.User],
                   use_labels=True).where(and_(where_post, where_user))
        with (yield from self.request.app.db.engine) as conn:
            r = yield from conn.execute(q)
            post = yield from r.fetchone()
        pages = yield from get_pages(self.request.app.db.engine)
        p = copy.deepcopy(dict(post))
        p["body"] = md(p["post_body"])
        if post is None:
            return web.HTTPNotFound()
        else:
            error = None
        return {
            "session": session,
            "error": error,
            "post": p,
            "pages": pages}


def register(app):
    app.router.add_route('*', '/post/{post}', Post)
