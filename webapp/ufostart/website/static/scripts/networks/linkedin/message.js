define(["tools/ajax"], function(ajax){
    var View = Backbone.View.extend({
        initialize:function(opts){

        }
        , render: function(){

        }
        , addHandler: function($el){
            $el.on({"click": _.bind(this.onClick, this)});
        }
        , onClick: function(e){
            var id = $(e.currentTarget).data("entityId");
            this.options.auth.getContacts(function(collection){
                console.log(collection.get(id));
            })
        }
    })
    , instance = null;
    return function(opts){
        if(!instance)instance = new View(opts);
        instance.addHandler(opts.$el);
    };
});