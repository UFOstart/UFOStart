define(["tools/hash", "tools/ajax"], function(hashlib, ajax){
    var
    defaultRollback = function () {
        document.body.style.cursor = "";
    }
    , AuthHandler = function (options, user, apiUrl) { /* app_id, fbRootNode */
        var _t = this, loadDefs, loginDefs, e;
        this.user = user || {};
        this.apiUrl = apiUrl;
        this.whenLoaded = $.Deferred();
        this.whenLoggedIn = $.Deferred();
        this.initialize && this.initialize(options);
    };
    _.extend(AuthHandler.prototype, Backbone.Events, {
        isLoggedIn : function () {
            return false
        }
        , backendLogin: function(profile, params){
            var _t = this, rollback = defaultRollback, success = params.success || function(){window.location.reload()}
            , data = {
                type:"linkedin"
                , id: profile.id
                , picture: profile.pictureUrl || "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
                , name: profile.firstName +" "+profile.lastName
                , email: profile.emailAddress
            };

            params = params || {};
            params.complete = params.complete || rollback;
            params.success = function(resp, xhr, status){
                if(resp.success == true && resp.user){
                    _t.user = resp.user;
                    success&&success(resp);
                    _t.whenLoggedIn.resolve(_t.user);
                }
            };
            ajax.submit(_.extend({
                url:_t.apiUrl
                , data: {'profile':data}
            }, params))
        }
        , onLoaded: function(IN){
            var _t = this
            , handler = function(e){

                if(!e.keyCode|| e.keyCode==13){
                    var $t = $(e.currentTarget), $bodyTarget = $("body").add($t)
                        , rollback = function () {
                            $bodyTarget.css("cursor", "");
                            $t.siblings(".loading").addClass("hidden");
                            $t.removeClass("hidden");
                        };
                    $bodyTarget.css("cursor", "wait");
                    if ($t.siblings(".loading").removeClass("hidden").length > 0) {
                        $t.addClass("hidden");
                    }

                    IN.User.authorize(function(){
                        IN.API.Profile("me")
                            .fields(["id", "firstName", "lastName", "pictureUrl", "email-address"])
                            .result(function(result) {
                                _t.backendLogin(result.values[0], {success: function(resp, status, xhr){
                                    if(resp.success === true){
                                        window.location.href = $t.prop("href");
                                    } else {
                                        rollback();
                                    }
                                }
                                , error: rollback});
                            })
                            .error(function(err) {
                                rollback()
                            });
                    });

                    e.stopPropagation();
                    e.preventDefault();
                    return false;

                }
            };

            $(document).on({click: handler, keyup: handler}, ".linkedin-connect");
        }
        , initialize: function(options){
            var _t = this, cbName = '__linkedinCBV__';
            window[cbName] = function(){
                _t.whenLoaded.resolve(IN);
                _t.onLoaded(IN);
                if(IN.User.isAuthorized()){
                      IN.API.Profile("me").result(function(result){
                        _t.whenLoggedIn.resolve(result.values[0]);
                      });
                } else {
                    IN.Event.on(IN, "auth", function(){
                        if(IN.User.isAuthorized()){
                          IN.API.Profile("me").result(function(result){
                            _t.whenLoggedIn.resolve(result.values[0]);
                          });
                        }
                    });
                }
            };
            $.getScript("//platform.linkedin.com/in.js?async=true", function() {
                IN.init({
                    apiKey:options.appId
                    , authorize: true
                    , credentials_cookie: true
                    , onLoad: cbName
                });
            });
        }
    });
    return {AuthHandler: AuthHandler};
});


