require(["tools/ajax", "misc"], function(ajax, misc){
    var options = window.__options__, root = window;

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

    if(_.isEmpty(root.hnc)){
        var hnc = new HNC(options);


        var socials = _.keys(options.socials), i= 0;
        if(socials.length){
            hnc.socials = {};
            require(_.map(socials, function(e){return "networks/"+e}), function(){
                var name, lib;
                for(i;i<socials.length;i++){
                    name = socials[i];
                    lib = arguments[i];
                    hnc[name] = new lib.AuthHandler(options.socials[name], options.user, '/user/login/social');
                }
            });
        }
//      global login form (pull down style, if it exists, connect it up
        var form = $("#login-pull-down-form");
        if(!options.user.token && form.length){
            ajax.ifyForm({root:form});
        }

        root.hnc = hnc;
    }
});
