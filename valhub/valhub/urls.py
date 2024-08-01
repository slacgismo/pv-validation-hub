"""valhub URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.conf import settings

PATH = settings.STATIC_URL
ROOT = settings.STATIC_ROOT

urlpatterns = [
    path("analysis/", include("analyses.urls")),
    path("submissions/", include("submissions.urls")),
    path("", include("accounts.urls")),
    path("admin/", admin.site.urls),
    path("file_metadata/", include("file_metadata.urls")),
    path("system_metadata/", include("system_metadata.urls")),
    path("validation_tests/", include("validation_tests.urls")),
    path("healthy/", include("healthcheck.urls")),
    path("error/", include("error_report.urls")),
    path("versions/", include("versions.urls")),
] + static(PATH, document_root=ROOT)
