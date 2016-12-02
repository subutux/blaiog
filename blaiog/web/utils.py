from blaiog.db import models
from sqlalchemy.sql import select
from markdown2 import markdown
import asyncio


@asyncio.coroutine
def get_pages(engine):
    with (yield from engine) as conn:
        where = models.Page.c.writer_id == models.User.c.id
        q_pages = select([models.Page.c.title,
                          models.Page.c.url_title,
                          models.Page.c.short_body,
                          models.Page.c.last_update,
                          models.User.c.login],
                         use_labels=True).where(where)
        q_pages = q_pages.limit(10)
        r_pages = yield from conn.execute(q_pages)
        pages = yield from r_pages.fetchall()
    return pages


def md(md_string):
    return markdown(md_string, extras=["fenced-code-blocks",
                                       "cuddled-lists",
                                       "smarty-pants",
                                       "tables"])
