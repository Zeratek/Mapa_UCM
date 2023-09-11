from django import forms
from django.forms import ModelForm, HiddenInput
from crispy_forms.helper import FormHelper
from .models import Edificacion

class createEdificationForm(ModelForm):
    class Meta:
        model = Edificacion
        fields = ['nombre','pertenece']
        labels = {'nombre':'Nombre Edificacion','pertenece':'Pertenece a'}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # asi vuelves tus campos no requeridos
        self.fields['pertenece']= forms.ModelChoiceField(queryset=  Edificacion.objects.filter(pertenece__isnull=True))
        self.fields['pertenece'].required = False