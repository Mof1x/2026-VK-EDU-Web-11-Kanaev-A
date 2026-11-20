from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods

from .forms import LoginForm, ProfileForm, SignupForm


class LoginView(DjangoLoginView):
    template_name = 'core/login.html'
    authentication_form = LoginForm


class SiteLogoutView(LogoutView):
    next_page = reverse_lazy('questions:index')


@require_http_methods(['GET', 'POST'])
def signup(request):
    if request.user.is_authenticated:
        return redirect('questions:index')
    form = SignupForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.save())
        return redirect('questions:index')
    return render(request, 'core/signup.html', {'form': form})


@login_required
@require_http_methods(['GET', 'POST'])
def profile(request):
    form = ProfileForm(
        request.POST if request.method == 'POST' else None,
        request.FILES if request.method == 'POST' else None,
        instance=request.user,
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Настройки профиля сохранены.')
        return redirect('core:profile')
    return render(request, 'core/profile.html', {'form': form})
