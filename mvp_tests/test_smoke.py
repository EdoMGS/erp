def test_smoke_imports():
    import importlib

    assert importlib.import_module("project_root.settings.base")
