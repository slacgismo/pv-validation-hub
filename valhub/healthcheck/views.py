from django.http import HttpResponse

def healthcheck(request):
    return HttpResponse("The API is healthy")
