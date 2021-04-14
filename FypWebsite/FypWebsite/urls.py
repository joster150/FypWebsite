"""FypWebsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from userAuth.views import loginPage,logoutUser,register,homePage
from documentation.views import docsPage,createDoc,viewDoc,editDoc
from dynamicTables.views import tablesPage,createTable,viewTable
from notebooks.views import notebooksPage,viewNotebook,uploadNotebook
from pipelines.views import pipelinesPage,createPipeline,viewPipeline
from . import settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',homePage),
    path('login/',loginPage),
    path('logout/',logoutUser),
    path('register/',register),
    path('pipelines/<str:pipe_slug>/',viewPipeline),
    path('pipelines/',pipelinesPage),
    path('create-pipeline/',createPipeline),
    path('tables/<str:view_slug>/',viewTable),
    path('tables/',tablesPage),
    path('create-table/',createTable),
    path('notebooks/<str:note_slug>/',viewNotebook),
    path('notebooks/',notebooksPage),
    path('upload-notebook/',uploadNotebook),
    path('docs/<str:edit_doc>/edit/',editDoc),
    path('docs/<str:view_doc>/',viewDoc),
    path('docs/',docsPage),
    path('create-doc/',createDoc),
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
