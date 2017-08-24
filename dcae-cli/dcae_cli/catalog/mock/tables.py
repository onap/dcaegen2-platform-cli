# ============LICENSE_START=======================================================
# org.onap.dcae
# ================================================================================
# Copyright (c) 2017 AT&T Intellectual Property. All rights reserved.
# ================================================================================
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============LICENSE_END=========================================================
#
# ECOMP is a trademark and service mark of AT&T Intellectual Property.

# -*- coding: utf-8 -*-
'''
Provides a local mock catalog
'''
import uuid
import json
from datetime import datetime

from sqlalchemy import UniqueConstraint, Table, Column, String, DateTime, ForeignKey, Boolean, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import PrimaryKeyConstraint


datetime_now = datetime.utcnow

Base = declarative_base()


published = Table('published', Base.metadata,
    Column('component_id', String, ForeignKey('components.id', ondelete='CASCADE'), nullable=False),
    Column('format_id', String, ForeignKey('formats.id', ondelete='CASCADE'), nullable=False),
    PrimaryKeyConstraint('component_id', 'format_id')
)


subscribed = Table('subscribed', Base.metadata,
    Column('component_id', String, ForeignKey('components.id', ondelete='CASCADE'), nullable=False),
    Column('format_id', String, ForeignKey('formats.id', ondelete='CASCADE'), nullable=False),
    PrimaryKeyConstraint('component_id', 'format_id')
)


provided = Table('provided', Base.metadata,
    Column('component_id', String, ForeignKey('components.id', ondelete='CASCADE'), nullable=False),
    Column('pair_id', String, ForeignKey('format_pairs.id', ondelete='CASCADE'), nullable=False),
    PrimaryKeyConstraint('component_id', 'pair_id')
)


called = Table('called', Base.metadata,
    Column('component_id', String, ForeignKey('components.id', ondelete='CASCADE'), nullable=False),
    Column('pair_id', String, ForeignKey('format_pairs.id', ondelete='CASCADE'), nullable=False),
    PrimaryKeyConstraint('component_id', 'pair_id')
)


def generate_uuid():
    return str(uuid.uuid4())


class Component(Base):
    __tablename__ = 'components'
    id = Column(String, primary_key=True, default=generate_uuid)
    created = Column(DateTime, default=datetime_now, nullable=False)
    modified = Column(DateTime, default=datetime_now, onupdate=datetime_now, nullable=False)
    owner = Column(String, nullable=False)
    # To be used for tracking and debugging
    cli_version = Column(String, nullable=False)
    schema_path = Column(String, nullable=False)

    name = Column(String(), nullable=False)
    component_type = Column(Enum('docker', 'cdap', name='component_types'), nullable=False)
    version = Column(String(), nullable=False)
    description = Column(Text(), nullable=False)
    spec = Column(Text(), nullable=False)

    when_added = Column(DateTime, default=datetime_now, nullable=True)
    when_published = Column(DateTime, default=None, nullable=True)
    when_revoked = Column(DateTime, default=None, nullable=True)

    publishes = relationship('Format', secondary=published)
    subscribes = relationship('Format', secondary=subscribed)
    provides = relationship('FormatPair', secondary=provided)
    calls = relationship('FormatPair', secondary=called)

    __tableargs__ = (UniqueConstraint(name, version), )

    def __repr__(self):
        return '<{:}>'.format((self.__class__.__name__, self.id, self.name, self.version))

    def is_published(self):
        return self.when_published is not None

    def get_spec_as_dict(self):
        return json.loads(self.spec)


class Format(Base):
    __tablename__ = 'formats'
    id = Column(String, primary_key=True, default=generate_uuid)
    created = Column(DateTime, default=datetime_now, nullable=False)
    modified = Column(DateTime, default=datetime_now, onupdate=datetime_now, nullable=False)
    owner = Column(String, nullable=False)
    # To be used for tracking and debugging
    cli_version = Column(String, nullable=False)
    schema_path = Column(String, nullable=False)

    name = Column(String(), nullable=False)
    version = Column(String(), nullable=False)
    description = Column(Text(), nullable=False)
    spec = Column(Text(), nullable=False)

    when_added = Column(DateTime, default=datetime_now, nullable=True)
    when_published = Column(DateTime, default=None, nullable=True)
    when_revoked = Column(DateTime, default=None, nullable=True)

    __tableargs__ = (UniqueConstraint(name, version), )

    def __repr__(self):
        return '<{:}>'.format((self.__class__.__name__, self.id, self.name, self.version))

    def is_published(self):
        return self.when_published is not None


class FormatPair(Base):
    __tablename__ = 'format_pairs'
    id = Column(String, primary_key=True, default=generate_uuid)
    req_id = Column(String, ForeignKey('formats.id', ondelete='CASCADE'))
    resp_id = Column(String, ForeignKey('formats.id', ondelete='CASCADE'))

    req = relationship('Format', foreign_keys=req_id, uselist=False)
    resp = relationship('Format', foreign_keys=resp_id, uselist=False)

    __table_args__ = (UniqueConstraint(req_id, resp_id), )

    def __repr__(self):
        return '<{:}>'.format((self.__class__.__name__, self.id, self.req, self.resp))
