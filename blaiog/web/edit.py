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
from .utils import get_pages
import logging
log = logging.getLogger('blaiog.web.edit')
log.addHandler(logging.NullHandler())

class EditPost(web.View):
    
    @template('edit_post.tmpl.html')
    def get(self):
        
        session = yield from get_session(self.request)
        
        if "post" in self.request.match_info:
            edit = self.request.match_info['post']
        else:
            edit = None
        if edit:
            with (yield from self.request.app.db.engine) as conn:
                q = models.Post.select().where(models.Post.c.url_title == edit)
                r = yield from conn.execute(q)
                post = yield from r.fetchone()
        has_perm = yield from permits(self.request, "Superuser")
        if has_perm:
            if edit is None or post is None:
                return { "error": None, "curr":{}, "session": session, "a": "new_post"}
            else:
                return {"error": None, "curr": {}, "session": session,
                    "post": post, "a": "new_post"
                    }
        else:
            
            return web.HTTPFound('/')
    


    def slugify(self,value):
        """
        Normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens.
        """
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub('[^\w\s-]', '', value).strip().lower()
        return re.sub('[-\s]+', '-', value)
        
    @asyncio.coroutine
    @template('edit_post.tmpl.html')
    def post(self):
        has_perm = yield from permits(self.request, "Superuser")
        if not has_perm:
            return web.HTTPFound('/')
        
        session = yield from get_session(self.request)
        form = yield from self.request.post()
        title = form['title']
        short_body = form['short_body']
        body = form['body']
        
        post_id = form['id'] if 'id' in form else None
        
        url = self.slugify(title)
        engine = self.request.app.db.engine
        if post_id is None:
            q = models.Post.insert().values(
                writer_id=session["user_info"]["id"],
                title=title,
                url_title=url,
                short_body=short_body,
                body=body,
                active=1
                )
        else:
            q = models.Post.update().values(
                writer_id=session["user_info"]["id"],
                title=title,
                url_title=url,
                short_body=short_body,
                body=body,
                last_update=now(),
                active=1
                ).where(models.Post.c.id == post_id)
        with (yield from engine) as conn:
            r = yield from conn.execute(q)
            res = yield from conn.execute(models.Post.select())
            for row in res:
                print(row)
        return web.HTTPFound('/post/{}'.format(url))
        
class EditPage(web.View):
    
    @template('edit_page.tmpl.html')
    def get(self):
        
        session = yield from get_session(self.request)
        
        if "page" in self.request.match_info:
            edit = self.request.match_info['page']
        else:
            edit = None
        if edit:
            with (yield from self.request.app.db.engine) as conn:
                q = models.Page.select().where(models.Page.c.url_title == edit)
                r = yield from conn.execute(q)
                page = yield from r.fetchone()
        has_perm = yield from permits(self.request, "Superuser")
        if has_perm:
            if edit is None or page is None:
                return { "error": None, "curr":{}, "session": session, "a": "new_page"}
            else:
                return {"error": None, "curr": {}, "session": session,
                    "page": page, "a": "new_page"
                    }
        else:
            
            return web.HTTPFound('/')
    


    def slugify(self,value):
        """
        Normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens.
        """
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub('[^\w\s-]', '', value).strip().lower()
        return re.sub('[-\s]+', '-', value)
        
    @asyncio.coroutine
    @template('edit_page.tmpl.html')
    def post(self):
        has_perm = yield from permits(self.request, "Superuser")
        if not has_perm:
            return web.HTTPFound('/')
        
        session = yield from get_session(self.request)
        form = yield from self.request.post()
        title = form['title']
        short_body = " "
        body = form['body']
        page_id = form['id'] if 'id' in form else None
        
        url = self.slugify(title)
        engine = self.request.app.db.engine
        if page_id is None:
            q = models.Page.insert().values(
                writer_id=session["user_info"]["id"],
                title=title,
                url_title=url,
                short_body=short_body,
                body=body,
                active=1
                )
        else:
            q = models.Page.update().values(
                writer_id=session["user_info"]["id"],
                title=title,
                url_title=url,
                short_body=short_body,
                body=body,
                last_update=now(),
                active=1
                ).where(models.Page.c.id == page_id)
        with (yield from engine) as conn:
            r = yield from conn.execute(q)
            res = yield from conn.execute(models.Page.select())
            for row in res:
                print(row)
        return web.HTTPFound('/page/{}'.format(url))
        
class DeletePost(web.View):
    
    @template("delete_post.tmpl.html")
    def get(self):
        has_perm = yield from permits(self.request, "Superuser")
        if not has_perm:
            return web.HTTPFound('/')
        
        session = yield from get_session(self.request)
        url = self.request.match_info['post']
        where_Post = models.Post.c.url_title == url
        where_user = models.Post.c.writer_id == models.User.c.id
        q = select([models.Post, models.User],use_labels=True).where(and_(where_Post,where_user))
        with (yield from self.request.app.db.engine) as conn:
            r = yield from conn.execute(q)
            post = yield from r.fetchone()
        pages = yield from get_pages(self.request.app.db.engine)
        return {
            "session": session,
            "post": post,
            "pages": []
        }
    def post(self):
        form = yield from self.request.post()
        post_id = form['id']
        where = models.Post.c.id == post_id
        q = models.Post.delete().where(where)
        with (yield from self.request.app.db.engine) as conn:
             yield from conn.execute(q)
        return web.HTTPFound('/')


class DeletePage(web.View):
    
    @template("delete_page.tmpl.html")
    def get(self):
        has_perm = yield from permits(self.request, "Superuser")
        if not has_perm:
            return web.HTTPFound('/')
        
        session = yield from get_session(self.request)
        url = self.request.match_info['page']
        where_Page = models.Page.c.url_title == url
        where_user = models.Page.c.writer_id == models.User.c.id
        q = select([models.Page, models.User],use_labels=True).where(and_(where_Page,where_user))
        with (yield from self.request.app.db.engine) as conn:
            r = yield from conn.execute(q)
            page = yield from r.fetchone()
        pages = yield from get_pages(self.request.app.db.engine)
        return {
            "session": session,
            "page": page,
            "pages": []
        }
    def post(self):
        form = yield from self.request.post()
        post_id = form['id']
        where = models.Page.c.id == post_id
        q = models.Page.delete().where(where)
        with (yield from self.request.app.db.engine) as conn:
             yield from conn.execute(q)
        return web.HTTPFound('/')

def register(app):
    app.router.add_route("*","/post/edit",EditPost)
    app.router.add_route("*","/post/{post}/edit",EditPost)
    app.router.add_route("*","/post/{post}/delete",DeletePost)
    app.router.add_route("POST","/post/delete",DeletePost)
    app.router.add_route("*","/page/edit",EditPage)
    app.router.add_route("*","/page/{page}/edit",EditPage)
    app.router.add_route("*","/page/{page}/delete",DeletePage)
    app.router.add_route("POST","/page/delete",DeletePage)
    