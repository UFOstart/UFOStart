define([], function(){
  var validate = function(params){
        console.warn("NOT IMPLEMENTED PARSLEY VALIDATION YET");
        var form = params.root.is("form.form-validated") ? params.root : params.root.find("form.form-validated")
        var opts = _.extend({}, params)
        return $(form).parsley(opts);
    }
    , resetForm = function(form){
        var $f = $(form);
        console.warn("NOT IMPLEMENTED PARSLEY VALIDATION YET");
    }
    , showFormEncodeErrors = function($form, errors){
        var formId = $form.find("[name=type]").val();
        for(var k in errors){
            if(/--repetitions$/.test(k))delete errors[k];
            else { // formencode sends null errors into the list, needs stripping for jquery validate
              if(_.isEmpty(errors[k]))delete errors[k];
            }
        }
        validator.showErrors(errors);
        for(var attr in resp.values){
            $form.find("#"+formId+"\\."+attr).val(resp.values[attr]);
        }
        $form.find(".error-hidden").hide(); // show any additional hints/elems
        $form.find(".error-shown").fadeIn(); // show any additional hints/elems
  }
  return {validate: validate, resetForm: resetForm, showFormEncodeErrors: showFormEncodeErrors};
});