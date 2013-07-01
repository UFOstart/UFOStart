define(["tools/messaging", "tools/ajax", "libs/tachymeter"], function(messaging, ajax, Tachymeter){
    var



    PledgeModel = ajax.Model.extend({
        key : "Pledge"
        , getObject: function(){

        }
    })

    , TYPE_MAP = {
        'PLEDGE': PledgeModel
    }

    , Activity = ajax.Model.extend({
        getObject: function(){
            var cls = TYPE_MAP[this.get('type')];
            return new cls(this.get(cls.key))
        }
    })
    , ActivityStream = ajax.Collection.extend({model : Activity})

    , ActivityView = Backbone.View.extend({
        template: _.template("<div>Event: {{ model.get('type') }}</div>")
        , initialize: function(opts){
            this.$el.html(this.template({model: this.model}));
        }
    })

    , View = Backbone.View.extend({
        events: {
            'click .remove': "removeNeed"
            , 'keyup .remove': "removeNeed"

            , 'click .workflow-link': "highlightTarget"
            , 'keyup .workflow-link': "highlightTarget"
        }
        , initialize:function(opts){
            var lengths = [], max, min, view = this;
            if(opts.tacho) this.tacho = new Tachymeter(opts.tacho);


            this.$activity = this.$(".activity-stream");
            this.model = new ActivityStream();
            this.listenTo(this.model, "add", this.addOne, this);
            ajax.submitPrefixed({
                url: "/web/round/activity"
                , data:{token: this.$activity.data('entityId')}
                , success: function(resp, status, xhr){
                    view.$activity.html('');
                    view.model.addOrUpdate(resp.Activity.Item);
                }
            })
        }

        , addOne: function(model){
            this.$activity.prepend(new ActivityView({model:model}).$el).removeClass("empty");
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
