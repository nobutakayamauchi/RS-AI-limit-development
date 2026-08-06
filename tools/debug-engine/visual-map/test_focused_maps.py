import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
SPEC = importlib.util.spec_from_file_location("focused_maps", ROOT / "focused_maps.py")
focused_maps = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(focused_maps)


class FocusedMapTests(unittest.TestCase):
    def sample(self):
        return {
            "title": "dense map",
            "screens": [
                {"id": "top", "label": "Top"},
                {"id": "a", "label": "A"},
                {"id": "b", "label": "B"},
                {"id": "c", "label": "C"},
            ],
            "actions": [
                {"id": "to-a", "source": "top", "label": "Aへ", "expected_target": "a", "observed_target": "a", "status": "confirmed"},
                {"id": "to-b", "source": "top", "label": "Bへ", "expected_target": "b", "observed_target": "b", "status": "confirmed"},
                {"id": "to-c", "source": "top", "label": "Cへ", "expected_target": "c", "observed_target": "c", "status": "confirmed"},
            ],
        }

    def test_split_when_one_screen_has_many_outgoing_actions(self):
        split, reasons = focused_maps.should_split(self.sample(), action_threshold=99, outgoing_threshold=3, crossing_threshold=99)
        self.assertTrue(split)
        self.assertTrue(any("最大接続数" in reason for reason in reasons))

    def test_focused_manifest_keeps_only_one_source(self):
        result = focused_maps._focused_manifest(self.sample(), "top")
        self.assertEqual({action["source"] for action in result["actions"]}, {"top"})
        self.assertEqual({screen["id"] for screen in result["screens"]}, {"top", "a", "b", "c"})

    def test_generate_writes_overview_index_and_per_screen_page(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "map.json"
            output = root / "maps"
            manifest.write_text(json.dumps(self.sample(), ensure_ascii=False), encoding="utf-8")
            result = focused_maps.generate(manifest, output, outgoing_threshold=3)
            self.assertTrue(result["split"])
            self.assertTrue((output / "index.html").exists())
            self.assertTrue((output / "navigation-map-overview.html").exists())
            self.assertTrue((output / "navigation-map-top.html").exists())
            page = (output / "navigation-map-top.html").read_text(encoding="utf-8")
            self.assertIn("Top の接続", page)
            self.assertNotIn("source: a", page)


if __name__ == "__main__":
    unittest.main()
