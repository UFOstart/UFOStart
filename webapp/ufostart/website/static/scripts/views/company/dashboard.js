define(["tools/messaging", "tools/ajax"], function(messaging, ajax){
    var View = Backbone.View.extend({
        events: {
            'click .remove': "removeNeed"
            , 'keyup .remove': "removeNeed"

            , 'click .workflow-link': "highlightTarget"
            , 'keyup .workflow-link': "highlightTarget"
        }
        , initialize:function(opts){
            var lengths = [], max, min;
        }

        , highlightTarget: function(e){
            if(!e.keyCode||e.keyCode == 13){
                var $t = $($(e.currentTarget).attr("href")).closest(".highlight-target");
                $t.addClass("highlighted");
                setTimeout(function(){
                    $t.removeClass("highlighted");
                }, 1000);
            }
        }
        , removeNeed: function(e){
            if(!e.keyCode||e.keyCode == 13){
                var $t = $(e.currentTarget)
                    , $need = $t.closest($t.data("target"))
                    , roundToken = this.$el.data('entityId');
                if(confirm("Do you really want to delete this need?")){
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
