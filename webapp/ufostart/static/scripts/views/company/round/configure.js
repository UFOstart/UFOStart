define(["tools/ajax"], function(ajax){
    var


    Expert = Backbone.Model.extend({
        getIntroPicture: function(){
            return this.get('introPicture') || "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
        }
        , getIntroName: function(){
            return this.get("introFirstName") +" "+ this.get("introLastName")
        }
        , getExpertPicture: function(){
            return this.get('picture') || "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
        }
        , getExpertName: function(){
            return this.get("firstName") +" "+ this.get("lastName")
        }
    })


    , View = Backbone.View.extend({
        template: _.template($("#expert-template").html())
        , initialize:function(opts){
            $(".need-detail,.information-btn").qtip({
                content: {
                    title: function(api) {
                        return $(this).text()
                    }
                    , text: function(api) {
                        return $(this).data("description")
                    }
                }
                , style: {
                    tip: {
                        width: 20,
                        height: 20
                    }
                }
                , position: {
                    my: 'bottom center', at: 'top center'
                    , viewport: $(window)
                }
                , show:"click"
                , hide:"unfocus"
            });
        }
        , render: function(token){
            var _t= this, elems = {};
            this.$(".round-need-setup.expert.loading").each(function(idx, elem){
                var need = $(elem).data("need");
                elems[need] = $(elem);
            });
            if(!_.isEmpty(elems)){
                ajax.submitPrefixed({url: '/web/round', data: {token: token}, success: function(resp, status, xhr){
                    _.each(resp.Round.Needs, function(need){
                        var key = need.key, $el = elems[key];
                        if(key && $el){
                            $el.removeClass("loading");
                            if(!_.isEmpty(need.Expert)){

                                $el.html(_t.template({model: new Expert(need.Expert)}));
                            } else {
                                $el.remove();
                            }

                        }
                    })
                }});
            }
        }
    });
    return View;
});