from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout


def signin(request):
    if request.user.is_authenticated:
        return redirect(to='index')  # direct to twitter directly

    if request.method == 'GET':
        return render(request, 'auth_signin.html')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
            else:
                return render(request, 'auth_signin.html', {'warning_message': 'Credentials are wrong'})
        return redirect(to='index')


def sign_out(request):
    logout(request)
    return redirect(to='index')
