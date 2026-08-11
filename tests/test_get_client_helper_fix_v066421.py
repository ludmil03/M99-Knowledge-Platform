import os
import unittest
from unittest.mock import patch, Mock

from integrations.channel_publish.mela99_controlled import (
    ControlledMela99Publisher,
    Mela99ClientConfig,
    ControlledChannelHttpError,
)


class GetClientHelperFixV066421Tests(unittest.TestCase):
    def setUp(self):
        os.environ["M99_TEST_API_KEY"] = "TEST_ONLY"
        self.client = ControlledMela99Publisher(
            Mela99ClientConfig(
                base_url="https://example.invalid",
                api_key_env="M99_TEST_API_KEY",
                timeout_seconds=5,
            )
        )

    def tearDown(self):
        os.environ.pop("M99_TEST_API_KEY", None)

    @patch("integrations.channel_publish.mela99_controlled.requests.get")
    def test_get_resource_xml_uses_shared_response_helper(self, get):
        response = Mock()
        response.ok = True
        response.text = "<prestashop><languages/></prestashop>"
        response.url = "https://example.invalid/api/languages?display=full"
        get.return_value = response

        xml = self.client.get_resource_xml("languages", {"display": "full"})
        self.assertIn("<languages", xml)

    @patch("integrations.channel_publish.mela99_controlled.requests.get")
    def test_get_resource_xml_returns_safe_http_diagnostic(self, get):
        response = Mock()
        response.ok = False
        response.status_code = 403
        response.text = "<error>Forbidden</error>"
        response.url = "https://example.invalid/api/languages?display=full&secret=x"
        get.return_value = response

        with self.assertRaises(ControlledChannelHttpError) as ctx:
            self.client.get_resource_xml("languages", {"display": "full"})

        self.assertEqual(ctx.exception.status_code, 403)
        self.assertNotIn("secret=x", ctx.exception.url)

    @patch("integrations.channel_publish.mela99_controlled.requests.get")
    def test_product_get_uses_same_helper(self, get):
        response = Mock()
        response.ok = True
        response.text = "<prestashop><product><id>2076</id></product></prestashop>"
        response.url = "https://example.invalid/api/products/2076"
        get.return_value = response
        self.assertIn("<id>2076</id>", self.client.get_product_xml("2076"))

    def test_backward_compatible_check_alias_exists(self):
        self.assertTrue(callable(getattr(self.client, "_check")))
        self.assertTrue(callable(getattr(self.client, "_raise_for_response")))


if __name__ == "__main__":
    unittest.main()
