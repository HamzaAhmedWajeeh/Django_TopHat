# from django.http import HttpResponse
# from django.contrib.auth import authenticate
# from django.conf import settings

# from core.models import User

# class SwaggerAuthMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         if request.path.startswith('/api/docs/'):
#             # Check for Basic Authentication
#             if 'HTTP_AUTHORIZATION' in request.META:
#                 auth = request.META['HTTP_AUTHORIZATION'].split()
#                 if len(auth) == 2 and auth[0].lower() == "basic":
#                     username, password = auth[1].split(':')
#                     print(username)
#                     print(password)
#                     user = authenticate(request=request, email=username, password=password)
#                     if user:
#                         request.user = user
#                         return self.get_response(request)
#         response = HttpResponse()
#         response.status_code = 401
#         response['WWW-Authenticate'] = 'Basic realm="Restricted API"'
#         return response
