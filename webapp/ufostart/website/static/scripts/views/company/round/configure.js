define(["tools/ajax"], function(ajax){
    var View = Backbone.View.extend({
        initialize:function(opts){
            $(".need-detail,.information-btn").qtip({
                content: {
                    title: function(api) {
                        return $(this).text()
                    }
                    , text: function(api) {
                        return $(this).data("description")
                    }
                }
                , style: {
                    tip: {
                        width: 20,
                        height: 20
                    }
                }
                , position: {
                    my: 'bottom center', at: 'top center'
                }
                , show:"click"
                , hide:"unfocus"
            });
        }
        , render: function(){

        }
    });
    return View;
});