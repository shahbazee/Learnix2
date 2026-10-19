from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class SignupForm(forms.Form):
    email = forms.EmailField()
    display_name = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)