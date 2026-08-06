import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("visual_map.py")
SPEC = importlib.util.spec_from_file_location("visual_map", MODULE_PATH)
visual_map = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(visual_map)


class VisualMapTests(unittest.TestCase):
    def sample(self):
        return {
            "title": "test map",
            "screens": [
                {"id": "a", "label": "A", "x": 0, "y": 0},
                {"id": "b", "label": "B", "x": 400, "y": 0},
                {"id": "wrong", "label": "Wrong", "x": 400, "y": 400},
            ],
            "actions": [
                {
                    "id": "go",
                    "source": "a",
                    "label": "Go",
                    "expected_target": "b",
                    "observed_target": "wrong",
                    "status": "mismatch",
                }
            ],
        }

    def test_validate_accepts_valid_manifest(self):
        visual_map._validate(self.sample())

    def test_validate_rejects_unknown_target(self):
        data = self.sample()
        data["actions"][0]["observed_target"] = "missing"
        with self.assertRaisesRegex(ValueError, "unknown observed_target"):
            visual_map._validate(data)

    def test_render_contains_expected_and_observed_destinations(self):
        data = self.sample()
        visual_map._validate(data)
        rendered = visual_map._render(data, Path("map.json"))
        self.assertIn("期待接続先", rendered)
        self.assertIn("observed_target", rendered)
        self.assertIn("edge-mismatch", rendered)
        self.assertIn("Wrong", rendered)

    def test_main_writes_standalone_html(self):
        data = self.sample()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "map.json"
            output = root / "map.html"
            manifest.write_text(json.dumps(data), encoding="utf-8")
            loaded = visual_map._load_manifest(manifest)
            visual_map._validate(loaded)
            output.write_text(visual_map._render(loaded, manifest), encoding="utf-8")
            self.assertTrue(output.exists())
            self.assertIn("<!doctype html>", output.read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main()
