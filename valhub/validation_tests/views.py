from django.views.generic import ListView, DetailView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import ValidationTests
from .serializers import ValidationTestsSerializer


class ValidationTestsListView(ListView):
    model = ValidationTests
    template_name = 'validation_tests_list.html'


class ValidationTestsDetailView(DetailView):
    model = ValidationTests
    template_name = 'validation_tests_detail.html'


class ValidationTestsListAPIView(ListAPIView):
    queryset = ValidationTests.objects.all()
    serializer_class = ValidationTestsSerializer


class ValidationTestsDetailAPIView(RetrieveAPIView):
    queryset = ValidationTests.objects.all()
    serializer_class = ValidationTestsSerializer
