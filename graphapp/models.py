from __future__ import unicode_literals

from django.db import models


# Create your models here.
class Posts(models.Model):
    id = models.CharField(max_length=35, primary_key=True)
    message = models.TextField(null=True)
    story = models.TextField(null=True)
    privacy = models.IntegerField(null=True)
    status_type = models.IntegerField(null=True)
    object_id = models.TextField(null=True)
    image_url = models.TextField(null=True)
    other_urls = models.TextField(null=True)
    timestamp = models.IntegerField()

 
class Comments(models.Model):
    id = models.CharField(max_length=35, primary_key=True)
    post_id = models.TextField(null=True)
    commenter_id = models.TextField(null=True)
    message = models.TextField(null=True)
    media_url = models.TextField(null=True)
    comment_type = models.TextField(null=True)
    timestamp = models.IntegerField()


class Photos(models.Model):
    target_id = models.TextField(null=True)
    post_id = models.TextField(null=True)
    image_url = models.TextField(null=True)
    target_url = models.TextField(null=True)
    local_image_url = models.TextField(null=True)
    class Meta:
        unique_together = ('post_id', 'image_url')


class Videos(models.Model):
    target_id = models.TextField(null=True)
    post_id = models.TextField(null=True)
    video_url = models.TextField(null=True)
    target_url = models.TextField(null=True)
    local_video_url = models.TextField(null=True)
    vid_type = models.TextField(default="video")
    class Meta:
        unique_together = ('post_id', 'video_url')