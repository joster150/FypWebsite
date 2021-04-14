from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import NotebookModel
import sys,os
class NotebookForm(forms.ModelForm):
    class Meta:
        model = NotebookModel
        fields = ['verbose_name','notebook_group', 'notebook','notebook_test']
    update=forms.BooleanField(required=False)
    def clean(self):
        #print(self.cleaned_data.get('update'))
        if not self.cleaned_data.get('update'):
            file_path = os.path.join(settings.SCRIPTS_ROOT,
                self.cleaned_data.get('notebook_group').upper()+"/" + str(self.cleaned_data.get('notebook')))
            file_path2 = os.path.join(settings.SCRIPTS_ROOT,
                self.cleaned_data.get('notebook_group').upper()+"/" + str(self.cleaned_data.get('notebook_test')))
            if os.path.isfile(file_path):
                raise ValidationError('Notebook already exists')
            elif os.path.isfile(file_path2):
                raise ValidationError('Noteebook test already exists')
        return self.cleaned_data
