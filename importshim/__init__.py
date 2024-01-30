"""
Goal: Suppose we have the following dep tree
    foo depends on [bar, baz]
    bar depends on [qux@v1]
    baz depends on [qux@v2]
we want to be able to have multiple versions of qux installed/importable.

we need to have a venv per library:
    .venvs/bar/...
    .venvs/baz/...

and translate import calls like so:
    import bar
    import baz

    # becomes

    with _env('...venvs/bar'):
        import bar
    with _env('...venvs/baz'):
        import baz


Resolving library references for tooling is a non-goal (e.g. knowing that
`import cv` requires opencv, etc)
"""

import builtins
import json
import sys
import traceback

from contextlib import contextmanager
from importlib.abc import MetaPathFinder
from pathlib import Path
from typing import Optional, List

orig_sys_modules = sys.modules.copy()
per_venv_module_cache = {}

def update_env(new_env):
    """C-Extensions break if sys.module's reference changes, so we must update
    the existing dictionary instead of just replacing it"""
    sys.modules.update(new_env)
    mods_to_delete = [m for m in sys.modules if m not in new_env]
    for m in mods_to_delete:
        del sys.modules[m]

current_venv = None

def switch_modules_to_env(venv):
    global current_venv
    venv = str(venv) if venv is not None else None
    if str(venv) == str(current_venv):
        return
    if current_venv is not None:
        per_venv_module_cache[current_venv] = sys.modules.copy()
    if venv is None:
        new_env = orig_sys_modules
    else:
        if venv not in per_venv_module_cache:
            per_venv_module_cache[venv] = orig_sys_modules.copy()
        new_env = per_venv_module_cache[venv]
    update_env(new_env)
    current_venv = venv


force_env = False

@contextmanager
def _env(env_path):
    global force_env

    sys.path = [env_path] + sys.path
    switch_modules_to_env(env_path)
    orig_force_env = force_env
    force_env = True
    try:
        yield
    finally:
        force_env = orig_force_env
        sys.path = sys.path[1:]
        if env_path in sys.path_importer_cache:
            del sys.path_importer_cache[env_path]

# This method will be used to determine if an import from a library should be
# wrapped with a `_env` or not.
known_venvs: List[Path] = []


def is_in_venv(p: Path) -> Optional[Path]:
    parents = p.parents
    for venv in known_venvs:
        if venv in parents:
            return venv

    parts = p.parts
    try:
        index = list(parts).index('site-packages')
    except ValueError:
        return None

    if index > 2:
        possible_venv_dir = Path(*p.parts[:index - 2])
        possible_site_packages = Path(*p.parts[:index + 1])
        if (possible_venv_dir / "pyvenv.cfg").exists():
            known_venvs.append(possible_site_packages)
            return possible_site_packages
    return None


def in_venv_context():
    stack = traceback.extract_stack()
    parent_venv = None
    for s in stack[::-1]:
        if s.filename == __file__:
            continue
        if not s.filename.startswith('/'):
            continue
        if (venv := is_in_venv(Path(s.filename))):
            parent_venv = venv
            break
    return parent_venv

config_path = Path(__file__).parent / 'import_map.json'
with config_path.open() as f:
    config = json.load(f)

orig_import = builtins.__import__

def __import__(name: str, globals=None, locals=None, fromlist=(), level=0):
    def import_wrapper():
        if not force_env:
            if venv := in_venv_context():
                switch_modules_to_env(venv)
            else:
                switch_modules_to_env(None)
        return orig_import(name, globals, locals, fromlist, level)

    if name in config:
        with _env(config[name]):
            return import_wrapper()
    return import_wrapper()

builtins.__import__ = __import__


class PathFinder(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        # Only if we're importing library code that was imported from a venv do
        # we want to have a custom import process
        if not force_env and (parent_venv := in_venv_context()):
            with _env(str(parent_venv)):
                for finder in sys.meta_path[1:]:
                    if (module := finder.find_spec(fullname, path, target)):
                        return module
        return None

    def invalidate_caches(self):
        pass


finder = PathFinder()
sys.meta_path = [finder] + sys.meta_path
