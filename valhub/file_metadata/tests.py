from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from systemmetadata.models import SystemMetadata
from .models import FileMetadata

class FileMetadataTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.systemmetadata = SystemMetadata.objects.create(
            name='System 1',
            azimuth=180.0,
            tilt=30.0,
            elevation=20.0,
            latitude=37.7749,
            longitude=-122.4194,
            tracking=True,
            dc_capacity=100.0
        )
        self.filemetadata = FileMetadata.objects.create(
            system_id=self.systemmetadata,
            file_name='File 1',
            time_zone='UTC',
            sampling_freq_minute=5,
            issue='Issue 1',
            subissue='Subissue 1'
        )

    def test_filemetadata_list(self):
        response = self.client.get(reverse('filemetadata-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filemetadata_detail(self):
        response = self.client.get(reverse('filemetadata-detail', kwargs={'pk': self.filemetadata.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['file_name'], 'File 1')
