# (C) Datadog, Inc. 2020-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
from .__about__ import __version__
from .sidekiq import SidekiqCheck

__all__ = ['__version__', 'SidekiqCheck']
