from django import forms
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from .models import Account, Customer, Business

class LoginForm(forms.Form):
    email = forms.CharField(
        max_length=150,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email',
            'id': 'id_email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password',
            'id': 'id_password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'id': 'remember_me'
        })
    )

class RegistrationForm(forms.ModelForm, type):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your username',
            'id': 'id_username'
        })
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password',
            'id': 'id_password1'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm password',
            'id': 'id_password2'
        })
    )


    class Meta:
        model = Account
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter your email',
                'id': 'id_email'
            })
        }
    
    def __init__(self, *args, accountType, **kwargs):
        
        super().__init__(*args, **kwargs)
        # dynamic placeholder
        placeholer = "Name" if accountType == 'customer' else "Display Name"
        self.fields['username'].widget.attrs['placeholder'] = placeholer
        self.accountType = accountType
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2
    
    def save(self, commit=True):
        account = super().save(commit=False)
        account.password = make_password(self.cleaned_data['password1'])
        account.accountType = self.accountType
        if commit:
            account.save()
        return account