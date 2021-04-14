from django.shortcuts import render,redirect
from .forms import DocumentationPostForm,DocumentationImageForm
from .models import DocumentationPost,DocumentationImage
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required

# Create your views here.
def docsPage(request):
    context={'active_view':'docs'}
    template_name="documentation/documentationlist.html"

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
@login_required(login_url="/login/")
def createDoc(request):
    context={'active_view':'docs'}
    template_name="documentation/createDoc.html"
    form=DocumentationPostForm()
    #print(request.POST)
    if request.method=="POST":
        form=DocumentationPostForm(data={'title':request.POST.get('title'),'content':request.POST.get('content'),'user':request.user})

        if form.is_valid():
            form.save()
            return redirect('/docs/'+slugify(request.POST.get('title'))+'/')
    context['form']=form
    return render(request,template_name,context)
@login_required(login_url="/login/")
def viewDoc(request,view_doc):
    context={'active_view':'docs'}
    template_name="documentation/viewDoc.html"
    doc=DocumentationPost.objects.filter(slug=view_doc)
    if doc.exists():
        doc_images=DocumentationImage.objects.filter(post=doc[0])
        context['post']={
        'title':doc[0].title,
        'content':doc[0].content,
        'user':doc[0].user,
        'edit':doc[0].get_edit_url(),
        'images':[{'url':im.image.url,'caption':im.caption} for im in doc_images]
        }
    return render(request,template_name,context)
@login_required(login_url="/login/")
def editDoc(request,edit_doc=""):
    context={'active_view':'documentation'}
    template_name="documentation/editDoc.html"

    doc_post=DocumentationPost.objects.filter(slug=edit_doc)
    if doc_post.exists():
        if request.user==doc_post[0].user:
            context['creator']=True
            form=DocumentationPostForm(data={'title':doc_post[0].title,'content':doc_post[0].content})
            imgs=DocumentationImage.objects.filter(post=doc_post[0])
            im_list=[]
            if imgs.exists():
                for im in imgs:
                    im_list.append(im.caption)
                context['images']=im_list
            print(request.POST)
            if request.method=="POST" and 'caption' in request.POST:
                success=False
                img_form=DocumentationImageForm(request.POST,request.FILES)
                if img_form.is_valid():
                    img=img_form.save(commit=False)
                    img.post=doc_post[0]
                    img.image_number=len(im_list)+1
                    img.save()
                    success=True
                    imgs=DocumentationImage.objects.filter(post=doc_post[0])
                    im_list=[]
                    if imgs.exists():
                        for im in imgs:
                            im_list.append(im.caption)
                        context['images']=im_list
            img_form=DocumentationImageForm()
            if request.method=="POST" and 'title' in request.POST:
                form=DocumentationPostForm(data={'title':request.POST.get('title'),'content':request.POST.get('content'),'user':request.user},instance=doc_post[0])
                if form.is_valid():
                    form.save()
                    return redirect('/docs/'+edit_doc+'/')
                    #print(form.cleaned_data.get('title'))
                    #doc_post[0].title=form.cleaned_data.get('title')
                    #doc_post[0].content=form.cleaned_data.get('content')
                    #doc_post[0].save()
            context['form']=form
            context['img_form']=img_form
    return render(request,template_name,context)
