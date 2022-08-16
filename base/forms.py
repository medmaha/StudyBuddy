from django import forms
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from .models import Room, User, Groups


class MyUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=200)
    class Meta:
        model = User
        fields = ['avatar','email', 'name', 'username', 'password1', 'password2']
        # fields = '__all__'


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'first_name', 'last_name', 'username', 'email', 'bio']
        # fields = '__all__'


class  GroupForm(forms.ModelForm):
    """docstring for  GroupForm."""
    class Meta:
        model = Groups
        fields = ['name']
