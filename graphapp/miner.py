import requests, json
from dateutil import parser
from time import mktime
from models import *
import graphsocket

# App --> FooBot
# AppId
# 1809392732634214 
# UserToken 
# EAAZAtohMWfGYBABy9kFisVSCt6WYY2PsrhGt6UZAGo4R9f6FI31Ebh9Omi8sONq3nThI6g51GDAvF3TNmdyl9MmXjMpPbwoR4O4jtEsXBQk4kYe0lZBGXJ7gyyTsi2HGS9S3WucDtHO8iueSpdozB6vTXUr6oIZD

ACCESS_TOKEN = "EAAZAtohMWfGYBABy9kFisVSCt6WYY2PsrhGt6UZAGo4R9f6FI31Ebh9Omi8sONq3nThI6g51GDAvF3TNmdyl9MmXjMpPbwoR4O4jtEsXBQk4kYe0lZBGXJ7gyyTsi2HGS9S3WucDtHO8iueSpdozB6vTXUr6oIZD"
BASE_URL = "https://graph.facebook.com"


def sync_posts(TARGET_URL=None):
    if TARGET_URL is None:
        TARGET_URL = BASE_URL + "/v2.8/me/posts?"
        params = [  
                    "privacy", 
                    "message", 
                    "full_picture", 
                    "created_time",
                    "link", 
                    "story", 
                    "status_type", 
                    "object_id"
                ]

        param_query = ','.join(params)
        # 1481824059 dec 14
        # 1470009600 aug 
        request_param = {'fields':param_query, 'access_token':ACCESS_TOKEN, 'limit':1, 'since':1470009600}
        res = requests.get(TARGET_URL, params=request_param)
    else:
        res = requests.get(TARGET_URL)
    res = res.json()
    # print res
    if "error" in res:
        return res
    if "data" in res:
        if len(res["data"]) is not 0:
            data = res["data"]

            for item in data:
                temp = dict(
                    id=None,
                    privacy=None, 
                    message=None, 
                    full_picture=None, 
                    created_time=None,
                    link=None, 
                    story=None, 
                    status_type=None, 
                    object_id=None,
                    timestamp=None
                    )
                if "id" in item:
                    temp["id"] = item["id"]
                else:
                    continue
                if "privacy" in item:
                    temp["privacy"] = item["privacy"]["value"]
                if "message" in item:
                    temp["message"] = item["message"]
                if "full_picture" in item:
                    temp["full_picture"] = item["full_picture"]
                if "created_time" in item:
                    temp["created_time"] = item["created_time"]
                if "link" in item:
                    temp["link"] = item["link"]
                if "story" in item:
                    temp["story"] = item["story"]
                if "status_type" in item:
                    temp["status_type"] = item["status_type"]
                if "object_id" in item:
                    temp["object_id"] = item["object_id"]

                dt = parser.parse(item["created_time"])
                dt = mktime(dt.timetuple())
                try:   
                    db = Posts.objects.create(id=temp["id"], timestamp=dt)
                    if temp["privacy"] == "SELF" or temp["privacy"] == "CUSTOM":
                        db.privacy = 2
                    if temp["privacy"] == "ALL_FRIENDS" or temp["privacy"] == "FRIENDS_OF_FRIENDS":
                        db.privacy = 1
                    if temp["privacy"] == "EVERYONE":
                        db.privacy = 0
                    db.message = temp["message"]
                    db.image_url = temp["full_picture"]
                    db.other_urls = temp["link"]
                    db.story = temp["story"]
                    if temp["status_type"] == "mobile_status_update" or temp["status_type"] == "wall_post":
                        db.status_type = 0
                    elif temp["status_type"] == "added_photos":
                        db.status_type = 1
                    elif temp["status_type"] == "shared_story":
                        db.status_type = 2
                    elif temp["status_type"] == "added_video":
                        db.status_type = 3    
                    else:
                        db.status_type = 4    
                    db.object_id = temp["object_id"]
                    db.save()
                except:
                    pass

    if "paging" in res:
        if "next" in res["paging"]:
            res = {'next':res["paging"]["next"],'status_type':temp["status_type"],'id':temp["id"],'time':dt}
            return res
        else:
            return None

def get_comment_inline_video(target_id):
    TARGET_URL = BASE_URL + "/v2.8/" + target_id
    params = "source"
    request_param = {'fields':params, 'access_token':ACCESS_TOKEN}
    res = requests.get(TARGET_URL, params=request_param)
    res = res.json()
    if "source" in res:
        return res["source"]
    else:
        return None

def sync_comments(post_id):
    TARGET_URL = BASE_URL + "/v2.8/" + post_id
    params = "comments{attachment, message, created_time, from}"
    request_param = {'fields':params, 'access_token':ACCESS_TOKEN}
    res = requests.get(TARGET_URL, params=request_param)
    res = res.json()
    if "error" in res:
        return res

    if "comments" in res:
        if "data" in res["comments"]:
            if len(res["comments"]["data"]) is not 0:
                data = res["comments"]["data"]
                
                for item in data:
                    temp = dict(
                        id=None,
                        post_id=None, 
                        commenter_id=None,
                        message=None, 
                        media_url=None,
                        comment_type=None,
                        target_id=None,
                        target_url=None,
                        video_url=None,
                        timestamp=None
                        )
                    temp["post_id"] = post_id
                    if "id" in item:
                        temp["id"] = item["id"]
                    else:
                        continue

                    if "attachment" in item:
                        target_id = None
                        if "media" in item["attachment"]:
                            if "image" in item["attachment"]["media"]:
                                if "src" in item["attachment"]["media"]["image"]:
                                    temp["media_url"] = item["attachment"]["media"]["image"]["src"]
                        if "type" in item["attachment"]:
                            temp["comment_type"] = item["attachment"]["type"]
                            if temp["comment_type"] == "video_inline":
                                    temp["target_id"] = item["attachment"]["target"]["id"]
                                    temp["target_url"] = item["attachment"]["target"]["url"]
                                    temp["video_url"] = get_comment_inline_video(temp["target_id"])
                            if temp["comment_type"] == "animated_image_video":
                                    temp["target_id"] = item["attachment"]["target"]["id"]
                                    temp["target_url"] = item["attachment"]["target"]["url"]
                                    temp["video_url"] = get_comment_inline_video(temp["target_id"])
                                    temp["media_url"] = None

                    if "from" in item:
                        if "id" in item["from"]:
                            temp["commenter_id"] = item["from"]["id"]
                    if "message" in item:
                        temp["message"] = item["message"]
                    if "created_time" in item:
                        dt = parser.parse(item["created_time"])
                        dt = mktime(dt.timetuple())
                    try:   
                        db = Comments.objects.create(id=temp["id"], timestamp=dt)
                        db.message = temp["message"]
                        db.media_url = temp["media_url"]
                        db.post_id = temp["post_id"]
                        db.commenter_id = temp["commenter_id"]
                        db.comment_type = temp["comment_type"]
                        db.save()
                        if temp["comment_type"] == "video_inline":
                            db = Videos.objects.create(target_id=temp["target_id"])
                            db.post_id = temp["id"]
                            db.video_url = temp["video_url"]
                            db.target_url = temp["target_url"]

                            db.save()
                        if temp["comment_type"] == "animated_image_video":
                            db = Videos.objects.create(target_id=temp["target_id"])
                            db.post_id = temp["id"]
                            db.video_url = temp["video_url"]
                            db.target_url = temp["target_url"]
                            db.vid_type = "gif"
                            db.save()
                    except:
                        pass

        if "paging" in res:
            if "next" in res["paging"]:
                next_urls = res["comments"]["paging"]["next"]
                return sync_comments2(next_urls)
            else:
                return None


def sync_comments2(TARGET_URL):
    res = requests.get(TARGET_URL)
    res = res.json()
    # print res
    if "error" in res:
        return res

        if "data" in res:
            if len(res["data"]) is not 0:
                data = res["data"]
                
                for item in data:
                    temp = dict(
                        id=None,
                        post_id=None, 
                        commenter_id=None,
                        message=None, 
                        media_url=None,
                        comment_type=None,
                        target_id=None,
                        target_url=None,
                        video_url=None,
                        timestamp=None
                        )
                    temp["post_id"] = post_id
                    if "id" in item:
                        temp["id"] = item["id"]
                    else:
                        continue

                    if "attachment" in item:
                        if "media" in item["attachment"]:
                            if "image" in item["attachment"]["media"]:
                                if "src" in item["attachment"]["media"]["image"]:
                                    temp["media_url"] = item["attachment"]["media"]["image"]["src"]
                        if "type" in item["attachment"]:
                            temp["comment_type"] = item["attachment"]["type"]
                            if temp["comment_type"] == "video_inline":
                                    temp["target_id"] = item["attachment"]["target"]["id"]
                                    temp["target_url"] = item["attachment"]["target"]["url"]
                                    temp["video_url"] = get_comment_inline_video(temp["target_id"])
                            if temp["comment_type"] == "animated_image_video":
                                    temp["target_id"] = item["attachment"]["target"]["id"]
                                    temp["target_url"] = item["attachment"]["target"]["url"]
                                    temp["video_url"] = get_comment_inline_video(temp["target_id"])
                                    temp["media_url"] = None
                    
                    if "from" in item:
                        if "id" in item["from"]:
                            temp["commenter_id"] = item["from"]["id"]
                    if "message" in item:
                        temp["message"] = item["message"]
                    if "created_time" in item:
                        dt = parser.parse(item["created_time"])
                        dt = mktime(dt.timetuple())
                    
                    try:   
                        db = Comments.objects.create(id=temp["id"], timestamp=dt)
                        db.message = temp["message"]
                        db.media_url = temp["media_url"]
                        db.post_id = temp["post_id"]
                        db.commenter_id = temp["commenter_id"]
                        db.comment_type = temp["comment_type"]
                        db.save()
                        temp["comment_type"]
                        if temp["comment_type"] == "video_inline":
                            print "HERE VID"
                            db = Videos.objects.create(target_id=temp["target_id"])
                            db.post_id = temp["id"]
                            db.video_url = temp["video_url"]
                            db.target_url = temp["target_url"]
                            db.save()
                        if temp["comment_type"] == "animated_image_video":
                            print "HERE GIF"
                            db = Videos.objects.create(target_id=temp["target_id"])
                            db.post_id = temp["id"]
                            db.video_url = temp["video_url"]
                            db.target_url = temp["target_url"]
                            db.vid_type = "gif"
                            db.save()
                    except:
                        pass

        if "paging" in res:
            if "next" in res["paging"]:
                next_url = res["paging"]["next"]
                sync_comments2(next_url)
            else:
                return None

def get_video_url(vid):
    TARGET_URL = BASE_URL + "/v2.8/" + vid
    request_param = {'fields':'source','access_token':ACCESS_TOKEN}
    res = requests.get(TARGET_URL, params=request_param)
    res = res.json()
    if "source" in res:
        return res["source"]
    else:
        return None

def getgif(target_id):
    TARGET_URL = BASE_URL + "/v2.8/" + target_id
    request_param = {'fields':'source','access_token':ACCESS_TOKEN}
    res = requests.get(TARGET_URL, params=request_param)
    res = res.json()    
    return res["source"]
    
def sync_photos(post_id, status_type):
    TARGET_URL = BASE_URL + "/v2.8/" + post_id + "/attachments"
    request_param = {'access_token':ACCESS_TOKEN}
    res = requests.get(TARGET_URL, params=request_param)
    res = res.json()    
    if "error" in res:
        return res
    if "data" in res and len(res["data"])>0:
        if "subattachments" in res["data"][0]:
            image_urls = []
            target_urls = []
            target_ids = []
            for im in res["data"][0]["subattachments"]["data"]:
                target = im["target"]["url"]
                target_id = im["target"]["id"]

                if im["type"] == "animated_image_video":
                    image = getgif(target_id) 
                else:   
                    image = im["media"]["image"]["src"]
                
                target_ids.append(target_id)
                image_urls.append(image)
                target_urls.append(target)
                
                if im["type"] == "video":
                    vid_url = get_video_url(target_id)
                    try:
                        vid = Videos.objects.create(post_id=post_id, video_url=vid_url, target_url=target)
                        if "id" in im["target"]:
                            vid.target_id = target_id
                        vid.save()
                        continue

                    except:
                        pass   
                try:
                    if im["type"] == "animated_image_video":
                        vid = Videos.objects.create(post_id=post_id, video_url=image, target_url=target)
                        vid.vid_type = "gif"
                        if "id" in im["target"]:
                            vid.target_id = target_id
                        vid.save()
                    else:
                        pic = Photos.objects.create(post_id=post_id, image_url=image, target_url=target)
                        if "id" in im["target"]:
                            pic.target_id = target_id
                        pic.save()
                except:
                    pass



            target_id_tpl ='[</br>'
            for tid in target_ids:
                target_id_tpl += '<span style="margin-left:20px">' + str(tid) + ",</span></br>"
            target_id_tpl += "]"
            return ({'images': image_urls, 'targets': target_id_tpl})
        else:
            target_id = None
            target = res["data"][0]["target"]["url"]
            if "id" in res["data"][0]["target"]:
                target_id = res["data"][0]["target"]["id"]
            if res["data"][0]["type"] == "animated_image_video":
                if res["data"][0]["target"]["id"]:
                    image = getgif(target_id) 
                else:
                    image = target
            else:   
                image = res["data"][0]["media"]["image"]["src"]

            if res["data"][0]["type"] == "video_inline":
                vid_url = get_video_url(target_id)
                try:
                    vid = Videos.objects.create(post_id=post_id, video_url=vid_url, target_url=target)
                    if "id" in res["data"][0]["target"]:
                        vid.target_id = target_id
                    vid.save()
                    return ({'images': image, 'targets': target_id})  
                except:
                    pass

            try:
                if res["data"][0]["type"] == "animated_image_video":
                    vid = Videos.objects.create(post_id=post_id, video_url=image, target_url=target)
                    vid.vid_type = "gif"
                    if "id" in res["data"][0]["target"]:
                        vid.target_id = target_id
                    vid.save()
                elif res["data"][0]["type"] == "animated_image_share":
                    vid = Photos.objects.create(post_id=post_id)
                    # 
                    # 
                    import urllib

                    s = target
                    d = s[s.find('?u=')+3:]
                    d = d[:d.find('&')]
                    d = urllib.unquote(d).decode('utf-8')
                    # 
                    # 
                    vid.image_url=d
                    vid.target_url=target
                    # vid.vid_type = "gif"
                    if "id" in res["data"][0]["target"]:
                        vid.target_id = target_id
                    vid.save()
                
                else:
                    pic = Photos.objects.create(post_id=post_id, image_url=image, target_url=target)
                    if "id" in res["data"][0]["target"]:
                        pic.target_id = target_id
                    pic.save()
            except:
                pass

            return ({'images': image, 'targets': target_id})    

    else:
        return {'images': "null", 'targets': "null"}

def update_stuffs(since, TARGET_URL=None):
    if TARGET_URL is None:
        TARGET_URL = BASE_URL + "/v2.8/me/posts?"
        params = [  
                    "privacy", 
                    "message", 
                    "full_picture", 
                    "created_time",
                    "link", 
                    "story", 
                    "status_type", 
                    "object_id"
                ]

        param_query = ','.join(params)
        request_param = {
                         'fields':param_query,
                         'access_token':ACCESS_TOKEN, 
                         'limit':1,
                         'since': since
        }
        res = requests.get(TARGET_URL, params=request_param)
    else:
        res = requests.get(TARGET_URL)
    res = res.json()
    # print res
    if "error" in res:
        return res
    if "data" in res:
        if len(res["data"]) is not 0:
            data = res["data"]

            for item in data:
                temp = dict(
                    id=None,
                    privacy=None, 
                    message=None, 
                    full_picture=None, 
                    created_time=None,
                    link=None, 
                    story=None, 
                    status_type=None, 
                    object_id=None,
                    timestamp=None
                    )
                if "id" in item:
                    temp["id"] = item["id"]
                else:
                    continue
                if "privacy" in item:
                    temp["privacy"] = item["privacy"]["value"]
                if "message" in item:
                    temp["message"] = item["message"]
                if "full_picture" in item:
                    temp["full_picture"] = item["full_picture"]
                if "created_time" in item:
                    temp["created_time"] = item["created_time"]
                if "link" in item:
                    temp["link"] = item["link"]
                if "story" in item:
                    temp["story"] = item["story"]
                if "status_type" in item:
                    temp["status_type"] = item["status_type"]
                if "object_id" in item:
                    temp["object_id"] = item["object_id"]

                dt = parser.parse(item["created_time"])
                dt = mktime(dt.timetuple())
                try:   
                    db = Posts.objects.create(id=temp["id"], timestamp=dt)
                    if temp["privacy"] == "SELF" or temp["privacy"] == "CUSTOM":
                        db.privacy = 2
                    if temp["privacy"] == "ALL_FRIENDS" or temp["privacy"] == "FRIENDS_OF_FRIENDS":
                        db.privacy = 1
                    if temp["privacy"] == "EVERYONE":
                        db.privacy = 0
                    db.message = temp["message"]
                    db.image_url = temp["full_picture"]
                    db.other_urls = temp["link"]
                    db.story = temp["story"]
                    if temp["status_type"] == "mobile_status_update" or temp["status_type"] == "wall_post":
                        db.status_type = 0
                    elif temp["status_type"] == "added_photos":
                        db.status_type = 1
                    elif temp["status_type"] == "shared_story":
                        db.status_type = 2
                    else:
                        db.status_type = 3    
                    db.object_id = temp["object_id"]
                    db.save()
                except:
                    pass

    if "paging" in res:

        if "next" in res["paging"]:
            print "YESSS"
            res = {'next':res["paging"]["next"],'status_type':temp["status_type"],'id':temp["id"],'time':dt}
            return res
        else:
            return None

def post_the_comment(comment_id):
    TARGET_URL = BASE_URL + "/v2.8/" + comment_id 
    request_param = {'fields':'attachment, message, created_time, from', 'access_token':ACCESS_TOKEN}
    res = requests.get(TARGET_URL, params=request_param)
    res = res.json()
    print res
    dt = parser.parse(res["created_time"])
    dt = mktime(dt.timetuple())
    try:
        if "attachment" in res:
            if "media" in res["attachment"]:
                if "image" in res["attachment"]["media"]:
                    if "src" in res["attachment"]["media"]["image"]:
                        media_url = res["attachment"]["media"]["image"]["src"]  

            if "from" in res:
                if "id" in res["from"]:
                    commenter_id = res["from"]["id"] 
        db = Comments.objects.create(id=res["id"], timestamp=dt)
        db.message = res["message"]
        db.media_url = media_url
        db.post_id = post_id
        db.commenter_id = commenter_id
        print "YESS"
        db.save()
    except:
        pass

if __name__ == "__main__":
    test()

