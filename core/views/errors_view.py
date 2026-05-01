from django.shortcuts import render

def ratelimited_view(request, exception=None):
    response = render(request, 'erros/ratelimited.html', status=429)
    response['Retry-After'] = '60'
    return response
