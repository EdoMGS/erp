import importlib


def test_import_settings():
    assert importlib.import_module('project_root.settings.base')
