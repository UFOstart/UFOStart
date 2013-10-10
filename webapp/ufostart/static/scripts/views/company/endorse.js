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
    , EndorsementView = Backbone.View.extend({
        initialize:function(opts){
            this.setElement($(opts.template({model: this.model}).trim()));
        }
    })
    , View = Backbone.View.extend({
        events: {
        }
        , initialize:function(opts){
            var preset = [];
            this.needToken = this.$el.data('entityId');

            this.$results = this.$(".results");
            this.template = _.template(this.$(".endorsement-template").html());
            opts.watch.on({'selected': _.bind(this.onSelected, this)});
            this.model = new Endorsements();


            this.$results.find(".search-result-item").each(function(idx, elem){
                preset.push({id: $(elem).data("entityId")});
            });
            this.model.addOrUpdate(preset, {silent: true});

            this.listenTo(this.model, "add", this.addOne, this);
        }
        , onSelected: function(e, model){
            var view = this;
            this.model.addOrUpdate(model.attributes, {preserve: true});

            ajax.submitPrefixed({url: '/web/round/endorse'
                , data:{
                    token: this.needToken
                    , Endorsement: {
                        endorserSlug: hnc.getUserSlug()
                        , endorserToken: hnc.getUserToken()
                        , endorseeName: model.getName()
                        , endorseeHeadline: model.getPosition()
                        , endorseeLinkedinId: model.id
                        , endorseePicture: model.getPicture()
                    }
                }
                , success:function(data, status, xhr){}
                , error: function(err){
                    view.model.get(model.id).destroy();
                }
            })
        }
        , addOne: function(model){
            this.$results.trigger("newnodes", (new EndorsementView({model:model, template: this.template}).$el).appendTo(this.$results));
        }
    });
    return View;
});