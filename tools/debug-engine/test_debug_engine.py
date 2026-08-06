import unittest

from debug_engine import build_release_gate, classify_report


class DebugEngineTests(unittest.TestCase):
    def test_destructive_recovery_report(self) -> None:
        result = classify_report("壊れないか確認するため、処理中に別画面へ移動して戻った")
        self.assertIn("DESTRUCTIVE_TEST", result.tags)
        self.assertIn("RECOVERY_TEST", result.tags)
        self.assertIn("離脱・復帰後も状態を保持すること", result.purposes)

    def test_accidental_data_loss_report(self) -> None:
        result = classify_report("間違えて戻ったら編集内容が消えて復元できない")
        self.assertIn("ACCIDENTAL_MISUSE", result.tags)
        self.assertIn("DATA_LOSS_RISK", result.tags)
        self.assertIn("編集内容・保存データを失わないこと", result.purposes)

    def test_plain_report_defaults_to_normal(self) -> None:
        result = classify_report("動画を追加して書き出した")
        self.assertEqual(["NORMAL_FLOW"], result.tags)

    def test_release_gate_blocks_until_executed(self) -> None:
        gate = build_release_gate("sample")
        self.assertEqual("BLOCK_UNTIL_EXECUTED", gate["decision"])
        self.assertGreaterEqual(len(gate["human_test_program"]), 3)


if __name__ == "__main__":
    unittest.main()
