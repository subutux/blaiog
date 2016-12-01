from blaiog.db import models
import asyncio
from aiohttp import web
import aiohttp_jinja2
from sqlalchemy.sql import select

import logging
log = logging.getLogger('blaiog.web.admin')
log.addHandler(logging.NullHandler())

from aiohttp_security import remember, forget, authorized_userid, permits
from aiohttp_session import get_session
from .authentication import check_credentials, get_user, async_get_user

class AdminRoot(web.View):
    @asyncio.coroutine
    def get(self):
        
        with (yield from self.request.app.db.engine) as conn:
            rows =  yield from conn.execute(select([models.Page]))
            pages = yield from rows.fetchall()
            rows =  yield from conn.execute(select([models.Post]))
            posts = rows.fetchall()
            rows =  yield from conn.execute(select([models.User]))
            users = rows.fetchall()
            rows =  yield from conn.execute(select([models.Permission]))
            perission = rows.fetchall()
        
        return web.json_response(pages)

class Login(web.View):
    
    @aiohttp_jinja2.template('login.tmpl.html')
    def get(self,error=None):
        return { "error": error, "curr":{}, "session": None }
    
    @asyncio.coroutine
    @aiohttp_jinja2.template('login.tmpl.html')
    def post(self):
        session = yield from get_session(self.request)
        form = yield from self.request.post()
        log.info("Form: {}".format(form))
        login = form['user']
        password = form['password']
        engine = self.request.app.db.engine
        response = web.HTTPFound('/')
        if (yield from check_credentials(engine, login, password)):
            yield from remember(self.request, response, login)
            session["user_info"] = yield from async_get_user(engine,login)
            return response
        else:
            return { "error": "error", "curr":{} , "session": None}

@asyncio.coroutine
def logout(request):
        session = yield from get_session(request)
        response = web.HTTPFound('/')
        yield from forget(request, response)
        session["user_info"] = None
        return response

def register(app):
    app.router.add_route('*','/admin',AdminRoot)
    app.router.add_route('*','/login',Login)
    app.router.add_get('/logout',logout)
