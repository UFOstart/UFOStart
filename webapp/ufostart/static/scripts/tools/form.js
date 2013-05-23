define([], function(){
  var validate = function(params){
        var form = params.root.is("form.form-validated") ? params.root : params.root.find("form.form-validated");
        var opts = _.extend({
            errors: {
                classHandler: function ( elem, isRadioOrCheckbox ) {
                    return $( elem ).closest(".control-group");
                }
            }
        }, params);
        return $(form).parsley(opts);
    }
    , resetForm = function(form){
        var $f = $(form);
        console.warn("NOT IMPLEMENTED PARSLEY VALIDATION YET");
    }
    , showFormEncodeErrors = function($form, errors, values){
        var formId = $form.find("[name=type]").val();
        for(var k in errors){
            if(/--repetitions$/.test(k))delete errors[k];
            else { // formencode sends null errors into the list, needs stripping for jquery validate
              if(_.isEmpty(errors[k]))delete errors[k];
            }
        }
        for(var attr in errors){
            $form.find("#"+attr.replace(".", "\\.")).parsley("addError", {'server': errors[attr]});
        }
        for(var attr in values){
            $form.find("#"+formId+"\\."+attr).val(values[attr]);
        }
        $form.find(".error-hidden").hide(); // show any additional hints/elems
        $form.find(".error-shown").fadeIn(); // show any additional hints/elems
  }
  return {validate: validate, resetForm: resetForm, showFormEncodeErrors: showFormEncodeErrors};
});