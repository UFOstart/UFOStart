define(["tools/ajax"], function(ajax){

    var View = Backbone.View.extend({
        events: {
            'click .remove': 'removePic'
            , 'keyup .remove': 'removePic'

        }
        , initialize:function(opts){
            var view = this
                , uploader = this.$(".file-picker-upload")
                , picture_template = _.template(this.$(".picture-template").html())
                , backupText = uploader.siblings(".info").html();

           filepicker.makeDropPane(uploader[0], {
                multiple: true
                , dragEnter: function() {
                    uploader.addClass("drop-target");
                }
                , dragLeave: function() {
                    uploader.removeClass("drop-target");
                }
                , onSuccess: function(fpfiles) {
                   uploader.removeClass("empty");
                   _.each(fpfiles, function(file){
                       uploader.append(picture_template({pic: file, field_name: opts.fieldName}));
                   })
                   uploader.siblings(".info").html(backupText)
                }
                , onError: function(type, message) {
                    uploader.after().text('('+type+') '+ message);
                }
                , onProgress: function(percentage) {
                    uploader.siblings(".info").html('Uploading ('+percentage.toFixed(2)+'%)');
                }
            });
        }
        , removePic: function(e){
            if(!e.keyCode || e.keyCode == 13){
                $(e.target).closest(".picture").remove();
                if(!uploader.children(".picture").length)uploader.addClass("empty");
            }
        }
    })
    , init = function(opts){
        return new View(opts);
    };
    return {init: init, View: View};
});