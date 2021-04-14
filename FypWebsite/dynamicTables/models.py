from django.db import models
from django.conf import settings
User = settings.AUTH_USER_MODEL
from django.template.defaultfilters import slugify
import jsonfield
# Create your models here.
class step_tracker(models.Model):
    step=models.IntegerField()

class ModelDefinition(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    verbose_name = models.CharField(max_length=50)
    name = models.CharField(max_length=50, unique=True)
    table_group = models.CharField(max_length=50,default="Test")
    definition = jsonfield.JSONField()

    def save(self, *args, **kwargs):
        self.name = slugify(self.verbose_name)
        super().save(*args, **kwargs)

class Data(models.Model):
    model_definition = models.ForeignKey(ModelDefinition, on_delete=models.CASCADE)
    data = jsonfield.JSONField(unique=True)
