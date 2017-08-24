# Documentation build instructions

The autodoc extension doesn't regenerate the `dcae_cli` package files in the build directory. They can be recreated via:

```
sphinx-apidoc -o source/apidoc/ ../dcae_cli/
```

Then the HTML can be rebuilt via:

```
make clean
make html
```

The makefile was initially created via:

```
sphinx-quickstart
```
