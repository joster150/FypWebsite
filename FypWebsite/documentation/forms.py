from django import forms
from .models import DocumentationPost, DocumentationImage

class DocumentationPostForm(forms.ModelForm):
    class Meta:
        model = DocumentationPost
        fields = ['title','content','user']
    content=forms.CharField(widget=forms.Textarea(attrs={
        'style': 'width: 100%;resize: none;overflow: hidden;min-height: 50px;',
        'class':'form-control',
        'oninput':"auto_grow(this)"
    }))
    title=forms.CharField(widget=forms.TextInput(attrs={
        'style': 'width: 100%',
        'class':'form-control'
    }))
class DocumentationImageForm(forms.ModelForm):
    class Meta:
        model = DocumentationImage
        fields=['image','caption']
