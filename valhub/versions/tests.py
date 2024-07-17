from django.test import TestCase
from .models import Versions


class VersionsModelTest(TestCase):
    def setUp(self):
        self.versions = Versions.objects.create(
            python_versions={"3.9", "3.10", "3.11", "3.12"},
            old_python_versions={"3.8", "3.7"},
            cur_worker_version=1.0,
            old_worker_versions={"0.9", "0.8"},
        )

    def test_versions_creation(self):
        self.assertTrue(isinstance(self.versions, Versions))
        self.assertEqual(self.versions.cur_worker_version, 1.0)
