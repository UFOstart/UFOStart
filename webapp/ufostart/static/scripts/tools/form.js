define([], function(){
  var validate = function(params){
        var form = params.root.is("form.form-validated") ? params.root : params.root.find("form.form-validated")
        , btnValue
        , opts = _.extend({
                errorClass: "help-inline"
                , errorElement: "span"
                , validClass:"valid"
                , onkeyup: false
                , highlight: function (element, errorClass, validClass) {
                    $(element).closest(".control-group").addClass("has-error").removeClass(validClass).removeClass(validClass);
                }
                , unhighlight: function (element, errorClass, validClass) {
                    var name = $(element).attr("name");
                    if(name && $(element).closest(".controls").find('[for='+name.replace(/\./g,"\\.")+']').filter("[generated]").remove().length)
                        $(element).closest(".control-group").removeClass("has-error").addClass(validClass);
                }
                , errorPlacement: function(error, element) {
                    if(element.parent().find("."+this.errorClass+"[generated=true]").length)return;
                    if (element.parent().is(".input-append"))
                        error.insertAfter(element.parent());
                    else
                        error.appendTo(element.closest(".controls,.control-group"));
                }
            }, params)
            , validator = $(form).validate(opts)
            , view = this;

        $(form).find("input[type=reset], button[type=reset]").click(function(e) {
            view.resetForm(form);
        });
//        saving submit button value for later submitting
        var saveBtn = function(btn){
            form.data("submitButton", {value: btn.value, name: btn.name});
        };
        $(form).find("button[type=submit][value]").on({click: function(e){saveBtn(this)}, keyup: function(){
            if(e.keycode == 13 || e.keyCode == 32){saveBtn(this)}
        }});
        $(form).find("[data-validation-url]").each(function(idx, elem){
            var $elem = $(elem);
            $elem.rules("add", {remote: $elem.data("validationUrl")});
        });

        if(params.repeatables){
            form.on({
                "click": removeRow
                , "keyup": removeRow
            }, ".remove-link")
            form.on({
                "click" :addRow
                , "keyup": addRow
            }, ".add-more-link");

        }


        if(params.focus){
            form.find("input,select,textarea").filter(":visible").first().focus();
        }
        return validator;
    }
    , resetForm= function(form){
        var $f = $(form)
        $f.validate().resetForm();
        $f.find(".has-error").removeClass("has-error");
        $f.find("[generated]").remove();
    }
    , showFormEncodeErrors = function($form, errors, values){
        var formId = $form.find("[name=type]").val(), validator = $form.validate();
        for(var k in errors){
            if(/--repetitions$/.test(k))delete errors[k];
            else { // formencode sends null errors into the list, needs stripping for jquery validate
              if(_.isEmpty(errors[k]))delete errors[k];
            }
        }
        validator.showErrors(errors);
        for(var attr in values){
          $form.find("#"+formId+"\\."+attr).val(values[attr]);
        }
        $form.find(".error-hidden").hide(); // show any additional hints/elems
        $form.find(".error-shown").fadeIn(); // show any additional hints/elems
    }

    , wrapperSelector = '[data-closure="form"], .form-validated'
    , templateSelector = "[data-sequence], .form-validated"
    , removeLink = '<a class="remove-link link close">&times;</a>'

    , addRow = function(e){
        if((!e.keyCode || e.keyCode == 13)){
            var $target = $(e.target)
                , templ = $target.closest(wrapperSelector).find(templateSelector).last()
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
            if(!new_node.find(".remove-link").length) new_node.append(removeLink);
            new_node.find(".numbering").html(new_position+1);

            if($target.data("appendFirst")){
                templ.closest(wrapperSelector).prepend("<hr/>").prepend(new_node);
                $target.hide();
            } else {
                templ.after(new_node);
            }
            new_node.trigger("change");

            new_node.find("[generated]").remove();
            new_node.find(".error").removeClass("error");
            new_node.find(".valid").removeClass("valid");
        }
    }
    , removeRow = function(e){
        if(!e.keyCode|| e.keyCode == 13){
            var $target = $(e.target), $embeddedForm = $target.closest(templateSelector)
                , siblings = $embeddedForm.siblings(templateSelector)
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


  return {validate: validate, resetForm: resetForm, showFormEncodeErrors: showFormEncodeErrors};
});