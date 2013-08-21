define(["tools/hash", "tools/ajax"], function(hashlib, ajax){
    var setUpPlayer = function(params){

        var currentVideo
            , root = params.root||$(document)
            , aspect = params.aspect || 0.5625
            , quality = params.quality || "hd720";

        root.find('.you-tube-container').each(function(idx, elem){
            var elemId = 'youtube-'+hashlib.UUID(), initial = $(elem).data("videoId");
            $(elem).append('<div id="'+elemId+'"></div>');
            currentVideo = new YT.Player(elemId, {
                height: $(elem).width() * aspect,
                width: $(elem).width(),
                videoId: initial,
                suggestedQuality: quality,
                playerVars : {controls:0, autohide:1, modestbranding :1, theme :'dark', wmode: "opaque"},
                events: {
                    onReady: function(event){event.target.setPlaybackQuality("hd720")}
                }
            });
        });
    }, loaded = $.Deferred();
    window.onYouTubePlayerAPIReady = function () {
        loaded.resolve();
    };
    var tag = document.createElement('script');
    tag.src = "https://www.youtube.com/player_api";
    var firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
    return {
        onLoad: function(params){
            loaded.done(_.bind(setUpPlayer, this, params));
        }
    }
});

