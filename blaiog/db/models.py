import sqlalchemy as sa
from sqlalchemy import Table, Column, String, Integer, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import logging
log = logging.getLogger('blaiog.db.models')
log.addHandler(logging.NullHandler())

Base = declarative_base()


class Permission(Base):
    __tablename__ = "permission"
    id = Column(Integer, primary_key=True,autoincrement=True)
    users = relationship("User", cascade="all, delete-orphan",
                            backref='permission')
    name = Column(String(256),nullable=False)
    
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True,autoincrement=True)
    login = Column(String(256),nullable=False)
    full_name = Column(String(256),nullable=False)
    password = Column(String(256),nullable=False)
    is_superuser = Column(Boolean,nullable=False,
                          server_default='0')
    disabled = Column(Boolean,nullable=False,
                          server_default='0')
    permissions = Column(Integer,ForeignKey('permission.id'),primary_key=True,nullable=True)
    
    posts = relationship('post')


class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True,autoincrement=True)
    title = sa.Column(String(256),nullable=False)
    url_title = sa.Column(String(256),nullable=False)
    writer_id = Column(Integer,ForeignKey('writer.id'),primary_key=True,nullable=False)
    short_body = sa.Column(Text(),nullable=True)
    body = sa.Column(Text(),nullable=False)
    created = sa.Column(DateTime,default=sa.func.now())
    last_update= sa.Column(DateTime,default=sa.func.now())
    active = sa.Column(Boolean,nullable=False,server_default="0")

