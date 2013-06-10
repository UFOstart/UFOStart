define(["tools/ajax"], function(ajax){
    var View = Backbone.View.extend({
        events: {
            'click .remove': "removeNeed"
            , 'keyup .remove': "removeNeed"
        }
        , initialize:function(opts){
            var lengths = [], max, min;

            this.$(".js-need-card-list").each(function(idx, elem){
                lengths.push($(elem).height());
            });

            max = lengths.indexOf(Math.max.apply(Math, lengths));
            min = lengths.indexOf(Math.min.apply(Math, lengths));

            this.$(".js-need-card-list").eq(min).append(
                this.$(".js-need-card-list").eq(max).children('.need-card[data-entity-id]').last().detach()
            );
        }

        , removeNeed: function(e){
            if(!e.keyCode|| e.keyCode == 13){
                var $t = $(e.currentTarget)
                    , $need = $t.closest($t.data("target"))
                    , roundToken = this.$el.data('entityId');
                ajax.submitPrefixed({url: '/web/round/removeneed'
                    , data: {token:roundToken, Needs: [{token: $need.data("entityId")}]}
                    , success: function(resp, status, xhr){
                        $need.remove()
                    }
                });
            }
        }
        , render: function(){

        }
    });
    return View;
});
