from django.contrib import admin
from .models import Pipeline,PipelineStep
# Register your models here.
admin.site.register(Pipeline)
admin.site.register(PipelineStep)