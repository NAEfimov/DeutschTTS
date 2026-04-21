import unittest

from deutschtts.text import chunk_sentences, normalize_text, sentence_split


class TestTextProcessing(unittest.TestCase):
    def test_normalize_text_expands_abbrev_and_numbers(self) -> None:
        actual = normalize_text("Dr. Müller hat 12 Katzen, z.B. in Berlin.")
        self.assertIn("Doktor", actual)
        self.assertIn("eins zwei", actual)
        self.assertIn("zum Beispiel", actual)

    def test_sentence_split(self) -> None:
        chunks = sentence_split("Hallo Welt. Wie geht es dir? Gut!")
        self.assertEqual(chunks, ["Hallo Welt.", "Wie geht es dir?", "Gut!"])

    def test_chunk_sentences(self) -> None:
        sentences = ["eins zwei drei", "vier fünf sechs", "sieben acht neun"]
        max_chars = 20
        chunks = chunk_sentences(sentences, max_chars=max_chars)
        self.assertEqual(len(chunks), 3)
        self.assertTrue(all(len(chunk) <= max_chars for chunk in chunks))
        self.assertEqual(" ".join(chunks), " ".join(sentences))

    def test_chunk_sentences_force_splits_long_word(self) -> None:
        long_word = "a" * 25
        chunks = chunk_sentences([long_word], max_chars=10)
        self.assertEqual(chunks, ["a" * 10, "a" * 10, "a" * 5])
        self.assertTrue(all(len(chunk) <= 10 for chunk in chunks))


if __name__ == "__main__":
    unittest.main()
