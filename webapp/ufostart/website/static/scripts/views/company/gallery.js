define(["tools/ajax"], function(ajax){
    var View = Backbone.View.extend({
        initialize:function(opts){

        }
        , render: function(){

        }
    })
    , init = function(opts, target){
        opts.el = target;
        return new View()
    };
    return {init: init, View: View};
});
