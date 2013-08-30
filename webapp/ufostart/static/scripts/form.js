define(['tools/ajax'], function(ajax){
    jQuery.validator.addMethod("greaterThan",
    function(value, element, params) {
        if (!/Invalid|NaN/.test(new Date(value))) {
            return new Date(value) > new Date($(params).val());
        }
        return isNaN(value) && isNaN($(params).val())
            || (Number(value) > Number($(params).val()));
    },'Must be greater than {0}.');
    var View = Backbone.View.extend({
        events: {
            "click .remove-link": "removeRow"
            , "keyup .remove-link": "removeRow"
            , "click .add-more-link" :"addRow"
            , "keyup .add-more-link": "addRow"
        }
        , removeLink: '<a class="remove-link link close">&times;</a>'
        , initialize: function(opts){
            var view = this;
            var valid_params = {form: this.$el};

            this.widgets = [];
            this.setupWidgets(this.$el);

            ajax.ifyForm(_.extend(valid_params, opts), opts.validatorOpts);

            this.wrapperSelector = opts.wrapperSelector || '[data-closure="form"], .form-validated';
            this.templateSelector = opts.templateSelector || "[data-sequence], .form-validated";

            this.$el.find(this.wrapperSelector).each(function(idx, elem){
                var required = $(elem).data("required") === true;
                $(elem).find(view.templateSelector).each(function(idx, elem){
                    if(idx>0)$(elem).append(view.removeLink);
                });
            });
        }
        , setupWidgets : function(el, validPromise){
            el.find(".js-form-widget").each(function(idx, elem){
                var data = _.extend({el:elem}, $(elem).data());
                require([data.module], function(V){V[data['moduleMethod']||'init'](data, validPromise)});
            });
            el.find(".js-selectmenu").each(function(idx, elem){
                var $el = $(elem);
                $el.on({
                        'chosen:ready': function(e, c){
                            c.chosen.container.attr('generated', true)
                        }
                    }).chosen({width:"100%"});
            });
            el.find(".js-datepicker").each(function(idx, elem){
                var $el = $(elem);
                if(!$el.data('datepicker')) $el.removeClass("hasDatepicker");
                $el.datepicker( $el.data() );
                $el.siblings(".datepicker-opener").click(function(){$el.datepicker('show')});
            });
        }
        , addRow : function(e){
            if((!e.keyCode || e.keyCode == 13)){
                var $target = $(e.target)
                    , $root = $target.closest(this.wrapperSelector)
                    , templ = $root.find(this.templateSelector).last()
                    , new_node = templ.clone()
                    , new_position = parseInt(templ.data("sequence"), 10) + 1
                    , inc = function(elem, attr){
                        if(elem.attr(attr))
                            elem.attr(attr, elem.attr(attr).replace(/-[0-9]+\./g, "-"+new_position+"."))
                    };
                new_node.find("input,select,textarea").each(function(index, elem){
                    elem = $(elem);
                    inc(elem, "id");
                    inc(elem, "name");
                    if(!elem.is('[type=checkbox],.typehead-token,[readonly]'))elem.val("");
                });
                new_node.removeAttr("data-sequence").attr("data-sequence", new_position);
                if(!new_node.find(".remove-link").length) new_node.prepend(this.removeLink);
                new_node.find(".numbering").html(new_position+1);
                if($target.data('addClass')){new_node.addClass($target.data('addClass'));}
                if($target.data("appendFirst")){
                    $root.prepend("<hr/>").prepend(new_node);
                    $target.hide();
                } else {
                    $root.find($target.data('appendTarget')).append(new_node);
                }
                new_node.trigger("change");

                new_node.find("[generated]").remove();
                new_node.find(".error").removeClass("error");
                new_node.find(".valid").removeClass("valid");

                this.setupWidgets(new_node);
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        }
        , removeRow : function(e){
            if(!e.keyCode|| e.keyCode == 13){
                var $target = $(e.target), $embeddedForm = $target.closest(this.templateSelector)
                    , siblings = $embeddedForm.siblings(this.templateSelector)
                    , idx = function(elem, pos){
                        _.each(['id','name'], function(attr){
                            if(elem.attr(attr))
                                elem.attr(attr, elem.attr(attr).replace(/-[0-9]+\./g, "-"+pos+"."))
                        });
                    };
                $embeddedForm.trigger("change");
                $embeddedForm.remove();
                siblings.each(function(i, elem){
                    $(elem).attr('data-sequence', i).find("input,select,textarea").each(function(k, e){
                            idx($(e), i);
                    });
                    $(elem).find(".numbering").html(i+1);
                });

            }
        }
    });
    return View;
});