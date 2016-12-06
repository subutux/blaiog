from blaiog.db import models
from aiohttp_jinja2 import template
from aiohttp_session import get_session
from aiohttp_security import remember, forget, authorized_userid, permits
from sqlalchemy.sql.functions import now
from sqlalchemy.sql import select, and_
import asyncio
from aiohttp import web
import unicodedata
import re
import copy
import markdown2
from .utils import get_pages, md
import logging
log = logging.getLogger('blaiog.web.post')
log.addHandler(logging.NullHandler())


class Page(web.View):

    @asyncio.coroutine
    @template('page.tmpl.html')
    def get(self):
        session = yield from get_session(self.request)
        url = self.request.match_info['page']
        where_page = models.Page.c.url_title == url
        where_user = models.Page.c.writer_id == models.User.c.id
        q = select([models.Page, models.User],
                   use_labels=True).where(and_(where_page, where_user))
        with (yield from self.request.app.db.engine) as conn:
            r = yield from conn.execute(q)
            page = yield from r.fetchone()
        pages = yield from get_pages(self.request.app.db.engine)

        p = copy.deepcopy(dict(page))
        p["body"] = md(p["page_body"])
        if page is None:
            return web.HTTPNotFound()
        else:
            error = None
        return {
            "session": session,
            "error": error,
            "page": p,
            "url": self.request.url,
            "pages": pages,
            "a": page["page_url_title"]}


def register(app):
    app.router.add_route('*', '/page/{page}', Page)
