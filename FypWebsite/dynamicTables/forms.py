from django import forms
from django.forms.widgets import Select, SelectMultiple

class tableCreation(forms.Form):
    verbose_name = forms.CharField(widget=forms.TextInput(attrs={
                            "placeholder":"Table name",
                            "class":"form-control table-form-container-name"
                            })
                            )
    table_group = forms.CharField(initial="Test",widget=forms.TextInput(attrs={
                            "placeholder":"Table group",
                            "class":"form-control table-form-group"
                            })
                            )

class SelectWOA(Select):
    """
    Select With Option Attributes:
        subclass of Django's Select widget that allows attributes in options,
        like disabled="disabled", title="help text", class="some classes",
              style="background: color;"...

    Pass a dict instead of a string for its label:
        choices = [ ('value_1', 'label_1'),
                    ...
                    ('value_k', {'label': 'label_k', 'foo': 'bar', ...}),
                    ... ]
    The option k will be rendered as:
        <option value="value_k" foo="bar" ...>label_k</option>
    """

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


class FieldCreation(forms.Form):
    def __init__(self,choices_param=None, *args, **kwargs):
        super(FieldCreation,self).__init__(*args, **kwargs)
        self.fields['max_length'].widget.attrs['class'] = 'ajax-max_length'
        self.fields['required'].widget.attrs['class'] = 'ajax-required'
        if choices_param!=None:
            self.fields['data_type'].choices=choices_param
    name=forms.CharField(
        widget=forms.TextInput(attrs={
                                "placeholder":"Field name",
                                "class":"form-control ajax-name"
                                })
                                )
    data_type=forms.ChoiceField(
         choices=[(0,"String"),(1,"Integer"),(2,"Float")],
         widget=SelectWOA(attrs={"class":"form-control ajax-data_type"}))
    max_length=forms.IntegerField(required=False)
    required=forms.BooleanField(required=False)
class DataInt(forms.Form):
    def __init__(self,required_in=None, *args, **kwargs):
        super(DataInt,self).__init__(*args, **kwargs)
        if required_in!=None:
            self.fields['intField'].required=required_in
    intField=forms.IntegerField(required=True)
class DataString(forms.Form):
    def __init__(self,required_in=None, *args, **kwargs):
        super(DataString,self).__init__(*args, **kwargs)
        if required_in!=None:
            self.fields['stringField'].required=required_in
    stringField=forms.CharField(required=True)
class DataFloat(forms.Form):
    def __init__(self,required_in=None, *args, **kwargs):
        super(DataFloat,self).__init__(*args, **kwargs)
        if required_in!=None:
            self.fields['floatField'].required=required_in
    floatField=forms.FloatField(required=True)
