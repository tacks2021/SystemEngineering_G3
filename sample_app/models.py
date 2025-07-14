from django.db import models

choices = (
    (True, 'Yes'),
    (False, 'No'),
)

# Create your models here.
class Post(models.Model):
    Q1 = models.CharField(
        verbose_name="質問1",
        max_length=100,
        choices=choices,
        default=False,
    )
    micropost = models.CharField('tweet', max_length=140, blank=True)

    def __str__(self):
        return f'Post {self.id}: {self.micropost[:20]}'