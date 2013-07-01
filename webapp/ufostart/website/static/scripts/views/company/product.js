define(["tools/ajax"], function(ajax){
    var View = Backbone.View.extend({
        events: {
            'click .remove': "removeNeed"
            , 'keyup .remove': "removeNeed"
        }
        , initialize:function(opts){

        }
        , removeNeed: function(e){
            if(!e.keyCode||e.keyCode == 13){
                var $t = $(e.currentTarget)
                    , $need = $t.closest($t.data("target"))
                    , roundToken = this.$el.data('entityId');
                if(confirm("Do you really want to delete this offer?")){
                    ajax.submitPrefixed({url: '/web/round/removeneed'
                        , data: {token:roundToken, Needs: [{token: $need.data("entityId")}]}
                        , success: function(resp, status, xhr){
                            $need.remove();
                            messaging.addSuccess({message:"Need successfully removed!"})
                        }
                    });
                }
            }
        }
        , render: function(){

        }
    });
    return View;
});