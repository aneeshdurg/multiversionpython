This example shows how multiversioned imports might be used. In this example,
`my_app` depends on `dep_a` and `dep_b`, and while `dep_a` depends on
`pandas==2.2.0`, `dep_b` depends on `pandas==2.0.3`. Currently, there's a lot of
manual steps in `build.py`, but one could imagine integrating this with `pip` or
`rye` and automatically generating the import map.
