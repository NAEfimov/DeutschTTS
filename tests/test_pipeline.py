import json
from pathlib import Path
import tempfile
import unittest

from deutschtts.config import TTSConfig
from deutschtts.pipeline import TTSPipeline


class TestPipeline(unittest.TestCase):
    def test_synthesize_to_file_creates_wav_and_metadata(self) -> None:
        cfg = TTSConfig(model_name="dummy-sine")
        pipeline = TTSPipeline(config=cfg)
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "sample.wav"
            path = pipeline.synthesize_to_file("Hallo Welt. Das ist ein Test.", output)
            self.assertTrue(path.exists())
            self.assertGreater(path.stat().st_size, 44)

            metadata_path = output.with_suffix(".json")
            self.assertTrue(metadata_path.exists())
            data = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(data["model"], "dummy-sine")
            self.assertGreaterEqual(data["chunk_count"], 1)


if __name__ == "__main__":
    unittest.main()
