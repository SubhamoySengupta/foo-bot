from django.conf.urls import url
from views import *

urlpatterns = [
    url(r'^$', default),
    url(r'^load-posts/$', loadposts),
    url(r'^post/$', getpost),
    url(r'^post/comment$', comment_on_post),
    url(r'^post/the-comment$', post_the_comment),
    url(r'^sync/$', sync),
    url(r'^sync/sync-posts/$', sync_posts),
    url(r'^sync/load-post-tags/$', load_post_tags),
    url(r'^sync/sync-comments/$', sync_comments),
    url(r'^sync/sync-photos/$', sync_photos),
    url(r'^sync/sync-photos-2/$', sync_photos_2),
    url(r'^update/$', update),
    url(r'^update/update-stuffs$', update_stuffs),
]
