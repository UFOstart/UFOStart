define(["tools/ajax", "form"], function(ajax, Form){
    var View = Backbone.View.extend({
        initialize:function(opts){
            this.$form = new Form({el: opts.el});
        }
        , render: function(){

        }
    });
    return View;
});