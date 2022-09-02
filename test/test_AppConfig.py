import unittest
from dataclasses import asdict

from streamdeck.config.AppConfig import AppConfig


class TestAppConfig(unittest.TestCase):

    def test_serialization(self):
        name = 'myapp'
        url = 'https://media.ccc.de'
        profile = '/tmp'
        hide_address_bar = True
        app = AppConfig(name=name, url=url, firefox_profile=profile, hide_address_bar=hide_address_bar)
        restored = AppConfig.load(asdict(app))
        self.assertEqual(app, restored)
        self.assertEqual((name, url, profile, hide_address_bar),
                         (restored.name, restored.url, restored.firefox_profile, restored.hide_address_bar))

    def test_launch_args(self):
        name = 'myapp'
        url = 'https://media.ccc.de'
        profile = '/tmp'
        hide_address_bar = True

        app = AppConfig(name=name, url=url, firefox_profile=profile, hide_address_bar=hide_address_bar)

        self.assertIn(f'--profile|{profile}', "|".join(app.launch_args))
        self.assertIn(url, app.launch_args)
