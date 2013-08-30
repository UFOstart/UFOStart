define([], function(){
  var validate = function(params){
        var form = params.root.is("form.form-validated") ? params.root : params.root.find("form.form-validated")
        , btnValue
        , opts = _.extend({
                errorClass: "help-inline"
                , errorElement: "span"
                , validClass:"valid"
                , onkeyup: false
                , ignore: ".ignore"
                , highlight: function (element, errorClass, validClass) {
                    $(element).closest(".form-group").addClass("has-error").removeClass(validClass).removeClass(validClass);
                }
                , unhighlight: function (element, errorClass, validClass) {
                    var name = $(element).attr("name");
                    if(name && $(element).closest(".controls").find('[for='+name.replace(/\./g,"\\.")+']').filter("[generated]").remove().length)
                        $(element).closest(".form-group").removeClass("has-error").addClass(validClass);
                }
                , errorPlacement: function(error, element) {
                    if(element.parent().find("."+this.errorClass+"[generated=true]").length)return;
                    error.attr("generated", true);
                    if (element.parent().is(".input-append"))
                        error.insertAfter(element.parent());
                    else
                        error.appendTo(element.closest(".controls,.form-group"));
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



  return {validate: validate, resetForm: resetForm, showFormEncodeErrors: showFormEncodeErrors};
});