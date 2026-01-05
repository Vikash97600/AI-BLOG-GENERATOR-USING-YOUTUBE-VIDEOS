from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from bs4 import BeautifulSoup
import re

class ActiveBlogPostManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class BlogPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    youtube_title = models.CharField(max_length=300)
    youtube_link = models.URLField()
    generated_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    deleted_at = models.DateTimeField(null=True, blank=True)  # soft delete timestamp
    
    objects = ActiveBlogPostManager()  # default manager: only active (not deleted) posts
    all_objects = models.Manager()     # includes deleted posts
    
    def __str__(self):
        return self.youtube_title
    
    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()
    
    def restore(self):
        self.deleted_at = None
        self.save()
