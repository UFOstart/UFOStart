define(["misc", "fb"], function(misc, fb){
    _.templateSettings = {
        interpolate : /\{\{ (.+?) \}\}/g
        , evaluate: /\{% (.+?) %\}/g
    };

    // IE<9
    if(typeof String.prototype.trim !== 'function') {
        String.prototype.trim = function() {
            return this.replace(/^\s+|\s+$/g, '');
        }
    }

    var _isTouch = !!('ontouchstart' in window && '__proto__' in {})
        , LOCALE = $('html').attr('lang')
        , HNC = function(options){
            this.options = options;
            this.initialize.apply(this, arguments);
            var ctor = function(){}
                , inherits = function(parent, protoProps, staticProps) {
                    var child;
                    if (protoProps && protoProps.hasOwnProperty('constructor')) {
                        child = protoProps.constructor;
                    } else {
                        child = function(){ parent.apply(this, arguments); };
                    }
                    ctor.prototype = parent.prototype;
                    child.prototype = new ctor();
                    if (protoProps) _.extend(child.prototype, protoProps);
                    if (staticProps) _.extend(child, staticProps);
                    child.prototype.constructor = child;
                    child.__super__ = parent.prototype;
                    return child;
                };
            this.extend = function (protoProps, classProps) {
                var child = inherits(this, protoProps, classProps);
                child.extend = this.extend;
                return child;
            };
        };

    _.extend(HNC.prototype, Backbone.Events, {
        initialize: function(options){
            this.LOCALE = options.LOCALE || LOCALE
        }
        , rld: function(){
            window.location.href = "//" + window.location.host + window.location.pathname + '?' + window.location.search;
        }
        , getRecursive: function(obj, key, defaults){
            var tmp = obj, keys = key.split("."), i= 0, len = keys.length;
            for (;i<len;i++) {
                if(tmp.hasOwnProperty(keys[i])){
                    tmp = tmp[keys[i]];
                } else {
                    return defaults;
                }
            }
            return tmp;
        }
        , apiUrl: function (path){
            return '/api/'+this.api_version+path;
        }
        , isPicturePath: function(path){
            return /(jpe?g|png|gif|bmp|tiff?|tga)$/.test(path.toLowerCase())
        }
        , validate : function(params){
            var form = params.root.is("form.form-validated") ? params.root : params.root.find("form.form-validated")
            var opts = _.extend({
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

            $(form).find("[data-validation-url]").each(function(idx, elem){
                var $elem = $(elem);
                $elem.rules("add", {remote: $elem.data("validationUrl")});
            });

            if(params.focus){
                form.find("input,select,textarea").filter(":visible").first().focus();
            }
            return validator;
        }
        , resetForm: function(form){
            var $f = $(form)
            $f.validate().resetForm();
            $f.find(".has-error").removeClass("has-error");
            $f.find("[generated]").remove();
        }
        , zeroFill: function( number, width ) {
            width -= number.toString().length;
            if ( width > 0 )
            {
                return new Array( width + (/\./.test( number ) ? 2 : 1) ).join( '0' ) + number;
            }
            return number + ""; // always return a string
        }
        , support : {
            clickEvent : _isTouch?"touchstart":"click"
            , touchStartEvent: _isTouch?"touchstart":"mousedown"
        }
        , translate: function(s){return s;}
        // LOCALE AWARE
        , parseDate: function(input, format) {
            format = format || 'yyyy-mm-ddTHH:MM:SS'; // default format
            var parts = input.match(/(\d+)/g),
                i = 0, fmt = {};
            // extract date-part indexes from the format
            format.replace(/(yyyy|dd|mm|HH|MM|SS)/g, function(part) { fmt[part] = i++; });
            return new Date(parts[fmt.yyyy], parts[fmt.mm]-1, parts[fmt.dd], parts[fmt.HH]||0, parts[fmt.MM]||0, parts[fmt.SS]||0);
        }
    });

    var setup = function(root, opts){
        root.hnc = new HNC(opts);
        root.hnc.fb = fb.setup(hnc, opts);
    };
    return {setup:setup};
});
