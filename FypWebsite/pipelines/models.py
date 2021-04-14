from django.db import models
from django.conf import settings
from notebooks.models import NotebookModel
User =settings.AUTH_USER_MODEL
# Create your models here.
class Pipeline(models.Model):
    user = models.ForeignKey(User, default=1,null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    def get_complete_url(self):
        return f"/pipelines/use/{self.slug}"
class PipelineStep(models.Model):
    pipeline_id=models.ForeignKey(Pipeline, on_delete=models.CASCADE)
    step_num=models.IntegerField(default=1)
    module = models.ForeignKey(NotebookModel,on_delete=models.CASCADE,)#models.CharField(max_length=120)
    function = models.CharField(max_length=120)
    description = models.TextField()
    output = models.CharField(max_length=120)
    class Meta:
        unique_together = ('pipeline_id', 'step_num')
