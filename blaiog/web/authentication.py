from blaiog import db
from blaiog.db import models
from passlib.hash import pbkdf2_sha512
import asyncio
import sqlalchemy as sa
from sqlalchemy.sql import select, update
import functools
from aiohttp_security.abc import AbstractAuthorizationPolicy
from aiohttp_security import remember, forget, authorized_userid, permits

import logging
log = logging.getLogger('blaiog.web.authentication')
log.addHandler(logging.NullHandler())


class DBAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, dbengine):
        self.dbengine = dbengine

    @asyncio.coroutine
    def authorized_userid(self, identity):
        with (yield from self.dbengine) as conn:
            where = sa.and_(models.User.c.login == identity,
                            sa.not_(models.User.c.disabled))
            query = models.User.count().where(where)
            ret = yield from conn.scalar(query)
            if ret:
                return identity
            else:
                return None

    @asyncio.coroutine
    def permits(self, identity, permission, context=None):
        if identity is None:
            return False

        with (yield from self.dbengine) as conn:
            where = sa.and_(models.User.c.login == identity,
                            sa.not_(models.User.c.disabled))
            query = models.User.select().where(where)
            ret = yield from conn.execute(query)
            user = yield from ret.fetchone()
            if user is not None:
                user_id = user[0]
                is_superuser = user[3]
                if is_superuser:
                    return True

                where = models.Permission.c.user_id == user_id
                query = models.Permission.select().where(where)
                ret = yield from conn.execute(query)
                result = yield from ret.fetchall()
                if ret is not None:
                    for record in result:
                        if record.perm_name == permission:
                            return True

            return False


def require(permission):
    def wrapper(f):
        @asyncio.coroutine
        @functools.wraps(f)
        def wrapped(self, request):
            has_perm = yield from permits(request, permission)
            if not has_perm:
                message = 'User has no permission {}'.format(permission)
                raise web.HTTPForbidden(body=message.encode())
            return (yield from f(self, request))
        return wrapped
    return wrapper


@asyncio.coroutine
def check_credentials(db_engine, username, password):
    with (yield from db_engine) as conn:
        where = sa.and_(models.User.c.login == username,
                        sa.not_(models.User.c.disabled))
        query = models.User.select().where(where)
        ret = yield from conn.execute(query)
        user = yield from ret.fetchone()
        log.info("Login request for {}".format(user))
        if user is not None:
            hash = user[3]
            return pbkdf2_sha512.verify(password, hash)
    return False


@asyncio.coroutine
def async_get_user(engine, user):
    with (yield from engine) as conn:
        where = models.User.c.login == user
        query = models.User.select().where(where)
        ret = yield from conn.execute(query)
        data = yield from ret.fetchone()
        result = {
            "id": data[0],
            "login": data[1],
            "full_name": data[2],
            "is_superuser": data[4]
        }
        log.info(result)
        return result


def user_add(engine, user, password, full_name=' ', superuser=False,
             permission=None):
    conn = engine.connect()
    pass_hash = pbkdf2_sha512.encrypt(password)

    if permission is not None:
        permission_id = permission[0]
    else:
        permission_id = None
    user = models.User.insert().values(login=user,
                                       password=pass_hash,
                                       full_name=full_name,
                                       is_superuser=superuser,
                                       permissions=permission_id)
    r = conn.execute(user)
    conn.close()


def permission_add(engine, group):
    # check first uf permission already exists
    conn = engine.connect()
    where = db.models.Permission.c.name == group
    q = select([db.models.Permission]).where(where)
    result = conn.execute(q)
    perm = result.fetchone()
    if perm is None:
        pq = db.models.Permission.insert().values(name=group)
        conn.execute(pq)
        where = db.models.Permission.c.name == group
        q = select([db.models.Permission]).where(where)
        result = conn.execute(q)
        permission = result.fetchone()

    else:
        log.warn("Permission '{}'\
already exists. Using that one.".format(group))
        permission = perm
    conn.close()
    return permission


def get_user(engine, user):
    conn = engine.connect()
    where = models.User.c.login == user
    q = models.User.select().where(where)
    result = conn.execute(q)
    user = result.fetchone()
    conn.close()
    return user


def update_user_password(engine, user, password):
    pass_hash = pbkdf2_sha512.encrypt(password)
    conn = engine.connect()
    where = models.User.c.login == user
    q = models.User.update().where(where).values(password=pass_hash)
    try:
        conn.execute(q)
    except Exception as e:
        log.exception(e)
    conn.close()


def verify_password(user, password):
    if pbkdf2_sha512.verify(password, user.password):
        print("OK")
    else:
        log.error("Password does not match!")
