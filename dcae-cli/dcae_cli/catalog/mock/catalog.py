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
"""
Provides the mock catalog
"""
import os
import json
import contextlib
import itertools
from functools import partial
from datetime import datetime

import six

from sqlalchemy import create_engine as create_engine_, event, and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy_utils import database_exists, create_database, drop_database

from dcae_cli import _version as cli_version
from dcae_cli.catalog.mock.tables import Component, Format, FormatPair, Base
from dcae_cli.catalog.mock.schema import validate_component, validate_format, apply_defaults_docker_config
from dcae_cli.util import reraise_with_msg, get_app_dir
from dcae_cli.util.config import get_config, get_path_component_spec, \
    get_path_data_format
from dcae_cli.util.logger import get_logger
from dcae_cli.util.docker_util import image_exists
from dcae_cli.catalog.exc import CatalogError, DuplicateEntry, MissingEntry, FrozenEntry
from dcae_cli.util.cdap_util import normalize_cdap_params


logger = get_logger('Catalog')


#INTERNAL HELPERS
def _get_component(session, name, version):
    '''Returns a single component ORM'''
    try:
        if not version:
            query = session.query(Component).filter(Component.name==name).order_by(Component.version.desc()).limit(1)
        else:
            query = session.query(Component).filter(Component.name==name, Component.version==version)
        return query.one()
    except NoResultFound:
        comp_msg = "{}:{}".format(name, version) if version else name
        raise MissingEntry("Component '{}' was not found in the catalog".format(comp_msg))

def _get_docker_image_from_spec(spec):
    images = [ art["uri"] for art in spec["artifacts"] if art["type"] == "docker image" ]
    return images[0]

def _get_docker_image(session, name, version):
    '''Returns the docker image name of a given component'''
    comp = _get_component(session, name, version)
    return _get_docker_image_from_spec(comp.get_spec_as_dict())

def _add_docker_component(session, user, spec, update, enforce_image=True):
    '''Adds/updates a docker component to the catalog'''
    image = _get_docker_image_from_spec(spec)

    if enforce_image and not image_exists(image):
        raise CatalogError("Specified image '{}' does not exist locally.".format(image))

    comp = build_generic_component(session, user, spec, update)
    session.commit()

def _get_cdap_jar_from_spec(spec):
    jars = [ art["uri"] for art in spec["artifacts"] if art["type"] == "jar" ]
    return jars[0]

def _add_cdap_component(session, user, spec, update):
    '''Adds/updates a cdap component to the catalog'''
    comp = build_generic_component(session, user, spec, update)
    session.commit()


#PUBLIC FUNCTIONS
@contextlib.contextmanager
def SessionTransaction(engine):
    '''Provides a transactional scope around a series of operations'''
    Session = sessionmaker(engine)
    try:
        session = Session()
        yield session
        session.commit()
    except IntegrityError as e:
        session.rollback()
        _raise_if_duplicate(str(engine.url), e)
        raise
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


_dup_e = DuplicateEntry('Entry already exists. Try using the --update flag.')

def _raise_if_duplicate(url, e):
    '''Raises if the exception relates to duplicate entries'''
    if 'sqlite' in url:
        if 'UNIQUE' in e.orig.args[0].upper():
            raise _dup_e
    elif 'postgres' in url:
        # e.orig is of type psycopg2.IntegrityError that has 
        # pgcode which uses the following:
        #
        # https://www.postgresql.org/docs/current/static/errcodes-appendix.html#ERRCODES-TABLE
        #
        # 23505 means "unique_violation"
        if e.orig.pgcode == "23505":
            raise _dup_e

def create_engine(base, db_name=None, purge_existing=False, db_url=None):
    '''Returns an initialized database engine'''
    if db_url is None:
        if db_name is None:
            # no url or db name indicates we want to use the tool's configured db
            config = get_config()
            url = config['db_url']
        else:
            # if only a db name is given, interpret as a sqlite db in the app dir. this maintains backwards compat with existing tests.
            db_path = os.path.join(get_app_dir(), db_name)
            url = ''.join(('sqlite:///', db_path))
    else:
        # a full db url is the most explicit input and should be used over other inputs if provided
        url = db_url

    if not database_exists(url):
        create_database(url)
    elif purge_existing:
        drop_database(url)
        create_database(url)

    engine = create_engine_(url)
    _configure_engine(engine)
    base.metadata.create_all(engine)
    return engine


def _configure_engine(engine):
    '''Performs additional db-specific configurations'''
    str_url = str(engine.url)
    if 'sqlite' in str_url:
        event.listen(engine, 'connect', lambda conn, record: conn.execute('pragma foreign_keys=ON'))


def get_format(session, name, version):
    '''Returns a single data format ORM'''
    try:
        if not version:
            query = session.query(Format).filter(Format.name==name).order_by(Format.version.desc()).limit(1)
        else:
            query = session.query(Format).filter(Format.name==name, Format.version==version)
        return query.one()
    except NoResultFound:
        msg = "{}:{}".format(name, version) if version else name
        raise MissingEntry("Data format '{}' was not found in the catalog.".format(msg))

def _create_format_tuple(entry):
    '''Create tuple to identify format'''
    return (entry['format'], entry['version'])


def _get_format_pair(session, req_name, req_version, resp_name, resp_version, create=True):
    '''Returns a single data format pair ORM'''
    req = get_format(session, req_name, req_version)
    resp = get_format(session, resp_name, resp_version)

    query = session.query(FormatPair).filter(and_(FormatPair.req == req, FormatPair.resp == resp))
    try:
        return query.one()
    except NoResultFound:
        if not create:
            raise MissingEntry("Data format pair with request '{}:{}' and response '{}:{}' was not found in the catalog.".format(req.name, req.version, resp.name, resp.version))

    pair = FormatPair(req=req, resp=resp)
    session.add(pair)
    return pair

def _create_format_pair_tuple(entry):
    '''Create tuple to identify format pair'''
    req_name, req_version = entry['request']['format'], entry['request']['version']
    resp_name, resp_version = entry['response']['format'], entry['response']['version']
    return (req_name, req_version, resp_name, resp_version)

def _get_unique_format_things(create_tuple, get_func, entries):
    '''Get unique format things (formats, format pairs, ..)

    Args
    ----
    create_tuple: Function that has the signature dict->tuple
    get_func: Function that has the signature *tuple->orm
    entries: list of dicts that have data format details that come from
    streams.publishes, streams.subscribes, services.calls, services.provides

    Return
    ------
    List of unique orms
    '''
    src = set(create_tuple(entry) for entry in entries)
    return [get_func(*yo) for yo in src]


def verify_component(session, name, version):
    '''Returns the orm name and version of a given component'''
    orm = _get_component(session, name, version)
    return orm.name, orm.version


def get_component_type(session, name, version):
    '''Returns the component_type of a given component'''
    return _get_component(session, name, version).component_type


def get_component_spec(session, name, version):
    '''Returns the spec dict of a given component'''
    return json.loads(_get_component(session, name, version).spec)


def get_format_spec(session, name, version):
    '''Returns the spec dict of a given data format'''
    return json.loads(get_format(session, name, version).spec)


def build_generic_component(session, user, spec, update):
    '''Builds, adds, and returns a generic component ORM. Does not commit changes.'''
    attrs = spec['self'].copy()
    attrs['spec'] = json.dumps(spec)

    # TODO: This should really come from the spec too
    attrs['owner'] = user

    # grab existing or create a new component
    name, version = attrs['name'], attrs['version']
    if update:
        comp = _get_component(session, name, version)
        if comp.is_published():
            raise FrozenEntry("Component '{}:{}' has been pushed and cannot be updated".format(name, version))
    else:
        comp = Component()
        session.add(comp)

    # REVIEW: Inject these parameters as function arguments instead of this
    # hidden approach?
    # WATCH: This has to be done here before the code below because there is a
    # commit somewhere below and since these fields are not nullable, you'll get a
    # violation.
    comp.cli_version = cli_version.__version__
    comp.schema_path = get_path_component_spec()

    # build the ORM
    for attr, val in six.iteritems(attrs):
        setattr(comp, attr, val)

    # update relationships
    get_format_local = partial(get_format, session)
    get_unique_formats = partial(_get_unique_format_things, _create_format_tuple,
            get_format_local)

    try:
        comp.publishes = get_unique_formats(spec['streams']['publishes'])
    except MissingEntry as e:
        reraise_with_msg(e, 'Add failed while traversing "publishes"')

    try:
        comp.subscribes = get_unique_formats(spec['streams']['subscribes'])
    except MissingEntry as e:
        reraise_with_msg(e, 'Add failed while traversing "subscribes"')

    get_format_pairs = partial(_get_format_pair, session)
    get_unique_format_pairs = partial(_get_unique_format_things,
            _create_format_pair_tuple, get_format_pairs)

    try:
        comp.provides = get_unique_format_pairs(spec['services']['provides'])
    except MissingEntry as e:
        reraise_with_msg(e, 'Add failed while traversing "provides"')

    try:
        comp.calls = get_unique_format_pairs(spec['services']['calls'])
    except MissingEntry as e:
        reraise_with_msg(e, 'Add failed while traversing "calls"')

    return comp


def add_format(session, spec, user, update):
    '''Helper function which adds a data format to the catalog'''
    attrs = spec['self'].copy()
    attrs['spec'] = json.dumps(spec)
    name, version = attrs['name'], attrs['version']

    # TODO: This should really come from the spec too
    attrs['owner'] = user

    if update:
        data_format = get_format(session, name, version)
        if data_format.is_published():
            raise FrozenEntry("Data format {}:{} has been pushed and cannot be updated".format(name, version))
    else:
        data_format = Format()
        session.add(data_format)

    # build the ORM
    for attr, val in six.iteritems(attrs):
        setattr(data_format, attr, val)

    # REVIEW: Inject these parameters as function arguments instead of this
    # hidden approach?
    data_format.cli_version = cli_version.__version__
    data_format.schema_path = get_path_data_format()

    session.commit()


def _filter_neighbors(session, neighbors=None):
    '''Returns a Component query filtered by available neighbors'''
    if neighbors is None:
        query = session.query(Component)
    else:
        subfilt = or_(and_(Component.name==n, Component.version==v) for n,v in neighbors)
        query = session.query(Component).filter(subfilt)
    return query


def get_subscribers(session, orm, neighbors=None):
    '''Returns a list of component ORMs which subscribe to the specified format'''
    query = _filter_neighbors(session, neighbors)
    return query.filter(Component.subscribes.contains(orm)).all()


def get_providers(session, orm, neighbors=None):
    '''Returns a list of component ORMs which provide the specified format pair'''
    query = _filter_neighbors(session, neighbors)
    return query.filter(Component.provides.contains(orm)).all()


def _match_pub(entries, orms):
    '''Aligns the publishes orms with spec entries to get the config key'''
    lookup = {(orm.name, orm.version): orm for orm in orms}
    for entry in entries:
        if "http" not in entry["type"]:
            continue

        key = (entry['format'], entry['version'])
        yield entry['config_key'], lookup[key]


def _match_call(entries, orms):
    '''Aligns the calls orms with spec entries to get the config key'''
    lookup = {(orm.req.name, orm.req.version, orm.resp.name, orm.resp.version): orm for orm in orms}
    for entry in entries:
        key = (entry['request']['format'], entry['request']['version'], entry['response']['format'], entry['response']['version'])
        yield entry['config_key'], lookup[key]

def get_discovery(get_params_func, session, name, version,  neighbors=None):
    '''Returns the parameters and interface map for a given component and considering its neighbors'''
    comp = _get_component(session, name, version)
    spec = json.loads(comp.spec)
    interfaces = dict()
    for key, orm in _match_pub(spec['streams']['publishes'], comp.publishes):
        interfaces[key] = [(c.name, c.version) for c in get_subscribers(session, orm, neighbors) if not c is comp]

    for key, orm in _match_call(spec['services']['calls'], comp.calls):
        interfaces[key] = [(c.name, c.version) for c in get_providers(session, orm, neighbors) if not c is comp]

    params = get_params_func(spec)
    return params, interfaces

_get_discovery_for_cdap = partial(get_discovery, normalize_cdap_params)
_get_discovery_for_docker = partial(get_discovery,
        lambda spec: {param['name']: param['value'] for param in spec['parameters']})


def _get_discovery_for_dmaap(get_component_spec_func, name, version):
    """Get all config keys that are for dmaap streams

    Returns:
    --------
    Tuple of message router config keys list, data router config keys list
    """
    spec = get_component_spec_func(name, version)

    all_streams = spec["streams"].get("publishes", []) \
            + spec["streams"].get("subscribes", [])

    def is_for_message_router(stream):
        return stream["type"] == "message router" \
                or stream["type"] == "message_router"

    mr_keys = [ stream["config_key"] for stream in filter(is_for_message_router, all_streams) ]

    def is_for_data_router(stream):
        return stream["type"] == "data router" \
                or stream["type"] == "data_router"

    dr_keys = [ stream["config_key"] for stream in filter(is_for_data_router, all_streams) ]
    return mr_keys, dr_keys


def _filter_latest(orms):
    '''Filters and yields only (name, version, *) orm tuples with the highest version'''
    get_first_key_func = lambda x: x[0]
    # itertools.groupby requires the input to be sorted
    sorted_orms = sorted(orms, key=get_first_key_func)
    for _, g in itertools.groupby(sorted_orms, get_first_key_func):
        yield max(g, key=lambda x: x[1])


def list_components(session, user, only_published, subscribes=None, publishes=None,
        provides=None, calls=None, latest=True):
    """Get list of components

    Returns:
    --------
    List of component orms as dicts
    """
    filters = list()
    if subscribes:
        filters.extend(Component.subscribes.contains(get_format(session, n, v)) for n, v in subscribes)
    if publishes:
        filters.extend(Component.publishes.contains(get_format(session, n, v)) for n, v in publishes)
    if provides:
        filters.extend(Component.provides.contains(_get_format_pair(session, reqn, reqv, respn, respv, create=False))
                       for (reqn, reqv), (respn, respv) in provides)
    if calls:
        filters.extend(Component.calls.contains(_get_format_pair(session, reqn, reqv, respn, respv, create=False))
                       for (reqn, reqv), (respn, respv) in calls)
    if filters:
        query = session.query(Component).filter(or_(*filters))
    else:
        query = session.query(Component)

    if user:
        query = query.filter(Component.owner==user)
    if only_published:
        query = query.filter(Component.when_published!=None)

    orms = ((orm.name, orm.version, orm.component_type, orm) for orm in query)

    if latest:
        orms = _filter_latest(orms)

    return [ orm.__dict__ for _, _, _, orm in orms ]


def _list_formats(session, user, only_published, latest=True):
    """Get list of data formats

    Returns
    -------
    List of data format orms as dicts
    """
    query = session.query(Format).order_by(Format.modified.desc())

    if user:
        query = query.filter(Format.owner==user)
    if only_published:
        query = query.filter(Format.when_published!=None)

    orms = [ (orm.name, orm.version, orm) for orm in query ]

    if latest:
        orms = _filter_latest(orms)
    return [ orm.__dict__ for _, _, orm in orms ]


def build_config_keys_map(spec):
    """Build config keys map

    Return
    ------
    Dict where each item:

        <config_key>: { "group": <grouping>, "type": <http|message_router|data_router> }

    where grouping includes "streams_publishes", "streams_subscribes", "services_calls"
    """
    # subscribing as http doesn't have config key
    ss = [ (s["config_key"], { "group": "streams_subscribes", "type": s["type"] })
        for s in spec["streams"]["subscribes"] if "config_key" in s]
    sp = [ (s["config_key"], { "group": "streams_publishes", "type": s["type"] })
        for s in spec["streams"]["publishes"] ]
    sc = [ (s["config_key"], { "group": "services_calls" })
        for s in spec["services"]["calls"] ]
    return dict(ss+sp+sc)


def get_data_router_subscriber_route(spec, config_key):
    """Get route by config key for data router subscriber

    Utility method that parses the component spec
    """
    for s in spec["streams"].get("subscribes", []):
        if s["type"] in ["data_router", "data router"] \
                and s["config_key"] == config_key:
            return s["route"]

    raise MissingEntry("No data router subscriber for {0}".format(config_key))


class MockCatalog(object):

    def __init__(self, purge_existing=False, enforce_image=True, db_name=None, engine=None, db_url=None):
        self.engine = create_engine(Base, db_name=db_name, purge_existing=purge_existing, db_url=db_url) if engine is None else engine
        self.enforce_image = enforce_image

    def add_component(self, user, spec, update=False):
        '''Validates component specification and adds component to the mock catalog'''
        validate_component(spec)

        component_type = spec["self"]["component_type"]

        with SessionTransaction(self.engine) as session:
            if component_type == "cdap":
                _add_cdap_component(session, user, spec, update)
            elif component_type == "docker":
                _add_docker_component(session, user, spec, update,
                        enforce_image=self.enforce_image)
            else:
                raise CatalogError("Unknown component type: {0}".format(component_type))

    def get_docker_image(self, name, version):
        '''Returns the docker image name associated with this component'''
        with SessionTransaction(self.engine) as session:
            return _get_docker_image(session, name, version)

    def get_docker(self, name, version):
        with SessionTransaction(self.engine) as session:
            comp = _get_component(session, name, version)
            spec = comp.get_spec_as_dict()
            # NOTE: Defaults are being applied for docker config here at read
            # time. Not completely sure that this is the correct approach. The
            # benefit is that defaults can be changed without altering the stored
            # specs. It's a nice layering.
            docker_config = apply_defaults_docker_config(spec["auxilary"])
            return _get_docker_image_from_spec(spec), docker_config, spec

    def get_docker_config(self, name, version):
        _, docker_config, _ = self.get_docker(name, version)
        return docker_config

    def get_cdap(self, name, version):
        '''Returns a tuple representing this cdap component

        Returns
        -------
        tuple(jar, config, spec)
            jar: string
                URL where the CDAP jar is located.
            config: dict
                A dictionary loaded from the CDAP JSON configuration file.
            spec: dict
                The dcae-cli component specification file.
        '''
        with SessionTransaction(self.engine) as session:
            comp = _get_component(session, name, version)
            spec = comp.get_spec_as_dict()
            cdap_config = spec["auxilary"]
            return _get_cdap_jar_from_spec(spec), cdap_config, spec

    def get_component_type(self, name, version):
        '''Returns the component type associated with this component'''
        with SessionTransaction(self.engine) as session:
            return get_component_type(session, name, version)

    def get_component_spec(self, name, version):
        '''Returns the spec dict associated with this component'''
        with SessionTransaction(self.engine) as session:
            return get_component_spec(session, name, version)

    def get_format_spec(self, name, version):
        '''Returns the spec dict associated with this data format'''
        with SessionTransaction(self.engine) as session:
            return get_format_spec(session, name, version)

    def add_format(self, spec, user, update=False):
        '''Validates data format specification and adds data format to the mock catalog'''
        validate_format(spec)
        with SessionTransaction(self.engine) as session:
            add_format(session, spec, user, update)

    def get_discovery_for_cdap(self, name, version, neighbors=None):
        '''Returns the parameters and interface map for a given component and considering its neighbors'''
        with SessionTransaction(self.engine) as session:
            return _get_discovery_for_cdap(session, name, version, neighbors)

    def get_discovery_for_docker(self, name, version, neighbors=None):
        '''Returns the parameters and interface map for a given component and considering its neighbors'''
        with SessionTransaction(self.engine) as session:
            return _get_discovery_for_docker(session, name, version, neighbors)

    def get_discovery_for_dmaap(self, name, version):
        with SessionTransaction(self.engine) as session:
            get_component_spec_func = partial(get_component_spec, session)
            return _get_discovery_for_dmaap(get_component_spec_func, name, version)

    def get_discovery_from_spec(self, user, target_spec, neighbors=None):
        '''Get pieces to generate configuration for the given target spec

        This function is used to obtain the pieces needed to generate
        the application configuration json: parameters map, interfaces map, dmaap
        map. Where the input is a provided specification that hasn't been added to
        the catalog - prospective specs - which includes a component that doesn't
        exist or a new version of an existing spec.

        Returns
        -------
        Tuple of three elements:

        - Dict of parameter name to parameter value
        - Dict of "config_key" to list of (component.name, component.version)
          known as "interface_map"
        - Tuple of lists of "config_key" the first for message router the second
          for data router known as "dmaap_map"
        '''
        validate_component(target_spec)

        with SessionTransaction(self.engine) as session:
            # The following approach was taken in order to:
            # 1. Re-use existing functionality e.g. implement fast
            # 2. In order to make ORM-specific queries, I need the entire ORM
            # in SQLAlchemy meaning I cannot do arbitrary DataFormatPair queries
            # without Component.
            name = target_spec["self"]["name"]
            version = target_spec["self"]["version"]

            try:
                # Build a component with update to True first because you may
                # want to run this for an existing component
                build_generic_component(session, user, target_spec, True)
            except MissingEntry:
                # Since it doesn't exist already, build a new component
                build_generic_component(session, user, target_spec, False)

            # This is needed so that subsequent queries will "see" the component
            session.flush()

            ctype = target_spec["self"]["component_type"]

            if ctype == "cdap":
                params, interface_map = _get_discovery_for_cdap(session, name,
                        version, neighbors)
            elif ctype == "docker":
                params, interface_map = _get_discovery_for_docker(session, name,
                        version, neighbors)

            # Don't want to commit these changes so rollback.
            session.rollback()

            # Use the target spec as the source to compile the config keys from
            dmaap_config_keys = _get_discovery_for_dmaap(
                    lambda name, version: target_spec, name, version)

            return params, interface_map, dmaap_config_keys

    def verify_component(self, name, version):
        '''Returns the component's name and version if it exists and raises an exception otherwise'''
        with SessionTransaction(self.engine) as session:
            return verify_component(session, name, version)

    def list_components(self, subscribes=None, publishes=None, provides=None,
            calls=None, latest=True, user=None, only_published=False):
        '''Returns a list of component names which match the specified filter sequences'''
        with SessionTransaction(self.engine) as session:
            return list_components(session, user, only_published, subscribes,
                    publishes, provides, calls, latest)

    def list_formats(self, latest=True, user=None, only_published=False):
        """Get list of data formats

        Returns
        -------
        List of data formats as dicts
        """
        with SessionTransaction(self.engine) as session:
            return _list_formats(session, user, only_published, latest)

    def get_format(self, name, version):
        """Get data format

        Throws MissingEntry exception if no matches found.

        Returns
        -------
        Dict representation of data format
        """
        with SessionTransaction(self.engine) as session:
            return get_format(session, name, version).__dict__

    def _publish(self, get_func, user, name, version):
        """Publish data format

        Args:
        -----
        get_func: Function that takes a session, name, version and outputs a data
            object either Component or Format

        Returns:
        --------
        True upon success else False
        """
        # TODO: To make function composeable, it should take in the data format
        # object
        with SessionTransaction(self.engine) as session:
            obj = get_func(session, name, version)

            if obj:
                if obj.owner != user:
                    logger.error("Not authorized to modify component or data format")
                    return False
                elif obj.when_published:
                    logger.warn("Component or data format has already been published")
                    return False
                else:
                    obj.when_published = datetime.utcnow()
                    session.commit()
            else:
                logger.error("Component or data format not found: {0}, {1}".format(name, version))
                return False

        return True

    def publish_format(self, user, name, version):
        """Publish data format

        Returns
        -------
        True upon success else False
        """
        return self._publish(get_format, user, name, version)

    def get_unpublished_formats(self, comp_name, comp_version):
        """Get unpublished formats for given component

        Returns:
        --------
        List of unique data format name, version pairs
        """
        with SessionTransaction(self.engine) as session:
            comp = _get_component(session, comp_name, comp_version)

            dfs = comp.publishes + comp.subscribes
            dfs += [ p.req for p in comp.provides]
            dfs += [ p.resp for p in comp.provides]
            dfs += [ c.req for c in comp.calls]
            dfs += [ c.resp for c in comp.calls]

            def is_not_published(orm):
                return orm.when_published == None

            formats = [(df.name, df.version) for df in filter(is_not_published, dfs)]
            return list(set(formats))

    def publish_component(self, user, name, version):
        """Publish component

        Returns
        -------
        True upon success else False
        """
        return self._publish(_get_component, user, name, version)
