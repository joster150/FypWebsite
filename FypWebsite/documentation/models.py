from django.db import models
from django.conf import settings
from django.dispatch import receiver
User =settings.AUTH_USER_MODEL
from django.template.defaultfilters import slugify

class DocumentationPost(models.Model):
    user = models.ForeignKey(User,default=1, on_delete=models.SET_DEFAULT)
    title = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    def get_post_url(self):
        return f"/docs/{self.slug}"
    def get_edit_url(self):
        return f"/docs/{self.slug}/edit/"
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)
class DocumentationImage(models.Model):
    def generate_image_path(self, filename):
        foldername = "media/%s/%s" % (self.post.slug.upper(), filename)
        return foldername
    post=models.ForeignKey(DocumentationPost,on_delete=models.CASCADE)
    image=models.ImageField(upload_to=generate_image_path)
    #print(image.url)
    image_number=models.IntegerField(default=1)
    caption=models.CharField(max_length=100)
    class Meta:
        unique_together = ('post', 'image_number')

@receiver(models.signals.post_delete, sender=DocumentationImage)
def auto_delete_image_on_delete(sender, instance, **kwargs):
    """
    Deletes notebook from filesystem
    when corresponding `image` object is deleted.
    """
    if instance.image:
        #print(instance.image.path)
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
