from django.test import TestCase
from .models import ValidationTests


class ValidationTestsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        ValidationTests.objects.create(
            category="Test Category",
            performance_metrics=["Metric 1", "Metric 2"],
            function_name="test_function",
        )

    def test_category_label(self):
        test = ValidationTests.objects.get(id=1)
        field_label = test._meta.get_field("category").verbose_name
        self.assertEquals(field_label, "category")

    def test_function_name_max_length(self):
        test = ValidationTests.objects.get(id=1)
        max_length = test._meta.get_field("function_name").max_length
        self.assertEquals(max_length, 128)

    def test_object_name_is_category(self):
        test = ValidationTests.objects.get(id=1)
        expected_object_name = f"{test.category}"
        self.assertEquals(expected_object_name, str(test))
