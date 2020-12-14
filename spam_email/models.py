from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse


# Create your models here.
class Email(models.Model):
    content = models.TextField()
    result = models.CharField(max_length=100)
    accuracy = models.CharField(max_length=100)
    last_updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='+',
        default='1',
    )

    def __str__(self):
        return self.content

    def get_absolute_url(self):
        return reverse('history', args=[str(self.id)])
