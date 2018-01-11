from django import forms
from .models import DataSet, Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=200)
    last_name = forms.CharField(max_length=200)
    email = forms.EmailField(max_length=500)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'location', 'birth_date', 'associated_with')

class DataSetForm(forms.ModelForm):
    class Meta:
        model = DataSet
        fields = ['DataSet_Title', 'DataSet_Description']
        labels = {'DataSet_Title': '', 'DataSet_Description': ''}

class ColumnForm(forms.Form):
    cname = forms.CharField(max_length=100)
    labels = {'cname': ''}

class DataForm(forms.Form):
    dvalue = forms.CharField(max_length=100)
    labels = {'dvalue': ''}

class deleteRecordForm(forms.Form):
    pass