# multiversionpython
The goal of this project is to enable having conflicting dependencies in python
by allowing multiple versions of the same library to be concurrently installed.
This is achieved by isolating every dependancy into it's own venv, and hooking
every `import` call to redirect them to importing within the appropriate env.

The source code for intercepting imports and redirecting them to appropriate
venvs is in `importshim/`. A demo that shows how a real project might use this
is in `demo/`.

This project is currently a proof of concept. With some work, maybe it could be
integrated into existing python tools and made more stable.

A more detailed explanation of what is happening is below:

+ tooling generates venvs + additional runtime importing facilities
  + each venv contains one dependency and it's sub-deps in isolation
  + importer will allow application to import libraries from each dependent venv
    and will resolve imports from library code to the appropriate venv

The eventual directory structure for a project might look like:
```
.
├── SOURCE_FILES...
├── pyproject.toml
├── app
│   ├── bin
│   │   └── ...
│   ├── include
│   │   └── ...
│   ├── lib
│   │   └── python3.10
│   │       └── site-packages
│   │           └── _importer.py
│   └── pyvenv.cfg
└── py_modules
    ├── pandas
    │   ├── ...
    │   ├── lib
    │   │   └── python3.10
    │   │       └── site-packages
    │   │           └── ...
    │   └── pyvenv.cfg
    └── numpy
        ├── ...
        ├── lib
        │   └── python3.10
        │       └── site-packages
        │           └── ...
        └── pyvenv.cfg
```

here `py_modules` contains the isolated environments for each "top-level"
dependancy identified by `pyproject.toml`, `app` is the venv for the project,
containing only the generated import machinery, and `SOURCE_FILES` is the actual
project source code.

