from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CreateUserForm
from documentation.forms import DocumentationPostForm,DocumentationImageForm
from documentation.models import DocumentationPost,DocumentationImage
# Create your views here.
def homePage(request):
    context={'active_view':'home'}
    template_name="userAuth/home.html"

    context['content_dicts']=[]
    doc_posts=DocumentationPost.objects.all()
    for post in doc_posts:
        context['content_dicts'].append({
            'title':post.title,
            'content':post.content,
            'url':post.get_post_url(),
            'user':post.user
            })

    context['content_template_name']="documentation/docListInner.html"

    return render(request,template_name,context)
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        context={'active_view':'login'}
        template_name="userAuth/login.html"
        if request.method == "POST":
            username=request.POST.get("username")
            password=request.POST.get("password")
            user=authenticate(request,username=username,password=password)
            if user is not None:
                login(request,user)
                next=request.GET.get('next')
                if isinstance(next,str):
                    return redirect(next)

                return redirect('/')
            else:
                messages.info(request,'Usename OR Password is incorrect')
                return render(request,template_name,context)
        return render(request,template_name,context)
@login_required(login_url="/login/")
def logoutUser(request):
    logout(request)
    return redirect('/login/')
def register(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        context={'active_view':'login'}
        template_name="userAuth/register.html"
        form=CreateUserForm()
        if request.method=='POST':
            form=CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request,"Account created for "+form.cleaned_data.get('username'))
                return redirect('/login/')
        context['form']=form
        return render(request,template_name,context)
