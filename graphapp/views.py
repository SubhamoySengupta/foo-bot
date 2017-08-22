from django.shortcuts import render_to_response
from django.http import HttpResponse
import json
from time import time
import graphsocket
import miner
import datetime as dt
from models import *
import datetime
from django.core import serializers
# Create your views here.
from django.db.models import Max, Min, Count, Case, When


def default(request):
    return render_to_response('index.html')

def loadposts(request):
    posts = Posts.objects.all().order_by('timestamp')
    res = {"data":[]}
    a = res["data"]
    for post in posts:
        dt = datetime.datetime.fromtimestamp(int(post.timestamp)).strftime('%a %b %d, %Y %H:%M:%S')
        b = [
             post.id,
             post.message,
             post.story,
             post.privacy,
             post.status_type,
             post.other_urls,
             dt
            ]
        a.append(b)

    return HttpResponse(json.dumps(res), content_type="application/json")

def sync(request):
    return render_to_response('sync.html')

def sync_posts(request):
    next_url = request.GET.get("next_url", None)
    if next_url is not None:
        res = miner.sync_posts(next_url)
    else:
        res = miner.sync_posts()

    if "error" in res:
        res["status"] = "Not OK"
    else:    
        res["date"] = dt.datetime.fromtimestamp(int(res["time"])).strftime("%A %d, %Y")
        res["time"] = dt.datetime.fromtimestamp(int(res["time"])).strftime("%H:%M:%S")   
        res["status"] = "OK"
    return HttpResponse(json.dumps(res), content_type="application/json")


def load_post_tags(request):
    posts = []
    for post in Posts.objects.all():
        posts.append(post.id)            
    return HttpResponse(json.dumps({"posts":posts}), content_type="application/json")

def sync_comments(request):
    post_id = request.GET.get("id", None)
    res = miner.sync_comments(post_id)
    print res
    return HttpResponse(json.dumps(res), content_type="application/json")

def sync_photos(request):
    posts = []
    for post in Posts.objects.all():
        posts.append({"id":post.id, "status_type":post.status_type})
    return HttpResponse(json.dumps({"posts":posts}), content_type="application/json")

def sync_photos_2(request):
    post_id = request.GET.get("id", None)
    status_type = request.GET.get("status_type", None)
    
    # if status_type != 1 and status_type != 3:
    #         return HttpResponse(json.dumps({"data":"No data"}), content_type="application/json")

    res = miner.sync_photos(post_id, status_type)
    return HttpResponse(json.dumps(res), content_type="application/json")

def update(request):
    dt = Posts.objects.aggregate(
                Max('timestamp'),
                Min('timestamp'), 
                Count('id'), 
                Count('image_url'), 
                Count('story'),
         )
    dt.update(Posts.objects.filter(privacy=0).aggregate(privacy_public__count=Count('privacy')))
    dt.update(Posts.objects.filter(privacy=1).aggregate(privacy_friends__count=Count('privacy')))
    dt.update(Posts.objects.filter(privacy=2).aggregate(privacy_graph__count=Count('privacy')))

    dt['timestamp__max'] = datetime.datetime.fromtimestamp(int(dt['timestamp__max'])).strftime("%A %d, %Y")
    dt['timestamp__min'] = datetime.datetime.fromtimestamp(int(dt['timestamp__min'])).strftime("%A %d, %Y")
    return render_to_response('update.html', dt)

def update_stuffs(request):
    dt = Posts.objects.aggregate(
                Max('timestamp'))
    next_url = request.GET.get("next_url", None)
    print next_url
    if next_url is not None:
        res = miner.update_stuffs(dt['timestamp__max'], next_url)
    else:
        res = miner.update_stuffs(dt['timestamp__max'])
   
    return HttpResponse(json.dumps(res), content_type="application/json")    


def getpost(request):
    post_id = request.GET.get("id", None)        
    p = Posts.objects.get(id=post_id)
    dt = datetime.datetime.fromtimestamp(int(p.timestamp)).strftime('%a %b %d, %Y %H:%M:%S')
    post = {
        'id': p.id,  
        'message': p.message,
        'other_urls':p.other_urls,  
        'timestamp': dt
    }

    pv = {0:"fa fa-globe", 1:"fa fa-users", 2:"fa fa-object-group"}
    st = {0:"fa fa-mobile", 1:"fa fa-picture-o", 2:"fa fa-share-alt", 3:"fa fa-file-video-o", 4:"fa fa-object-ungroup"}
    post['privacy'] = pv[p.privacy]
    post['status_type'] = st[p.status_type]

    images = []    
    imgs = Photos.objects.filter(post_id=post_id)
    if len(imgs) > 0:
        for image in imgs:
            im = {
                    'post_id':image.post_id, 
                    'image_url': image.image_url, 
                    'local_image_url': image.local_image_url,
                    'target_url':image.target_url
                 }
            images.append(im)

    videos = []    
    vids = Videos.objects.filter(post_id=post_id)
    if len(vids) > 0:
        for video in vids:
            vid = {
                    'post_id':video.post_id, 
                    'video_url': video.video_url,
                    'local_video_url': video.local_video_url, 
                    'target_url':video.target_url,
                    'vid_type':video.vid_type
                  }
            videos.append(vid)

    c = Comments.objects.filter(post_id=post_id)
    comments = []
    for comment in c:
        s = {}
        c_dt = datetime.datetime.fromtimestamp(int(comment.timestamp)).strftime('%a %b %d, %Y %H:%M:%S')
        s['message'] = comment.message
        s['timestamp'] = c_dt
        s['commenter_id'] = comment.commenter_id
        s["comment_type"] = comment.comment_type
        s["comment_id"] = comment.id
        if s["comment_type"] == "video_inline":
            media_url = Videos.objects.get(post_id=comment.id)
            s['media_url'] = media_url.video_url
        elif s["comment_type"] == "animated_image_video":
            media_url = Videos.objects.get(post_id=comment.id)
            s['media_url'] = media_url.video_url
        else:    
            s['media_url'] = comment.media_url
        comments.append(s)
    print videos    
    res = {'post':post, 'video_items':videos, 'image_items':images, 'comments':comments, 'medialen':len(videos) + len(images)}
        
    return render_to_response('post.html', res)

def comment_on_post(request):
    post_id = request.GET.get("id", None)
    return render_to_response('post-comment.html', {'id':post_id})

def post_the_comment(request):
    post_id = request.GET.get("id", None)
    res = miner.post_the_comment(post_id)
    return HttpResponse(json.dumps(res), content_type="application/json")
