require(["tools/ajax"], function(ajax){

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

        , getUserSlug: function(){
            return this.options.user.slug;
        }
        , getUserToken: function(){
            return this.options.user.token;
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
        , months: ['January', 'February', "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        , formatDate: function(d){
            return this.months[d.getUTCMonth()] +' '+ d.getUTCDay()+ ', '+d.getUTCFullYear()
        }
        , formatNum: function(x) {
            return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        }
    });

    if(_.isEmpty(root.hnc)){
        var hnc = new HNC(options);

        var socials = _.keys(options.socials), i= 0;
        if(socials.length){
            hnc.socials = {};
            require(_.map(socials, function(e){return "networks/"+e+"/handler"}), function(){
                var name, lib;
                for(i;i<socials.length;i++){
                    name = socials[i];
                    lib = arguments[i];
                    hnc[name] = new lib.AuthHandler(options.socials[name], options.user[name], '/user/login/social');
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



    // Bootstrap Touch Devices DropDown Fix START
    $('body')
    .on('touchstart.dropdown', '.dropdown-menu', function (e) { e.stopPropagation(); })
    .on('touchstart.dropdown', '.dropdown-submenu', function (e) { e.preventDefault(); })
    // Bootstrap Form inside dropdown prevent close
    .on("click", '.dropdown input, .dropdown label', function(e){e.stopPropagation();});
    // Bootstrap Touch Devices DropDown Fix END

    // TOGGLEABLE FLY OUTS
    $(document).on({click: function(e){
        var $t = $(e.currentTarget)
            , data = $t.data()
            , cls = data.toggleClass
            , target = (data.toggleTarget?$t.closest(data.toggleTarget):$t).toggleClass(cls);
        if(data.toggleText){
            if(target.hasClass(cls)){
                $t.data("backupText", $t.html());
                $t.html(data.toggleText);
            } else {
                $t.html(data.backupText);
            }
        }
    }}, "[data-toggle-class]");
    // hiding server generated messages
    var mCont = $("#message-container");
    if(mCont.length){
        mCont.on({click: function(e){
            var $t = $(this).closest(".alert");
            if(!$t.siblings(".alert").length)
                mCont.hide();
            $t.remove();
        }}, '[data-dismiss="alert"]');
        $(document).on({scroll: function(e){
                var messageTop = mCont.position().top;
                mCont[$(window).scrollTop()>messageTop?"addClass":"removeClass"]("fixed")
        }});
    }
    // IE placeholder plugin
    var NATIVE_PLACEHOLDER = !!("placeholder" in document.createElement( "input" ));
    if(!NATIVE_PLACEHOLDER){
        $('input[placeholder], textarea[placeholder]').placeholder();
    }

    var tLoaded = $.Deferred();
    $(".hover-container").one({
        mouseover : function(e){
            var data = $(e.currentTarget).data();
            if(tLoaded.state() != 'resolved')
                    require(["text!templates/profile.html"], function(templ){tLoaded.resolve(_.template(templ)); return {};});
            ajax.submitPrefixed({
                url:"/web/user/mini"
                , data: {slug: data.entityId}
                , success: function(resp, status, xhr){
                    var user = resp.User;
                    if(user){
                        tLoaded.done(function(templ){
                            $(e.currentTarget).append(
                                templ({
                                    link: '/'+user.slug
                                    , startupValue: '$' + hnc.formatNum(user.startupValue)
                                    , user: user
                                })
                            )
                        });
                    }
                }
            });
        }
    }).find("a").prop('href', null);
    return {NATIVE_PLACEHOLDER:NATIVE_PLACEHOLDER, hnc: root.hnc}
});
