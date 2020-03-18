# (C) Datadog, Inc. 2020-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import os
from typing import Callable, Dict, List, Set, Tuple, Union

import pytest

from datadog_checks.base.stubs.aggregator import AggregatorStub
from datadog_checks.dev import get_docker_hostname, get_here

from .types import ServerName

HERE = get_here()

CHECK_NAME = 'rethinkdb'

IMAGE = os.environ.get('RETHINKDB_IMAGE', '')
RAW_VERSION = os.environ.get('RETHINKDB_RAW_VERSION', '')

HOST = get_docker_hostname()

TAGS = ['env:testing']

# Servers.
# NOTE: server information is tightly coupled to the Docker Compose setup.

SERVERS = {'server0', 'server1', 'server2'}  # type: Set[ServerName]
BOOTSTRAP_SERVER = 'server0'  # type: ServerName
SERVER_PORTS = {'server0': 28015, 'server1': 28016, 'server2': 28017, 'proxy': 28018}  # type: Dict[ServerName, int]
SERVER_TAGS = {
    'server0': ['default', 'us'],
    'server1': ['default', 'us', 'primary'],
    'server2': ['default', 'eu'],
}  # type: Dict[ServerName, List[str]]

# Users.

AGENT_USER = 'datadog-agent'
AGENT_PASSWORD = 'r3th1nK'
CLIENT_USER = 'doggo'

# TLS.

TLS_SERVER = 'server1'  # type: ServerName
TLS_DRIVER_KEY = os.path.join(HERE, 'data', 'tls', 'server.key')
TLS_DRIVER_CERT = os.path.join(HERE, 'data', 'tls', 'server.pem')
TLS_CLIENT_CERT = os.path.join(HERE, 'data', 'tls', 'client.pem')

# Database content.

DATABASE = 'doghouse'

HEROES_TABLE = 'heroes'
HEROES_TABLE_CONFIG = {
    'shards': 1,
    'replicas': {'primary': 1, 'eu': 1},
    'primary_replica_tag': 'primary',
}
HEROES_TABLE_SERVERS = {'server1', 'server2'}  # type: Set[ServerName]
HEROES_TABLE_PRIMARY_REPLICA = 'server1'  # type: ServerName
HEROES_TABLE_REPLICAS_BY_SHARD = {0: HEROES_TABLE_SERVERS}
HEROES_TABLE_DOCUMENTS = [
    {
        "hero": "Magneto",
        "name": "Max Eisenhardt",
        "aka": ["Magnus", "Erik Lehnsherr", "Lehnsherr"],
        "magazine_titles": ["Alpha Flight", "Avengers", "Avengers West Coast"],
        "appearances_count": 42,
    },
    {
        "hero": "Professor Xavier",
        "name": "Charles Francis Xavier",
        "magazine_titles": ["Alpha Flight", "Avengers", "Bishop", "Defenders"],
        "appearances_count": 72,
    },
    {
        "hero": "Storm",
        "name": "Ororo Monroe",
        "magazine_titles": ["Amazing Spider-Man vs. Wolverine", "Excalibur", "Fantastic Four", "Iron Fist"],
        "appearances_count": 72,
    },
]
HEROES_TABLE_INDEX_FIELD = 'appearances_count'

# Metrics lists.
# NOTE: jobs metrics are not listed here as they're hard to trigger, so they're covered by unit tests instead.

CONFIG_TOTALS_METRICS = (
    (
        'rethinkdb.server.total',
        AggregatorStub.GAUGE,
        lambda disconnected_servers: len(SERVERS) - len(disconnected_servers),
        [],
    ),
    ('rethinkdb.database.total', AggregatorStub.GAUGE, 1, []),
    ('rethinkdb.database.table.total', AggregatorStub.GAUGE, 1, ['database:{}'.format(DATABASE)]),
    ('rethinkdb.table.secondary_index.total', AggregatorStub.GAUGE, 1, ['table:{}'.format(HEROES_TABLE)]),
)  # type: Tuple[Tuple[str, int, Union[int, Callable[[set], int]], List[str]], ...]

CLUSTER_STATISTICS_METRICS = (
    ('rethinkdb.stats.cluster.queries_per_sec', AggregatorStub.GAUGE),
    ('rethinkdb.stats.cluster.read_docs_per_sec', AggregatorStub.GAUGE),
    ('rethinkdb.stats.cluster.written_docs_per_sec', AggregatorStub.GAUGE),
)  # type: Tuple[Tuple[str, int], ...]

SERVER_STATISTICS_METRICS = (
    ('rethinkdb.stats.server.queries_per_sec', AggregatorStub.GAUGE),
    ('rethinkdb.stats.server.queries_total', AggregatorStub.MONOTONIC_COUNT),
    ('rethinkdb.stats.server.read_docs_per_sec', AggregatorStub.GAUGE),
    ('rethinkdb.stats.server.read_docs_total', AggregatorStub.MONOTONIC_COUNT),
    ('rethinkdb.stats.server.written_docs_per_sec', AggregatorStub.GAUGE),
    ('rethinkdb.stats.server.written_docs_total', AggregatorStub.MONOTONIC_COUNT),
    ('rethinkdb.stats.server.client_connections', AggregatorStub.GAUGE),
    (
        # NOTE: submitted but not documented on the RethinkDB website.
        'rethinkdb.stats.server.clients_active',
        AggregatorStub.GAUGE,
    ),
)  # type: Tuple[Tuple[str, int], ...]

TABLE_STATISTICS_METRICS = (
    ('rethinkdb.stats.table.read_docs_per_sec', AggregatorStub.GAUGE),
    ('rethinkdb.stats.table.written_docs_per_sec', AggregatorStub.GAUGE),
)  # type: Tuple[Tuple[str, int], ...]

REPLICA_STATISTICS_METRICS = (
    ('rethinkdb.stats.table_server.read_docs_per_sec', AggregatorStub.GAUGE),
    ('rethinkdb.stats.table_server.read_docs_total', AggregatorStub.MONOTONIC_COUNT),
    ('rethinkdb.stats.table_server.written_docs_per_sec', AggregatorStub.GAUGE),
    ('rethinkdb.stats.table_server.written_docs_total', AggregatorStub.MONOTONIC_COUNT),
    ('rethinkdb.stats.table_server.cache.in_use_bytes', AggregatorStub.GAUGE),
    ('rethinkdb.stats.table_server.disk.read_bytes_per_sec', AggregatorStub.GAUGE),
    ('rethinkdb.stats.table_server.disk.read_bytes_total', AggregatorStub.MONOTONIC_COUNT),
    ('rethinkdb.stats.table_server.disk.written_bytes_per_sec', AggregatorStub.GAUGE),
    ('rethinkdb.stats.table_server.disk.written_bytes_total', AggregatorStub.MONOTONIC_COUNT),
    ('rethinkdb.stats.table_server.disk.metadata_bytes', AggregatorStub.GAUGE),
    ('rethinkdb.stats.table_server.disk.data_bytes', AggregatorStub.GAUGE),
    ('rethinkdb.stats.table_server.disk.garbage_bytes', AggregatorStub.GAUGE),
    ('rethinkdb.stats.table_server.disk.preallocated_bytes', AggregatorStub.GAUGE),
)  # type: Tuple[Tuple[str, int], ...]

TABLE_STATUS_SERVICE_CHECKS = (
    'rethinkdb.table_status.ready_for_outdated_reads',
    'rethinkdb.table_status.ready_for_reads',
    'rethinkdb.table_status.ready_for_writes',
    'rethinkdb.table_status.all_replicas_ready',
)

TABLE_STATUS_METRICS = (
    ('rethinkdb.table_status.shards.total', AggregatorStub.GAUGE),
)  # type: Tuple[Tuple[str, int], ...]

TABLE_STATUS_SHARDS_METRICS = (
    ('rethinkdb.table_status.shards.replicas.total', AggregatorStub.GAUGE),
    ('rethinkdb.table_status.shards.replicas.primary.total', AggregatorStub.GAUGE),
)  # type: Tuple[Tuple[str, int], ...]

SERVER_STATUS_METRICS = (
    ('rethinkdb.server_status.network.time_connected', AggregatorStub.GAUGE),
    ('rethinkdb.server_status.network.connected_to.total', AggregatorStub.GAUGE),
    ('rethinkdb.server_status.network.connected_to.pending.total', AggregatorStub.GAUGE),
    ('rethinkdb.server_status.process.time_started', AggregatorStub.GAUGE),
)  # type: Tuple[Tuple[str, int], ...]

CURRENT_ISSUES_METRICS = (
    ('rethinkdb.current_issues.total', AggregatorStub.GAUGE),
    ('rethinkdb.current_issues.critical.total', AggregatorStub.GAUGE),
)  # type: Tuple[Tuple[str, int], ...]

CURRENT_ISSUE_TYPES_SUBMITTED_IF_DISCONNECTED_SERVERS = ['table_availability']


E2E_METRICS = (
    tuple((name, typ) for name, typ, _, _ in CONFIG_TOTALS_METRICS)
    + CLUSTER_STATISTICS_METRICS
    + SERVER_STATISTICS_METRICS
    + TABLE_STATISTICS_METRICS
    + REPLICA_STATISTICS_METRICS
    + TABLE_STATUS_METRICS
    + TABLE_STATUS_SHARDS_METRICS
    + SERVER_STATUS_METRICS
)  # type: Tuple[Tuple[str, int], ...]

# Docker Compose configuration.

COMPOSE_FILE = os.path.join(HERE, 'compose', 'docker-compose.yaml')

COMPOSE_ENV_VARS = env_vars = {
    'RETHINKDB_IMAGE': IMAGE,
    'RETHINKDB_PORT_SERVER0': str(SERVER_PORTS['server0']),
    'RETHINKDB_PORT_SERVER1': str(SERVER_PORTS['server1']),
    'RETHINKDB_PORT_SERVER2': str(SERVER_PORTS['server2']),
    'RETHINKDB_PORT_PROXY': str(SERVER_PORTS['proxy']),
    'RETHINKDB_TLS_DRIVER_KEY': TLS_DRIVER_KEY,
    'RETHINKDB_TLS_DRIVER_CERT': TLS_DRIVER_CERT,
}


# Pytest common test data.

MALFORMED_VERSION_STRING_PARAMS = [
    pytest.param('rethinkdb 2.3.3', id='no-compilation-string'),
    pytest.param('rethinkdb (GCC 4.9.2)', id='no-version'),
    pytest.param('rethinkdb', id='prefix-only'),
    pytest.param('abc 2.4.0~0bionic (GCC 4.9.2)', id='wrong-prefix'),
]