from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect


def index(request):
    return render(request, 'index.html', {'welcome_page': 'Hello worlds in this python filex'})


def signin(request):
    if request.user.is_authenticated:
        return redirect(to='index')

    if request.method == 'GET':
        return render(request, 'signin.html')

    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
            else:
                return render(request, 'signin.html', {'warning_message': 'Credentials are wrong'})

        return redirect(to='index')
