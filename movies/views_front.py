from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'movies/index.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    return render(request, 'movies/profile.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    
    # Add form-control class to fields for Bootstrap styling
    for field in form.fields.values():
        field.widget.attrs.update({'class': 'form-control'})
        
    return render(request, 'movies/register.html', {'form': form})

