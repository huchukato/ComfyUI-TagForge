import importlib.util
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path


class TagDataManagerPathTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.tags_dir = self.root / "tags"
        self.translate_dir = self.root / "translate"
        self.tags_dir.mkdir()
        self.translate_dir.mkdir()
        (self.root / "category_map.csv").write_text("category,description,site\n", encoding="utf-8")

        folder_paths = types.ModuleType("folder_paths")
        folder_paths.get_filename_list = lambda _: []
        sys.modules["folder_paths"] = folder_paths

        package = types.ModuleType("tagforge_py")
        package.__path__ = []
        sys.modules["tagforge_py"] = package

        paths = types.ModuleType("tagforge_py.paths")
        paths.root_dir = self.root
        paths.tags_dir = self.tags_dir
        paths.translate_dir = self.translate_dir
        sys.modules["tagforge_py.paths"] = paths

        wildcards = types.ModuleType("tagforge_py.wildcards")
        wildcards.WildcardLoader = type("WildcardLoader", (), {})
        sys.modules["tagforge_py.wildcards"] = wildcards

        source = Path(__file__).parents[1] / "py" / "tagdata_manager.py"
        spec = importlib.util.spec_from_file_location("tagforge_py.tagdata_manager", source)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        self.manager = module.TagDataManager

    def tearDown(self):
        self.manager.close()
        self.temp.cleanup()

    def test_accepts_file_inside_data_directory(self):
        csv_file = self.tags_dir / "valid.csv"
        csv_file.write_text("tag,0,1,\n", encoding="utf-8")
        self.assertEqual(self.manager.resolve_data_path(self.tags_dir, "valid.csv"), os.path.realpath(csv_file))

    def test_accepts_none_selection(self):
        self.assertIsNone(self.manager.resolve_data_path(self.tags_dir, "None"))

    def test_rejects_missing_and_non_string_filename(self):
        for filename in (None, "", 123):
            with self.subTest(filename=filename), self.assertRaises(ValueError):
                self.manager.resolve_data_path(self.tags_dir, filename)

    def test_rejects_absolute_path(self):
        with self.assertRaises(ValueError):
            self.manager.resolve_data_path(self.tags_dir, str(self.root / "outside.csv"))

    def test_rejects_parent_traversal(self):
        with self.assertRaises(ValueError):
            self.manager.resolve_data_path(self.tags_dir, "../outside.csv")

    def test_rejects_symlink_outside_data_directory(self):
        outside = self.root / "outside.csv"
        outside.write_text("secret", encoding="utf-8")
        link = self.tags_dir / "link.csv"
        link.symlink_to(outside)
        with self.assertRaises(ValueError):
            self.manager.resolve_data_path(self.tags_dir, link.name)


if __name__ == "__main__":
    unittest.main()
