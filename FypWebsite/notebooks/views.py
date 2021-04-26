from django.shortcuts import render,redirect
from .forms import NotebookForm
from .models import NotebookModel
from django.http import JsonResponse
from django.template.defaultfilters import slugify
import os,sys
from django.conf import settings
from django.contrib.auth.decorators import login_required
dir = settings.SCRIPTS_ROOT
# Create your views here.
@login_required(login_url="/login/")
def notebooksPage(request):
    context={'active_view':'notebooks'}
    template_name="notebooks/notebooklist.html"

    text=request.GET.get('module_name')
    if request.is_ajax():
        if request.GET.get('ajax_type')=="func_info":
            text=text[text.index(":")+1:]
            modname=text[text.index("!")+1:]
            funcname=text[:text.index("!")]
            notebook=NotebookModel.objects.get(name=modname)
            descript=notebook.functions[funcname]
            print(modname,funcname,descript)
            return JsonResponse({'funcname':funcname,'funcdoc':descript,'mod_name':modname},status=200)
    notebooks=NotebookModel.objects.all()
    context['content_dicts']=[]
    context['content_template_name']="notebooks/notebookListCard.html"
    if notebooks.exists():
        for nb in notebooks:
            functions=[*nb.functions.keys()]
            context['content_dicts'].append({
            'name':nb.verbose_name,
            'slug_name':nb.name,
            'first_func':nb.functions[functions[0]],
            'description':nb.description,
            'functions':functions,
            })
    return render(request,template_name,context)
@login_required(login_url="/login/")
def viewNotebook(request,note_slug):
    context={'active_view':'notebooks'}
    template_name="notebooks/viewNotebook.html"
    nb=NotebookModel.objects.filter(name=note_slug)
    if nb.exists():
        context['nb_content']=nb[0].notebook_html
        context['nb_test_content']=nb[0].notebook_test_html
        context['nb_name']=nb[0].verbose_name
        context['nb_description']=nb[0].description
        context['download_nb']=nb[0].notebook.url
        context['download_test_nb']=nb[0].notebook_test.url
    return render(request,template_name,context)
@login_required(login_url="/login/")
def uploadNotebook(request):
    context={'active_view':'notebooks'}
    template_name="notebooks/uploadNotebook.html"
    context['content_template_name']="notebooks/notebookUploadCard.html"

    nb_script_groups=NotebookModel.objects.values_list('notebook_group',flat=True).distinct()
    notebooks=NotebookModel.objects.all()
    imported_notebooks={}
    if notebooks.exists():
        for fldr in nb_script_groups:
            sys.path.append(os.path.join(dir,fldr.upper()))
    if request.method=='POST':
        form=NotebookForm(request.POST, request.FILES)
        #update_form=BooleanInput(request.POST).as_p().replace('Form val','Update').replace('name="form_val"','name="update"')
        if form.is_valid():
            if form.cleaned_data.get("update"):
                #print(form.cleaned_data)
                obj=NotebookModel.objects.get(name=slugify(form.cleaned_data.get('verbose_name')))
                old_file=obj.notebook
                old_test_file=obj.notebook_test
                obj.notebook=form.cleaned_data.get('notebook')
                obj.notebook_test=form.cleaned_data.get('notebook_test')
                obj.save()
                success=obj.save2()
                if success!='success':
                    print('revert to old')
                    obj.notebook=old_file
                    obj.notebook_test=old_test_file
                    obj.save()
                    success=obj.save2()
                print(success)
            else:
                obj=form.save(commit=False)
                obj.user=request.user
                obj.save()
                success=obj.save2()
                print(success)
                form=NotebookForm()
            if "success"==success:
                print("redirecting")
                return redirect("/notebooks/"+obj.name+"/")

    notebook_form=NotebookForm()
    context['content_dicts']=[]
    context['content_dicts'].append({"title":"Upload Notebook",
                            "form":notebook_form,
                            "user":request.user})
    return render(request,template_name,context)
