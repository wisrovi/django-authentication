from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from baliza.models import RolUsuario


class PackBracelet(forms.Form):
    key = forms.CharField(label='Key', max_length=5000)
    string_pack = forms.CharField(label='StringPack', max_length=5000)


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')

    rolUsuario = forms.ModelChoiceField(queryset=RolUsuario.objects.all(), label="Rol Usuario",
                                        help_text="Elija un rol de usuario")

    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )
