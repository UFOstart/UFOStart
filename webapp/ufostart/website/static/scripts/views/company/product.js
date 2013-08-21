define(["tools/messaging", "tools/ajax"], function(messaging, ajax){
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
                    , $target = $t.closest($t.data("target"))
                    , token = $target.data('entityId');
                if(confirm("Do you really want to delete this offer?")){
                    ajax.submitPrefixed({url: '/web/product/offerDelete'
                        , data: {token:token}
                        , success: function(resp, status, xhr){
                            $target.remove();
                            messaging.addSuccess({message:"Offer successfully removed!"})
                        }
                    });
                }
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        }
        , render: function(){

        }
    });
    return View;
});