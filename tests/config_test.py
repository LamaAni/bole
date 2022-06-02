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


def test_import_single_file():
    validate_config_values(vals={"single_imported_value": "imported"})


def test_import_multi_file():
    validate_config_values(
        vals={
            "multi_imported_value_1": "imported",
            "multi_imported_value_2": "imported",
        }
    )


# def test_config_max_depth():
#     config = CascadingConfig.load(TEST_CONFIG_PATH, max_inherit_depth=1)
#     validate_config_values(config, {"test_value": "imported"})


# def test_config_no_imports():
#     config = CascadingConfig.load(TEST_CONFIG_PATH, load_imports=False)
#     validate_config_values(config, {"test_value": "source"})


# def test_config_env():
#     config = CascadingConfig.load(TEST_CONFIG_PATH, environment="test")
#     validate_config_values(
#         config,
#         {
#             "list": [1, 2, 3, 4],
#         },
#     )
