# (C) Datadog, Inc. 2018-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import json
import os
import re
from ast import literal_eval

import requests
import semver

from ..utils import dir_exists, file_exists, read_file, write_file
from .config import load_config
from .constants import NOT_CHECKS, REPO_CHOICES, REPO_OPTIONS_MAP, VERSION_BUMP, get_root, set_root
from .git import get_latest_tag

# match integration's version within the __about__.py module
VERSION = re.compile(r'__version__ *= *(?:[\'"])(.+?)(?:[\'"])')


def format_commit_id(commit_id):
    if commit_id:
        if commit_id.isdigit():
            return f'PR #{commit_id}'
        else:
            return f'commit hash `{commit_id}`'
    return commit_id


def get_current_agent_version():
    release_data = requests.get('https://raw.githubusercontent.com/DataDog/datadog-agent/master/release.json').json()
    versions = set()

    for version in release_data:
        parts = version.split('.')
        if len(parts) > 1:
            versions.add((int(parts[0]), int(parts[1])))

    most_recent = sorted(versions)[-1]

    return f"{most_recent[0]}.{most_recent[1]}"


def is_package(d):
    return file_exists(os.path.join(d, 'setup.py'))


def normalize_package_name(package_name):
    return re.sub(r'[-_. ]+', '_', package_name).lower()


def string_to_toml_type(s):
    if s.isdigit():
        s = int(s)
    elif s == 'true':
        s = True
    elif s == 'false':
        s = False
    elif s.startswith('['):
        s = literal_eval(s)

    return s


def get_check_file(check_name):
    return os.path.join(get_root(), check_name, 'datadog_checks', check_name, check_name + '.py')


def check_root():
    """Check if root has already been set."""
    existing_root = get_root()
    if existing_root:
        return True

    root = os.getenv('DDEV_ROOT', '')
    if root and os.path.isdir(root):
        set_root(root)
        return True
    return False


def initialize_root(config, agent=False, core=False, extras=False, here=False):
    """Initialize root directory based on config and options"""
    if check_root():
        return

    repo_choice = 'core' if core else 'extras' if extras else 'agent' if agent else config.get('repo', 'core')
    config['repo_choice'] = repo_choice
    config['repo_name'] = REPO_CHOICES[repo_choice]

    message = None
    root = os.path.expanduser(config.get(repo_choice, ''))
    if here or not dir_exists(root):
        if not here:
            repo = 'datadog-agent' if repo_choice == 'agent' else f'integrations-{repo_choice}'
            message = f'`{repo}` directory `{root}` does not exist, defaulting to the current location.'

        root = os.getcwd()

    set_root(root)
    return message


def complete_set_root(args):
    """Set the root directory within the context of a cli completion operation."""
    if check_root():
        return

    config = load_config()

    kwargs = {REPO_OPTIONS_MAP[arg]: True for arg in args if arg in REPO_OPTIONS_MAP}
    initialize_root(config, **kwargs)


def complete_testable_checks(ctx, args, incomplete):
    complete_set_root(args)
    return sorted(k for k in get_testable_checks() if k.startswith(incomplete))


def complete_valid_checks(ctx, args, incomplete):
    complete_set_root(args)
    return [k for k in get_valid_checks() if k.startswith(incomplete)]


def get_version_file(check_name):
    if check_name == 'datadog_checks_base':
        return os.path.join(get_root(), check_name, 'datadog_checks', 'base', '__about__.py')
    elif check_name == 'datadog_checks_dev':
        return os.path.join(get_root(), check_name, 'datadog_checks', 'dev', '__about__.py')
    elif check_name == 'datadog_checks_downloader':
        return os.path.join(get_root(), check_name, 'datadog_checks', 'downloader', '__about__.py')
    else:
        return os.path.join(get_root(), check_name, 'datadog_checks', check_name, '__about__.py')


def get_manifest_file(check_name):
    return os.path.join(get_root(), check_name, 'manifest.json')


def get_tox_file(check_name):
    return os.path.join(get_root(), check_name, 'tox.ini')


def get_metadata_file(check_name):
    return os.path.join(get_root(), check_name, 'metadata.csv')


def get_config_file(check_name):
    return os.path.join(get_data_directory(check_name), 'conf.yaml.example')


def get_config_spec(check_name):
    if check_name == 'agent':
        return os.path.join(get_root(), 'pkg', 'config', 'conf_spec.yaml')
    else:
        path = load_manifest(check_name).get('assets', {}).get('configuration', {}).get('spec', '')
        return os.path.join(get_root(), check_name, *path.split('/'))


def get_default_config_spec(check_name):
    return os.path.join(get_root(), check_name, 'assets', 'configuration', 'spec.yaml')


def get_assets_directory(check_name):
    return os.path.join(get_root(), check_name, 'assets')


def get_data_directory(check_name):
    if check_name == 'agent':
        return os.path.join(get_root(), 'pkg', 'config')
    else:
        return os.path.join(get_root(), check_name, 'datadog_checks', check_name, 'data')


def get_check_directory(check_name):
    return os.path.join(get_root(), check_name, 'datadog_checks', check_name)


def get_test_directory(check_name):
    return os.path.join(get_root(), check_name, 'tests')


def get_config_files(check_name):
    """TODO: Remove this function when all specs are finished"""
    if check_name == 'agent':
        return [os.path.join(get_root(), 'pkg', 'config', 'config_template.yaml')]

    files = []

    if check_name in NOT_CHECKS:
        return files

    root = get_root()

    auto_conf = os.path.join(root, check_name, 'datadog_checks', check_name, 'data', 'auto_conf.yaml')
    if file_exists(auto_conf):
        files.append(auto_conf)

    default_yaml = os.path.join(root, check_name, 'datadog_checks', check_name, 'data', 'conf.yaml.default')
    if file_exists(default_yaml):
        files.append(default_yaml)

    example_yaml = os.path.join(root, check_name, 'datadog_checks', check_name, 'data', 'conf.yaml.example')
    if file_exists(example_yaml):
        files.append(example_yaml)

    return sorted(files)


def get_valid_checks():
    return {path for path in os.listdir(get_root()) if file_exists(get_version_file(path))}


def get_valid_integrations():
    return {path for path in os.listdir(get_root()) if file_exists(get_manifest_file(path))}


def get_testable_checks():
    return {path for path in os.listdir(get_root()) if file_exists(get_tox_file(path))}


def get_metric_sources():
    return {path for path in os.listdir(get_root()) if file_exists(get_metadata_file(path))}


def read_metric_data_file(check_name):
    return read_file(os.path.join(get_root(), check_name, 'metadata.csv'))


def read_version_file(check_name):
    return read_file(get_version_file(check_name))


def get_version_string(check_name, tag_prefix='v'):
    """
    Get the version string for the given check.
    """
    # Check the version file of the integration if available
    # Otherwise, get the latest SemVer git tag for the project
    if check_name:
        version = VERSION.search(read_version_file(check_name))
        if version:
            return version.group(1)
    else:
        return get_latest_tag(tag_prefix=tag_prefix)


def load_manifest(check_name):
    """
    Load the manifest file into a dictionary
    """
    manifest_path = get_manifest_file(check_name)
    if file_exists(manifest_path):
        return json.loads(read_file(manifest_path).strip())
    return {}


def write_manifest(manifest, check_name):
    manifest_path = get_manifest_file(check_name)
    write_file(manifest_path, f'{json.dumps(manifest, indent=2)}\n')


def get_bump_function(changelog_types):
    minor_bump = False

    for changelog_type in changelog_types:
        bump_function = VERSION_BUMP.get(changelog_type)
        if bump_function is semver.bump_major:
            return bump_function
        elif bump_function is semver.bump_minor:
            minor_bump = True

    return semver.bump_minor if minor_bump else semver.bump_patch


def parse_agent_req_file(contents):
    """
    Returns a dictionary mapping {check-package-name --> pinned_version} from the
    given file contents. We can assume lines are in the form:

        datadog-active-directory==1.1.1; sys_platform == 'win32'

    """
    catalog = {}
    for line in contents.splitlines():
        toks = line.split('==', 1)
        if len(toks) != 2 or not toks[0] or not toks[1]:
            # if we get here, the requirements file is garbled but let's stay
            # resilient
            continue

        name, other = toks
        version = other.split(';')
        catalog[name] = version[0]

    return catalog


def parse_version_parts(version):
    if not isinstance(version, str):
        return []
    return [int(v) for v in version.split('.') if v.isdigit()]


def has_e2e(check):
    for path, _, files in os.walk(get_test_directory(check)):
        for fn in files:
            if fn.startswith('test_') and fn.endswith('.py'):
                with open(os.path.join(path, fn)) as test_file:
                    if 'pytest.mark.e2e' in test_file.read():
                        return True
    return False


def has_legacy_signature(check):
    for path, _, files in os.walk(get_check_directory(check)):
        for fn in files:
            if fn.endswith('.py'):
                with open(os.path.join(path, fn)) as test_file:
                    for line in test_file:
                        if "init" in line and "agentConfig" in line:
                            return True
    return False
