import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path


class WildcardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        folder_paths = types.ModuleType("folder_paths")
        folder_paths.get_folder_paths = lambda _: []
        sys.modules["folder_paths"] = folder_paths
        package = types.ModuleType("tagforge_py")
        package.__path__ = []
        sys.modules["tagforge_py"] = package
        paths = types.ModuleType("tagforge_py.paths")
        paths.wildcards_dir = self.root
        paths.custom_nodes_dir = self.root / "custom_nodes" / "ComfyUI-TagForge"
        sys.modules["tagforge_py.paths"] = paths
        source = Path(__file__).parents[1] / "py" / "wildcards.py"
        spec = importlib.util.spec_from_file_location("tagforge_py.wildcards", source)
        self.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = self.module
        spec.loader.exec_module(self.module)
        self.loader = self.module.WildcardLoader

    def tearDown(self):
        self.loader.unload()
        self.temp.cleanup()

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_seeded_nested_weighted_and_depth_agnostic(self):
        self.write("animals/pet.txt", "2::cat\n1::dog\n")
        self.write("scene.txt", "a __pet__\n")
        self.loader.load(force=True)
        first = self.loader.process("{bright|dark} __scene__", 42)
        second = self.loader.process("{bright|dark} __scene__", 42)
        self.assertEqual(first, second)
        self.assertNotIn("__", first)
        self.assertTrue(any(animal in first for animal in ("cat", "dog")))

    def test_yaml_glob_comments_and_quantifier(self):
        self.write("colors.yaml", "palette:\n  warm: [red, orange]\n")
        self.write("things/one.txt", "# ignored\nalpha\n\n")
        self.write("things/two.txt", "beta\n")
        self.loader.load(force=True)
        self.assertEqual(self.loader.get_wildcard_value("palette/warm"), ["red", "orange"])
        self.assertEqual(set(self.loader.get_wildcard_value("things/*")), {"alpha", "beta"})
        self.assertEqual(len(self.loader.process("# heading\n2#__palette/warm__", 7).split()), 2)

    def test_multiselect_variants(self):
        self.write("letters.txt", "a\nb\nc\nd\n")
        self.loader.load(force=True)
        fixed = self.loader.process("{2$$, $$a|b|c|d}", 1)
        from_wildcard = self.loader.process("{2$$/$$__letters__}", 1)
        open_range = self.loader.process("{-3$$, $$a|b|c|d}", 1)
        self.assertEqual(len(fixed.split(", ")), 2)
        self.assertEqual(len(from_wildcard.split("/")), 2)
        self.assertLessEqual(len(open_range.split(", ")), 3)

    def test_comments_preserve_line_boundaries_and_non_finite_weight_is_text(self):
        self.write("values.txt", "nan::value\n")
        self.loader.load(force=True)
        self.assertEqual(self.loader.process("first\r\n# comment\r\nsecond", 1), "first\nsecond")
        self.assertEqual(self.loader.process("__values__", 1), "nan::value")

    def test_downvote_records_usage(self):
        self.write("choice.txt", "a\nb\n")
        self.loader.load(force=True)
        usage = {}
        self.loader.process("__choice__", 3, usage, 0.5)
        self.assertEqual(sum(usage["choice"].values()), 1)
        self.assertEqual(self.loader.process("__choice__", 3), self.loader.process("__choice__", 3))

    def test_on_demand_status(self):
        self.write("lazy.txt", "value\n")
        self.loader.CACHE_LIMIT_BYTES = 1
        self.loader.load(force=True)
        self.assertEqual(self.loader.get_status(), {"on_demand_mode": True, "total_available": 1, "loaded_count": 0})
        self.assertEqual(self.loader.process("__lazy__", 1), "value")
        self.assertEqual(self.loader.get_status()["loaded_count"], 1)

    def test_model_presets_replace_existing_prefix_and_return_negative(self):
        comfy = types.ModuleType("comfy")
        comfy_types = types.ModuleType("comfy.comfy_types")
        comfy_types.IO = types.SimpleNamespace(STRING="STRING", INT="INT", BOOLEAN="BOOLEAN", FLOAT="FLOAT")
        comfy_types.InputTypeDict = dict
        sys.modules["comfy"] = comfy
        sys.modules["comfy.comfy_types"] = comfy_types
        source = Path(__file__).parents[1] / "py" / "wildcard_processor.py"
        spec = importlib.util.spec_from_file_location("tagforge_py.wildcard_processor", source)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        pony_prefix = module.WildcardProcessorNode.MODEL_PRESETS["Pony"]["positive"]
        positive, negative = module.WildcardProcessorNode.apply_model_preset(f"{pony_prefix}, 1girl", "Illustrious")
        self.assertEqual(positive, f'{module.WildcardProcessorNode.MODEL_PRESETS["Illustrious"]["positive"]}, 1girl')
        self.assertEqual(negative, module.WildcardProcessorNode.MODEL_PRESETS["Illustrious"]["negative"])
        self.assertEqual(module.WildcardProcessorNode.RETURN_NAMES, ("processed_text", "negative"))
        self.assertIn("base_model", module.WildcardProcessorNode.INPUT_TYPES()["optional"])


if __name__ == "__main__":
    unittest.main()
