from bole.config.cascading import CascadingConfig
from tests.consts import TEST_CONFIG_PATH


def test_config_load():
    CascadingConfig.load(TEST_CONFIG_PATH)


def test_config_helper_methods():
    config = CascadingConfig.load(TEST_CONFIG_PATH)
    config.to_dictionary()
    assert config.config_imports is not None
    assert config.environments is not None


def test_config_find_with_action():
    config = CascadingConfig.load(TEST_CONFIG_PATH)
    assert config.find("source_value", action=(lambda val, parent: parent))[0] == config, "Find with action is invalid"


def validate_config_values(config: CascadingConfig = None, vals: dict = None):
    vals = vals or {
        "test_value": "imported",
        "addon_value": "imported",
        "parent_value": "parent",
        "col.a[0].b": "source",
    }

    config = config or CascadingConfig.load(TEST_CONFIG_PATH)

    def check_expected(key, expected):
        result = config.find(key)
        result = None if len(result) == 0 else result[0]

        assert expected == result, f"Expected {key} is invalid when loading cascading config, {expected}!={result}"

    for key in vals.keys():
        check_expected(key, vals[key])


def test_source_value():
    validate_config_values(vals={"source_value": "source"})


def test_parent_inherit():
    validate_config_values(vals={"parent_value": "parent"})


def test_config_max_depth():
    config = CascadingConfig.load(TEST_CONFIG_PATH, max_inherit_depth=0)
    validate_config_values(config, {"parent_value": None})


def test_config_no_imports():
    config = CascadingConfig.load(TEST_CONFIG_PATH, load_imports=False)
    validate_config_values(config, {"override_in_single_import": "source"})


def test_import_single_file():
    validate_config_values(vals={"single_imported_value": "imported"})


def test_import_at_parent():
    validate_config_values(vals={"parent_import_value": "imported"})


def test_import_multi_file():
    validate_config_values(
        vals={
            "multi_imported_value_1": "imported",
            "multi_imported_value_2": "imported",
        }
    )


def test_override_inherit():
    validate_config_values(
        vals={
            "override_inherit": "source",
        }
    )


def test_override_single_import():
    validate_config_values(
        vals={
            "override_in_single_import": "imported",
        }
    )


def test_override_multi_import():
    validate_config_values(
        vals={
            "override_in_multi_import_1": "imported",
            "override_in_multi_import_2": "imported",
        }
    )


def test_override_environment_import():
    config = CascadingConfig.load(TEST_CONFIG_PATH, environment="test")
    validate_config_values(
        config=config,
        vals={
            "override_in_environment_import": "env-imported",
        },
    )


def test_config_env():
    config = CascadingConfig.load(TEST_CONFIG_PATH, environment="test")
    validate_config_values(
        config,
        {
            "list": [1, 2, 3, 4],
        },
    )
