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
            this.$results = this.$(".box-content");
            this.template = _.template(this.$(".endorsement-template").html());
            opts.watch.on({'selected': _.bind(this.onSelected, this)});
            this.model = new Endorsements();
            this.listenTo(this.model, "updated", this.render, this);
        }
        , onSelected: function(e, model){
            this.model.addOrUpdate(model.attributes, {preserve: true});
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