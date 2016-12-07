import sqlalchemy as sa
from sqlalchemy import MetaData, Table, Column, String
from sqlalchemy import Integer, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.dialects.mysql import TEXT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import logging

log = logging.getLogger('blaiog.db.models')
log.addHandler(logging.NullHandler())

Base = declarative_base()
metadata = MetaData()

Permission = Table('permission', metadata,
                   Column('id', Integer, primary_key=True, autoincrement=True),
                   Column('name', String(256), nullable=False))

User = Table("user", metadata,
             Column('id', Integer, primary_key=True, autoincrement=True),
             Column('login', String(256), nullable=False),
             Column('full_name', String(256), nullable=False),
             Column('password', String(256), nullable=False),
             Column('is_superuser', Boolean, nullable=False,
                    server_default='0'),
             Column('disabled', Boolean, nullable=False,
                    server_default='0'),
             Column('permissions', Integer, ForeignKey('permission.id'),
                    primary_key=True, nullable=True))

Post = Table('post', metadata,
             Column('id', Integer, primary_key=True, autoincrement=True),
             Column('title', String(256), nullable=False),
             Column('url_title', String(256), nullable=False),
             Column('writer_id', Integer, ForeignKey('user.id'),
                    primary_key=True, nullable=False),
             Column('short_body', TEXT(charset='utf8mb4'), nullable=True),
             Column('body', TEXT(charset='utf8mb4'), nullable=False),
             Column('created', DateTime, default=sa.func.now()),
             Column('last_update', DateTime, default=sa.func.now()),
             Column('active', Boolean, nullable=False, server_default="0"))

Page = Table('page', metadata,
             Column('id', Integer, primary_key=True, autoincrement=True),
             Column('title', String(256), nullable=False),
             Column('url_title', String(256), nullable=False),
             Column('writer_id', Integer, ForeignKey('user.id'),
                    primary_key=True, nullable=False),
             Column('short_body', TEXT(charset='utf8mb4'), nullable=True),
             Column('body', TEXT(charset='utf8mb4'), nullable=False),
             Column('created', DateTime, default=sa.func.now()),
             Column('last_update', DateTime, default=sa.func.now()),
             Column('active', Boolean, nullable=False, server_default="0"))
