from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    profile_image = models.ImageField(null=True, blank=True, upload_to="usuario/",
                                      default="imagenes/user-default.png")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.username)

    class Meta:
        ordering = ['id']

    @property
    def imageURL(self):
        try:
            url = self.profile_image.url
        except:
            url = ''

        return url


class Rol(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    user = models.ManyToManyField(User)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['id']