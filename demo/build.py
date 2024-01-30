#!/usr/bin/env python
"""
This file simulates the tooling that would enable this to be used
"""
import json
import os
import sys

# This should be read from a pyproject.toml instead
dependencies = ["dep_a", "dep_b"]

os.mkdir('py_modules')

import_map = {}
# Install dependencies into isolated environments
for i, dep in enumerate(dependencies):
    dir_ = f"py_modules/venv{i}"
    site_pkgs = f'{dir_}/lib/python3.{sys.version_info.minor}/site-packages'

    os.mkdir(dir_)
    os.system(f'python3 -m venv {dir_}')
    os.system(f'{dir_}/bin/pip install ./src/{dep}')
    # This should be done by properly configuring the pyproject so that the pip
    # install above takes care of this
    os.system(f'cp -rv src/{dep} {site_pkgs}')

    import_map[dep] = os.path.realpath(site_pkgs)

with open('import_map.json', 'w') as f:
    json.dump(import_map, f)


os.mkdir('app')
os.system('python3 -m venv app')
# Copy the app into the venv - this should be done via pip instead, but without
# installing dependencies?
app_site_packages = f'app/lib/python3.{sys.version_info.minor}/site-packages'
os.system(f'cp -rv src/my_app {app_site_packages}/')
os.system(f'cp -rv ../importshim {app_site_packages}/')
os.system(f'mv -v import_map.json {app_site_packages}/importshim/')
