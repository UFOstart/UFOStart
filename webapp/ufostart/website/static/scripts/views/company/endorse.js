define(["tools/ajax"], function(ajax){
    var

    Endorsement = ajax.Model.extend({
        getPicture: function(){
            return this.get('pictureUrl')
        }
        , getName: function(){
            return this.get('firstName') + ' ' + this.get('lastName');
        }
        , getPosition: function(){
            return this.get("headline")
        }
    })
    , Endorsements = ajax.Collection.extend({
        model : Endorsement
    })
    , View = Backbone.View.extend({
        events: {
        }
        , initialize:function(opts){
            this.needToken = this.$el.data('entityId');

            this.$results = this.$(".results");
            this.template = _.template(this.$(".endorsement-template").html());
            opts.watch.on({'selected': _.bind(this.onSelected, this)});
            this.model = new Endorsements();
            this.listenTo(this.model, "updated", this.render, this);
        }
        , onSelected: function(e, model){
            var view = this;
            this.model.addOrUpdate(model.attributes, {preserve: true});

            ajax.submitPrefixed({url: '/web/round/endorse'
                , data:{
                    token: this.needToken
                    , Endorsement: {
                        endorserToken: hnc.getUserToken()
                        , endorseeName: model.getName()
                        , endorseeHeadline: model.getPosition()
                        , endorseeLinkedinId: model.id
                        , endorseePicture: model.getPicture()
                    }
                }
                , success:function(data, status, xhr){
                    console.log(data)
                }
                , error: function(err){
                      view.model.get(model.id).destroy();
                }
            })
        }
        , render: function(){
            var html = [];
            this.model.each(function(model){
                html.push(this.template({model:model}))
            }, this);
            this.$results.html(html.join(''));
        }
    });
    return View;
});