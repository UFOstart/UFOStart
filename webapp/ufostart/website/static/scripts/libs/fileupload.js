define(["tools/ajax"], function(ajax){
    var View = Backbone.View.extend({
        initialize:function(opts){
            this.uploader = this.$(".file-picker-upload");
            var view = this, uploader = this.uploader, picture_template = _.template(this.$(".picture-template").html());
            filepicker.makeDropPane(uploader[0], {
                dragEnter: function() {
                    uploader.addClass("drop-target");
                },
                dragLeave: function() {
                    uploader.removeClass("drop-target");
                },
                onSuccess: function(fpfiles) {
                    uploader.html('<div class="info">Done!</div>').removeClass("empty");
                    var file = fpfiles[0];
                    uploader.html(picture_template({field_name: view.uploader.data("fieldName"), pic: fpfiles[0]}));
                },
                onError: function(type, message) {
                    uploader.after().text('('+type+') '+ message);
                },
                onProgress: function(percentage) {
                    uploader.html('<div class="info">Uploading ('+percentage+'%)');
                }
            });
        }
        , render: function(){

        }
    });
    return View;
});