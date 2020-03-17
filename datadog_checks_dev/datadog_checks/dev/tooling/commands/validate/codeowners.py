# (C) Datadog, Inc. 2020-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import re

import click

from ...utils import get_codeowners, get_valid_integrations
from ..console import CONTEXT_SETTINGS, echo_failure, echo_success

DIRECTORY_REGEX = re.compile(r"\/(.*)\/$")


def get_all_checks_with_codeowners():
    codeowners = get_codeowners()

    checks_with_codeowners = set()
    checks_with_only_entries = set()

    for entry in codeowners:
        parts = [part for part in entry.split(" ") if part != "" and part != "\t"]
        if not parts:
            continue
        match = DIRECTORY_REGEX.match(parts[0])
        if match and match.group(1):
            check = match.group(1)
            if len(parts) != 2:
                checks_with_only_entries.add(check)
            else:
                checks_with_codeowners.add(check)
    return checks_with_codeowners, checks_with_only_entries


@click.command(
    'codeowners',
    context_settings=CONTEXT_SETTINGS,
    short_help='Validate `CODEOWNERS` file has an entry for each integration',
)
def codeowners():
    """Validate that every integration has an entry in the `CODEOWNERS` file."""
    all_checks_with_codeowners, checks_with_only_entries = get_all_checks_with_codeowners()
    all_checks = get_valid_integrations()
    has_failed = False

    for check in all_checks:
        if check in checks_with_only_entries:
            has_failed = True
            echo_failure(f"Integration {check} has a `CODEOWNERS` entry, but the codeowner is empty.")
        elif check not in all_checks_with_codeowners:
            has_failed = True
            echo_failure(f"Integration {check} does not have a valid `CODEOWNERS` entry.")

    if not has_failed:
        echo_success("All integrations have codeowners.")
