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
    assert config.find("test_value", action=(lambda val, parent: parent))[0] == config, "Find with action is invalid"


def test_config_find(config: CascadingConfig = None, vals: dict = None):
    vals = vals or {
        "test_value": "imported",
        "addon_value": "imported",
        "parent_value": "parent",
        "col.a[0].b": "source"
    }

    config = config or CascadingConfig.load(TEST_CONFIG_PATH)

    def check_expected(key, expected):
        result = config.find(key)
        result = None if len(result) == 0 else result[0]

        assert expected == result, f"Expected {key} is invalid when loading cascading config, {expected}!={result}"

    for key in vals.keys():
        check_expected(key, vals[key])


def test_config_max_depth():
    config = CascadingConfig.load(TEST_CONFIG_PATH, max_inherit_depth=1)
    test_config_find(config, {"test_value": "imported"})


def test_config_no_imports():
    config = CascadingConfig.load(TEST_CONFIG_PATH, load_imports=False)
    test_config_find(config, {"test_value": "source"})


def test_config_env():
    config = CascadingConfig.load(TEST_CONFIG_PATH, environment="test")
    test_config_find(
        config,
        {
            "list": [1, 2, 3, 4],
        },
    )
