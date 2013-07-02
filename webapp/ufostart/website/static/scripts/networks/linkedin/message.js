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
            var id = $(e.currentTarget).data("entityId")
                , msg = {
                      "recipients": {
                         "values": [{
                           "person": {
                                "_path": "/people/"+id
                             }
                           }]
                         },
                       "subject": "JSON POST from JSAPI",
                       "body": "Some long message!!!!"
                     };
              ajax.submit(
                  {url:this.options.auth.getApiUrl("/people/~/mailbox")
                    , data: msg
                    , success: function(){
                      console.log(arguments);
                  }
              })
        }
    })
    , instance = null;
    return function(opts){
        if(!instance)instance = new View(opts);
        instance.addHandler(opts.$el);
    };
});