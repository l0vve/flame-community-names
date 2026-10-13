import unittest
from publish import parse_feed, healthy


class FeedTests(unittest.TestCase):
    def test_complete_unicode_feed_and_empty_list(self):
        self.assertEqual(parse_feed("FLAME_NAMES_V1\n7\n- Mohanad -\ntcc-\nمهند\n"), (7, 3))
        self.assertEqual(parse_feed("FLAME_NAMES_V1\n8\n"), (8, 0))

    def test_rejects_partial_markup_separator_controls_and_duplicates(self):
        for text in ("FLAME_NAMES_V1\n7\nname", "FLAME_NAMES_V1\n7\n<b>name</b>\n", "FLAME_NAMES_V1\n7\na||b\n", "FLAME_NAMES_V1\n7\na\u200bb\n", "FLAME_NAMES_V1\n7\nAlice\nalice\n", "FLAME_NAMES_V1\nNaN\nname\n"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_feed(text)

    def test_requires_fresh_complete_healthy_source(self):
        status = dict(ready=True, sourceError=None, syncingHistory=False, messageContentEnabled=True, commandsRegistered=True, ownerConfigured=True, lastChecked=100)
        self.assertTrue(healthy(status, 100))
        self.assertFalse(healthy(status, 101))
        self.assertFalse(healthy({**status, "sourceError": "upstream failure"}, 100))
        self.assertFalse(healthy({**status, "syncingHistory": True}, 100))


if __name__ == "__main__":
    unittest.main()
