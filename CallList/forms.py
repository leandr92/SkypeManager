from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate

from .models import Account

class RegistrationFrom(UserCreationForm):
    email = forms.EmailField(max_length=60, help_text="Обязательное. Введите валидный email")

    class Meta:
        model = Account
        fields = ('email', 'username', 'password1','password2')

class AccountAuthenticationForm(forms.ModelForm):
   
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ('email', 'password')

    def clean(self):
        
        if self.is_valid():

            email = self.cleaned_data['email']
            password = self.cleaned_data['password']

            if not authenticate(email=email, password=password):
                raise forms.ValidationError('Неправильное имя пользователя')

class AccountUpdateForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = ('email', 'username', 'skype_login', 'skype_password')
    
    def clean_email(self):
        if self.is_valid():
            email = self.cleaned_data['email']

            try:
                account = Account.objects.exclude(pk=self.instance.pk).get(email=email)
            except Account.DoesNotExist:
                return email
            raise forms.ValidationError('Email "%s" уже используется.' % account)
