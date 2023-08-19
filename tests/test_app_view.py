import pytest
from page_analyzer import app


class TestViews:
    def setup(self):
        app.testing = True
        self.client = app.test_client()

    def test_home(self):
        response = self.client.get('/')
        assert response.status_code == 200

    def teardown(self):
        pass
