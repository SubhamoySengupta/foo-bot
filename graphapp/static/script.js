

var nextPost = function(argument, count) {
    $.ajax({
        url: "sync-posts",
        type: "GET",
        data: {
            "next_url":argument,
        },
        success: function(data){
            console.log(count)
            console.log(data)
            var toAppend = '<tr><td><i class="fa fa-id-badge"></i> Count</td><td><span class="badge">'+ (count + 1) +'</span></td></tr>'
            toAppend += '<tr><td><i class="fa fa-id-card-o"></i> ID</td><td>'+data["id"]+'</td></tr>'
            toAppend += '<tr><td><i class="fa fa-calendar-o"></i> Day</td><td>'+data["date"]+'</td></tr>'
            toAppend += '<tr><td><i class="fa fa-clock-o"></i> Time</td><td>'+data["time"]+'</td></tr>'
            toAppend += '<tr><td><i class="fa fa-newspaper-o"></i> Status Type</td><td>"'+data["status_type"]+'"</td></tr>'
            $(".sync-post").html(toAppend);
            if(data !==null){
                          if (data["next"] && data["next"] !==null ) {
                              nextPost(data["next"], count + 1)
                          }
                        }
            else{
                $("#syncPostBtn").removeClass("disabled").html('<i class="fa fa-refresh"></i> Sync');
            }
        },  
        failure: function(data){
            console.log(data)
        }

    });    
}

var syncPosts = function(argument) {
    $("#syncPostBtn").addClass("disabled").html('<i class="fa fa-spinner fa-pulse fa-fw"></i> Syncing ...');
    $.ajax({
        url: "sync-posts",
        type: "GET",
        success: function(data){
            console.log(data)
            var toAppend = '<tr><td><i class="fa fa-check-square-o"></i> Count</td><td><span class="badge">1</span></td></tr>'
            toAppend += '<tr><td><i class="fa fa-id-card-o"></i> ID</td><td>'+data["id"]+'</td></tr>'
            toAppend += '<tr><td><i class="fa fa-calendar-o"></i> Day</td><td>'+data["date"]+'</td></tr>'
            toAppend += '<tr><td><i class="fa fa-clock-o"></i> Time</td><td>'+data["time"]+'</td></tr>'
            toAppend += '<tr><td><i class="fa fa-newspaper-o"></i> Status Type</td><td>"'+data["status_type"]+'"</td></tr>'
            $(".sync-post").html(toAppend);
            if (data["next"] !==null)
                nextPost(data["next"], 1)
        },  
        failure: function(data){
            console.log(data)
        }
    });
}


var loadPostTags = function(argument) {
    $("#syncCommentBtn").addClass("disabled").html('<i class="fa fa-spinner fa-pulse fa-fw"></i> Syncing ...');
    $.ajax({
        url: "load-post-tags",
        type: "GET",
        success: function(data){
            console.log(data)
            syncComments(data["posts"], 0)
        },  
        failure: function(data){
            console.log(data)
        }
    });
}


var syncComments = function(ids, count) {
        /*$(".sync-commment-label").removeClass("hidden").html(i+1);*/
        if (count < ids.length){
            $.ajax({
                url: "sync-comments",
                type: "GET",
                data: {
                    id:ids[count],
                },
                success: function(data){
                    console.log(data);
                    var toAppend = '<tr><td><i class="fa fa-check-square-o"></i> Count</td><td><span class="badge">'+ (count + 1) +'</span></td></tr>';
                    toAppend += '<tr><td><i class="fa fa-id-badge"></i> POST ID</td><td>'+ ids[count] +'</td></tr>';
                    $(".sync-comment").html(toAppend);
                    syncComments(ids, count + 1);
                },  
                failure: function(data){
                    console.log(data)
                }
            });           
        }
        else{
            $("#syncCommentBtn").removeClass("disabled").html('<i class="fa fa-refresh"></i> Sync');
        }
    /*    $(".sync-commment-label").addClass("hidden").html("");*/
}

var syncPhotos = function() {
        $("#syncPhotosBtn").addClass("disabled").html('<i class="fa fa-spinner fa-pulse fa-fw"></i> Syncing ...');
    $.ajax({
        url: "sync-photos",
        type: "GET",
        success: function(data){
            console.log(data);
            syncPhotos2(data["posts"], 0)
        },  
        failure: function(data){
            console.log(data)
        }
    });
}

var syncPhotos2 = function(posts, cnt) {
    if (cnt < posts.length) {
        $.ajax({
            url: "sync-photos-2",
            type: "GET",
            data: {
                'id': posts[cnt]["id"],
                'status_type': posts[cnt]["status_type"]
            },
            success: function(data){
                console.log(data)
                var statusIcon = null; 
                if (posts[cnt]["status_type"] == 1)
                    statusIcon = '<i class="fa fa-picture-o"></i>';
                if (posts[cnt]["status_type"] == 3)
                    statusIcon = '<i class="fa fa-file-video-o"></i>';
                var toAppend = '<tr><td><i class="fa fa-check-square-o"></i> Count</td><td><span class="badge">'+ (cnt + 1) +'</span></td></tr>';
                toAppend += '<tr><td><i class="fa fa-id-card-o"></i> POST ID</td><td>'+ posts[cnt]["id"] +'</td></tr>';
                toAppend += '<tr><td><i class="fa fa-id-badge"></i> Type</td><td>'+ statusIcon +'</td></tr>';
                toAppend += '<tr><td><i class="fa fa-newspaper-o"></i> Media ID</td><td>'+ data["targets"] +'</td></tr>';
                $(".sync-photos").html(toAppend);

                syncPhotos2(posts, cnt + 1)    
            },  
            failure: function(data){
                console.log(data)
            }
        });
    }
    else{
        $("#syncPhotosBtn").removeClass("disabled").html('<i class="fa fa-refresh"></i> Sync');
    }
}