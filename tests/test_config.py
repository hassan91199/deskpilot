import unittest
from unittest.mock import patch

from deskpilot.config import database_url


class DatabaseUrlTests(unittest.TestCase):
    @patch.dict("os.environ", {"DATABASE_URL": "postgresql://x/y"}, clear=True)
    def test_reads_from_environment(self):
        self.assertEqual(database_url(), "postgresql://x/y")


if __name__ == "__main__":
    unittest.main()
