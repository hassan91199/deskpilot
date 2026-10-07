import unittest
from unittest.mock import patch

from deskpilot.api import cors_allow_origins

LOCAL_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]


class CorsAllowOriginsTests(unittest.TestCase):
    @patch.dict("os.environ", {}, clear=True)
    def test_only_dev_server_origins_when_unset(self):
        self.assertEqual(cors_allow_origins(), LOCAL_ORIGINS)

    @patch.dict("os.environ", {"FRONTEND_ORIGIN": "https://deskpilot.hassanabbas.net"}, clear=True)
    def test_appends_frontend_origin_when_set(self):
        self.assertEqual(
            cors_allow_origins(), [*LOCAL_ORIGINS, "https://deskpilot.hassanabbas.net"]
        )


if __name__ == "__main__":
    unittest.main()
