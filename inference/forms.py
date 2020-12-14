from django.forms import ModelForm

from inference.models import FileModel


class FileForm(ModelForm):
    class Meta:
        model = FileModel
        fields = ['file']