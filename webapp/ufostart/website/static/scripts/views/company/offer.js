define(["tools/ajax"], function(ajax){
    var View = Backbone.View.extend({
        events: {
            "click .remove-link": "removeRow"
            , "keyup .remove-link": "removeRow"
            , "click .save-offer-btn" :"addRow"
            , "keyup .save-offer-btn": "addRow"
        }
        , initialize:function(opts){
            var view = this;
            this.template = _.template(this.$(".template").html());
            this.$target = this.$(opts.appendTarget);
            this.$form = this.$(".single-offer-form");
            if(this.$target.children().length){
                this.$form.find("input,select,textarea")
                    .each(function(index, elem){$(elem).addClass("super-valid");})
            }
        }
        , addRow : function(e){
            if((!e.keyCode || e.keyCode == 13)){
                var $target = $(e.target)
                    , $root = $target.closest(this.wrapperSelector)
                    , new_position = this.$target.children().length
                    , values = {}, $el
                    , inc = function(attr) {
                            return attr.replace(/-[0-9]+\./g, "-"+new_position+".")
                    }, valid = true;
                this.$form.find("input,select,textarea").each(function(idx, elem){valid = valid && $(elem).valid();});
                if(!valid)return;
                this.$form.find("input,select,textarea").each(function(index, elem){
                    $el = $(elem);
                    values[_.last($el.prop('name').split("."))] = {value: $el.val(),name:inc($el.prop('name'))};
                    $el.val('').addClass("super-valid");
                });
                this.$target.append('<div class="'+this.options.addClass+'">'+ this.template(values)+'</div>');
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        }
        , removeRow : function(e) {
            $(e.target).closest("."+this.options.addClass).remove();
            this.reIndex();
        }
        , reIndex: function(){
            var idx = function(elem, pos){
                _.each(['id','name'], function(attr){
                    if(elem.attr(attr))
                        elem.attr(attr, elem.attr(attr).replace(/-[0-9]+\./g, "-"+pos+"."))
                });
            };
            if(this.$target.children().each(function(i, elem){
                $(elem).find("input,select,textarea").each(function(k, e){
                    idx($(e), i);
                });
                $(elem).find(".numbering").html(i+1);
            }).length == 0){
                this.$form.find(".super-valid").removeClass("super-valid");
            }
        }
    })

    , init = function(data, validPromise){
        return new View(data);
    };
    return {init:init, View:View};
});