define(["tools/ajax"], function(ajax){
    var
    SCOPE = "email", MAX_SCOPE = "email"
    , defaultRollback = function () {
        document.body.style.cursor = "";
    }
    , AuthHandler = function (options, user, apiUrl) {
        var _t = this, sse;
        this.user = user || {};
        this.apiUrl = apiUrl;
        this.fbUserID = this.user.facebookId;
        this.fbToken = this.user.accessToken || "NOTOKEN";
        this.fbFriends = null;
        this.fbPerms = {};
        this.require_refresh = false;
        this.whenLoaded = $.Deferred();
        this.whenLoggedIn = $.Deferred();
        this.initialize && this.initialize(options);
        this.failedLogins = store.get("FAILED_LOGINS") || {};
    };
    _.extend(AuthHandler.prototype, Backbone.Events, {
        isLoggedIn : function () {
            return FB.getAccessToken() && this.user.accessToken;
        }
        , hasAuthedFB: function () {
            return FB.getAccessToken();
        }
        , setUser : function(user){
            this.user = user;
        }
        , getPicFromUserID : function (id, type) {
            if(type)
                return "//graph.facebook.com/" + id + "/picture?type="+type;
            else
                return "//graph.facebook.com/" + id + "/picture";
        }
        , getMyPicture : function (id) {
            return root.resolve_resource(this.user.picture)||"//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
        }
        , delReqs: function(type){
            FB.api("/me/apprequests", function(requests){
                _.each(requests.data, function(req){
                    if(req.data === type){
                        FB.api(req.id, 'delete', function(response) {});
                    }
                });
            })
        }
        , getPermissions : function () {
            var _t = this;
            this.whenLoggedIn.done(function () {
                FB.api("/me/permissions", function (response) {
                    if (_.isArray(response.data)) _t.fbPerms = response.data[0];
                });
            });
            return _t.fbPerms;
        }
        , getFriends : function (cb, ctxt) {
            var _t = this;
            if (!_t.fbFriends) {
                FB.api("/me/friends", { fields: 'name,id,gender,picture' }, function (response) {
                    _t.fbFriends = response.data;
                    if (cb) cb.call(ctxt, _t.fbFriends)
                });
            }
            else if (cb) cb.call(ctxt, _t.fbFriends);
        }
        , removeRequest: function( fullReqId , callback, context){
            FB.api( '/'+fullReqId, 'DELETE', function(response) {
                if(callback)callback.apply(context, arguments);
            });
        }
        , sendUserToServer : function (profile, authResponse, params) {
            params = params||{};
            var success = params.success, _t = this
            , data = {
                type: "facebook"
                , id:profile.id
                , accessToken:authResponse.accessToken
                , picture : _t.getPicFromUserID(profile.id)
                , email: profile.email
                , name: profile.name
            };
            params.success = function(resp, xhr, status){
                if(resp.success == true && resp.user){
                    _t.user = resp.user;
                    success&&success(resp);
                    _t.whenLoggedIn.resolve(_t.user);
                }
            };

            ajax.submit(_.extend({
                url:this.apiUrl
                , data: {'profile':data}
            }, params))
        }
        , validateProfile: function(profile, rollback){
            if(!_.isEmpty(profile.error)){
                require(["tools/messaging"], function(messaging){
                    messaging.addError({message: 'We do not have permission to access your facebook profile.'});
                    rollback();
                });
                return false;
            } else if (_.isEmpty(profile) || !profile.name) {
                rollback();
                return false;
            }
            return true;
        }
        , login: function(authResponse, params){
            var _t = this, rollback = defaultRollback;
            params = params || {};
            FB.api("/me", function (profile) {
                if(_t.validateProfile(profile, rollback)){
                    params.complete = params.complete || rollback;
                    params.success = params.success || function(){window.location.reload()};
                    _t.sendUserToServer(profile, authResponse || FB.getAuthResponse(), params);
                }
            });
        }
        , refreshUser : function () {
            var _t = this;
            this.whenLoggedIn.done(function () {
                _t.require_refresh = true;
                FB.api("/me", function (profile) {
                    profile.picture = _t.getPicFromUserID(profile.id);
                    _t.sendUserToServer(profile, FB.getAuthResponse(), { success: function (resp, status, xhr) { _t.require_refresh = false; } });
                });
            });
        }
        , initialize: function(options){
            var _t = this;
            if(!options.connect)return;
            if (options.require_permissions) { this.getPermissions() }
            if (!! ~(window.location.hash.indexOf("refresh"))) { this.refreshUser(); }


            var handler = {
                click: function (click_event) {
                    var $t = $(click_event.currentTarget), $bodyTarget = $("body").add($t)
                        , rollback = function () {
                            $bodyTarget.css("cursor", "");
                            $t.siblings(".loading").addClass("hidden");
                            $t.removeClass("hidden");
                        };
                    $bodyTarget.css("cursor", "wait");
                    if ($t.siblings(".loading").removeClass("hidden").length > 0) {
                        $t.addClass("hidden");
                    }

                    if ($t.hasClass("logout")) {

                        FB.logout(function (response) { });

                    } else if ($t.hasClass("share")) {
                        var opts = $t.data();
                        FB.ui(
                            {
                                method: 'feed'
                                , display: 'popup'
                                , name: opts.title
                                , link: window.location.href
                                , picture: opts.picture
                                , description: opts.message
                            },
                            function(response) {
                                if (response && response.post_id) {
                                    $.post("/user/fb/hasShared", response, function(){if($t.data("doReload"))window.location.reload(true);});
                                } else {
                                    // Post was not published.
                                }
                                rollback();
                            }
                        );
                    } else if ($t.hasClass("disconnect")){
                        FB.api("/me/permissions", "delete", function(){
                            window.location.href = $t.data("href");
                        });
                        click_event.preventDefault();
                        click_event.stopPropagation();
                        return false;
                    } else {
                        click_event.preventDefault();
                        click_event.stopPropagation();

                        FB.login(function (response) {
                            var aR = response.authResponse;
                            if (aR) {
                                _t.login(aR, {success: function(resp, status, xhr){
                                    if(resp.success === true){
                                        window.location.href = $t.prop("href");
                                    } else {
                                    rollback();
                                    }
                                }});
                            } else {
                                rollback();
                            }
                        }, { scope: SCOPE });
                        return false;
                    }
                }
            };
            _t.whenLoaded.done(function(){
                $(document).on(handler, ".fbconnect");
            });

            window.fbAsyncInit = function () {
                var channelUrl = document.location.protocol + "//" + document.location.host + "/static/channel.html";
                FB.Event.subscribe('auth.statusChange', function (response) {
                    if (!response.authResponse && _t.user.facebookId){
                        root.send({ url: "/user/fb/logout", success: function (resp, status, xhr) { window.location.href = resp.location } });
                    }
                });
                FB._https = true;
                FB.init({ appId: options.appId, status: true, cookie: true, xfbml: true, channelUrl: channelUrl, frictionlessRequests : true });
                FB.getLoginStatus(function(response){
                    _t.whenLoaded.resolve(response);
                    if(response.authResponse && _t.user.token)
                        if (_t.user.facebookId != response.authResponse.userID) {
                            if(!_t.failedLogins[_t.user.token+"|"+response.authResponse.userID])
                                _t.login(response.authResponse, {success:function(resp, status, xhr){
                                    defaultRollback();
                                    if(resp.success === false){
                                        _t.failedLogins[_t.user.token+"|"+response.authResponse.userID] = true;
                                        store.set("FAILED_LOGINS", _t.failedLogins);
                                    }
                                }});
                        } else {
                            if (_t.fbToken != response.authResponse.accessToken) {
                                root.send({ url: "/user/fb/token/refresh", data: { accessToken: response.authResponse.accessToken, facebookId:response.authResponse.userID }, success: function (resp, status, xhr) { if (resp.isLogin) _t.login(response.authResponse); } });
                            }
                            _t.fbToken = response.authResponse.accessToken
                            _t.user.accessToken = _t.fbToken;
                            _t.whenLoggedIn.resolve(_t.user);
                        }
                    else
                        _t.whenLoggedIn.reject();
                });
            };
            e = document.createElement("script");
            e.src = "https://connect.facebook.net/en_US/all.js";
            e.async = true;
            document.getElementById(options.fbRootNode || "fb-root").appendChild(e);
        }
    });
    return {AuthHandler:function(){}};
});