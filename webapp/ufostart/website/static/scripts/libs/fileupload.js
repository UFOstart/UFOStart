define(["tools/ajax"], function(ajax){
    var View = Backbone.View.extend({
        picture_template : _.template('<img src="{{ pic.url }}"/><input type="hidden" name="{{ field_name }}" value="{{ pic.url }}"/>')
        , initialize:function(opts){
            this.uploader = this.$(".file-picker-upload");
            var view = this, uploader = this.uploader;

            filepicker.makeDropPane(uploader[0], {
                dragEnter: function() {
                    uploader.html("Drop to upload").css({
                        'backgroundColor': "rgba(0,0,0,.1)"
                    });
                },
                dragLeave: function() {
                    uploader.html("Drop files here").css({
                        'backgroundColor': "rgba(0,0,0,0)"
                    });
                },
                onSuccess: function(fpfiles) {
                    uploader.text("Done!");
                    var file = fpfiles[0];
                    uploader.html(view.picture_template({field_name: view.uploader.data("fieldName"), pic: fpfiles[0]}));
                },
                onError: function(type, message) {
                    uploader.after().text('('+type+') '+ message);
                },
                onProgress: function(percentage) {
                    uploader.text("Uploading ("+percentage+"%)");
                }
            });
        }
        , render: function(){

        }
    });
    return View;
});