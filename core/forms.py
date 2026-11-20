from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db import transaction

from .models import Profile, avatar_validators

User = get_user_model()


class StyledFieldsMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control form-control-ask'


class LoginForm(StyledFieldsMixin, AuthenticationForm):
    pass


class SignupForm(StyledFieldsMixin, UserCreationForm):
    email = forms.EmailField(label='Электронная почта')
    first_name = forms.CharField(label='Имя на сайте', max_length=150)

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email', 'first_name')

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Profile.objects.create(user=user)
        return user


class ProfileForm(StyledFieldsMixin, forms.ModelForm):
    email = forms.EmailField(label='Электронная почта')
    first_name = forms.CharField(label='Имя на сайте', max_length=150)
    avatar = forms.ImageField(
        label='Аватар',
        required=False,
        help_text='JPG, PNG или WebP, до 2 МБ.',
        validators=avatar_validators,
        widget=forms.ClearableFileInput(attrs={'accept': 'image/jpeg,image/png,image/webp'}),
    )

    class Meta:
        model = User
        fields = ('email', 'first_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile = getattr(self.instance, 'profile', None) or Profile(user=self.instance)
        self.initial['avatar'] = self.profile.avatar

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            avatar = self.cleaned_data['avatar']
            if avatar is False:
                self.profile.avatar = ''
            elif avatar:
                self.profile.avatar = avatar
            if self.profile.pk is None:
                Profile.objects.get_or_create(user=user, defaults={'avatar': self.profile.avatar})
            elif 'avatar' in self.changed_data:
                self.profile.save(update_fields=['avatar'])
        return user
