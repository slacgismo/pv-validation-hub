from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import SystemMetadata


class SystemMetadataTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.systemmetadata = SystemMetadata.objects.create(
            name="System 1",
            azimuth=180.0,
            tilt=30.0,
            elevation=20.0,
            latitude=37.7749,
            longitude=-122.4194,
            tracking=True,
            dc_capacity=100.0,
        )

    def test_systemmetadata_list(self):
        response = self.client.get(reverse("systemmetadata-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_systemmetadata_detail(self):
        response = self.client.get(
            reverse("systemmetadata-detail", kwargs={"pk": self.systemmetadata.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "System 1")
