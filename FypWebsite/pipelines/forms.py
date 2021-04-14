from django import forms
from django.forms.widgets import Select, SelectMultiple
class SelectWOA(Select):
    def create_option(self, name, value, label, selected, index,
                      subindex=None, attrs=None):
        if isinstance(label, dict):
            opt_attrs = label.copy()
            label = opt_attrs.pop('label')
        else:
            opt_attrs = {}
        option_dict = super(SelectWOA, self).create_option(name, value,
            label, selected, index, subindex=subindex, attrs=attrs)
        for key,val in opt_attrs.items():
            option_dict['attrs'][key] = val
        return option_dict
class PipelineCreateStep(forms.Form):
    def __init__(self,mod_choices_param=None,choices_param=None, *args, **kwargs):
        super(PipelineCreateStep,self).__init__(*args, **kwargs)
        if choices_param!=None and mod_choices_param!=None:
            self.fields['using_function'].choices=choices_param
            self.fields['using_module'].choices=mod_choices_param
    using_module= forms.ChoiceField(
        choices=[(0,"")],
         widget=SelectWOA(
         attrs={"class":"form-control ajax-using_modules"}
               )
        )
    using_function=forms.ChoiceField(
        choices=[(0,"")],
         widget=SelectWOA(
         attrs={"class":"form-control ajax-using_functions"}
               )
        )
    description=forms.CharField(
        widget=forms.Textarea(attrs={
                            "placeholder":"Description of step",
                            "class":"form-control ajax-description",
                            "rows":3
                            })
                            )
    output= forms.CharField(
        widget=forms.TextInput(attrs={
                                "placeholder":"Output Variable",
                                "class":"form-control ajax-output"
                                })
                                )

class PipelineCreateSubmit(forms.Form):
    title=forms.CharField(
        widget=forms.TextInput(attrs={
                                "placeholder":"Pipeline title",
                                "class":"form-control pipeline-title"
                                })
                                )
    description=forms.CharField(
        widget=forms.Textarea(attrs={
                            "placeholder":"Description of pipeline",
                            "class":"form-control pipeline-description",
                            "rows":4
                            })
                            )
class TextInput(forms.Form):
    form_val=forms.CharField(max_length=200)
class BooleanInput(forms.Form):
    form_val=forms.BooleanField(required=False)
class Include_Output(forms.Form):
    include_output=forms.BooleanField(required=False)
class IntInput(forms.Form):
    form_val=forms.IntegerField()
class FloatInput(forms.Form):
    form_val=forms.FloatField()
class Variable(forms.Form):
    def __init__(self,choices_param=None, *args, **kwargs):
        super(Variable,self).__init__(*args, **kwargs)
        if choices_param!=None:
            self.fields['form_val'].choices=choices_param
    form_val=forms.ChoiceField(
         choices=[(0,"")],
         widget=SelectWOA(
         attrs={"class":"form-control ajax-using_functions"}))
class TableParam(forms.Form):
    def __init__(self,choices_param=None, *args, **kwargs):
        super(TableParam,self).__init__(*args, **kwargs)
        if choices_param!=None:
         self.fields['form_val'].choices=choices_param
    form_val=forms.ChoiceField(
      choices=[(0,"")],
      widget=SelectWOA(
      attrs={"class":"form-control table_param"}))
class FileInput(forms.Form):
    form_val = forms.FileField()
class FilesInput(forms.Form):
    form_val = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
