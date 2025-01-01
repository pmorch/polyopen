import unittest

from polyopen import valid_url


class TestSum(unittest.TestCase):

    def test_http(self):
        self.assertTrue(valid_url.is_valid_url("http://www.google.com"))

    def test_https(self):
        self.assertTrue(valid_url.is_valid_url("https://www.google.com"))

    def test_ftp(self):
        self.assertTrue(valid_url.is_valid_url("ftp://www.google.com"))

    def test_ws(self):
        self.assertFalse(valid_url.is_valid_url("ws://www.google.com"))

    def test_non_urls(self):
        for url in [
            "hello world",
            "/hello",
            "//hello",
            "../hello",
            "//hello/world",
            "",
            None,
        ]:
            self.assertFalse(valid_url.is_valid_url(url))


if __name__ == "__main__":
    unittest.main()
