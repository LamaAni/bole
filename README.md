# bole
Cascading configuration manager and logger for python (yaml, json)

###### Why bole?
Bole = "trunk of a tree" = "log" :)

# BETA

Bole is a python configuration manager that has,
1. Loads configurations from `yaml, json`
2. Allows inheritance - child folder can load config from parent folder.
3. Allows imports - allows specifying config loading paths (and globs)
4. Has an easy to use cli.

# Install

Just install the pip [package](https://pypi.org/project/bole/),

```shell
pip install bole
```

# Configuration

## Example

```yaml
settings:
    inherit: True # If true, allow inherit parent folders.
environments:
    test:
        my_value: 22
    dev: 
        my_value: 42

my_value: 0
some_col:
    a: 
    - b: 0
```

To view this configuration just run (in the config folder),
```shell
bole config view
```

To get the result of `my_value`, run,
```shell
bole config get my_value # or
bole config get some_col.a[0].b
```

## Built in keywords and structures.

The following keywords are reserved (default values presented)

```yaml
settings:
    inherit: False # If true, allow inherit parent folders.
    inherit_siblings: True # If true allow inherit configuration files in the same source directory.
    use_deep_merge: True # Merge configurations via deep merge. If false, Only root keys are merged (and overwritten)
    concatenate_lists: True # When merging, append the merged list to the current one.
imports:
    - "**/*.config.yaml" # Recursively import all .config.yaml
    - path: my-config.yaml
      required: False # this item is not required.
      recursive: null # Applies if glob. Import recursively.
environments:
    [env name]:{ config overrides (any) }

```

## Example configuration

Example configuration with inheritance can be found in [tests](tests/test_files/root).

# Contribution

Feel free to ping me in issues or directly on LinkedIn to contribute.

# Future implementation

We plan to support multiple python version per environment.

Looking for help on this subject.

# Licence

Copyright ©
`Zav Shotan`, `Patrick Huber`, and other [contributors](graphs/contributors).
It is free software, released under the MIT licence, and may be redistributed under the terms specified in `LICENSE`.
