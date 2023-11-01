from django import forms
from django.forms import ModelForm, HiddenInput
from crispy_forms.helper import FormHelper
from .models import Edificacion
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
class createEdificationForm(ModelForm):
    class Meta:
        model = Edificacion
        fields = ['nombre','piso','pertenece','informacion']
        labels = {'nombre':'Nombre Edificacion','piso':'Numero de piso','pertenece':'Pertenece a','informacion':'Informacion Edificacion'}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # asi vuelves tus campos no requeridos
        self.fields['pertenece']= forms.ModelChoiceField(queryset=  Edificacion.objects.filter(pertenece__isnull=True))
        self.fields['pertenece'].required = False

class loginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['password'].label = 'Contraseña'