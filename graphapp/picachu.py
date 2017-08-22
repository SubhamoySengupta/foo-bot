from django.db import models
from models import *
import urllib
import imghdr
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Pic(object):
    """docstring for Pic"""
    def __init__(self):
        self.photos = Photos.objects.all()
        self.path = BASE_DIR + "/static/media/raw/"
        self.pic_path = BASE_DIR + "/static/media/photos/"

    def download(self):
        print BASE_DIR
        for photo in self.photos:
            id = photo.id
            target_id = photo.target_id
            post_id = photo.post_id
            image_url = photo.image_url
            if target_id is None:
                pic_name = post_id
            else:
                pic_name = target_id
            
            pic_path = self.path + pic_name
            urllib.urlretrieve(image_url, pic_path)
            extension = imghdr.what(pic_path)
            if extension == "jpeg":
                extension = "jpg"
            os.rename(pic_path, self.pic_path + pic_name + "." + extension)

            # store in db
            self.store_in_db(id, self.pic_path + pic_name + "." + extension)
            

    def store_in_db(self, id, file_name):
        pic = Photos.objects.get(id=id)
        pic.local_image_url = file_name
        pic.save()


class Vid(object):
    """docstring for Pic"""
    def __init__(self):
        self.videos = Videos.objects.all()
        self.path = BASE_DIR + "/static/media/raw/"
        self.vid_path = BASE_DIR + "/static/media/videos/"

    def download(self):
        for video in self.videos:
            id = video.id
            target_id = video.target_id
            post_id = video.post_id
            video_url = video.video_url
            if target_id is None:
                vid_name = post_id
            else:
                vid_name = target_id
            
            vid_path = self.path + vid_name
            urllib.urlretrieve(video_url, vid_path)
            os.rename(vid_path, self.vid_path + vid_name)

            # store in db
            self.store_in_db(id, self.vid_path + vid_name)
            

    def store_in_db(self, id, file_name):
        pic = Videos.objects.get(id=id)
        pic.local_video_url = file_name
        pic.save()




Pic = Pic()
Vid = Vid()