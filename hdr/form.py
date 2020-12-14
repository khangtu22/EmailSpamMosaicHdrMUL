from django import forms
from django.forms import ModelForm
from .models import FileHdrModel


class UploadFileForm(ModelForm):
    class Meta:
        model = FileHdrModel
        fields = ['file', 'expose_time']