define(["tools/hash"
        , "tools/ajax"
        , "networks/linkedin/models"]
    , function(hashlib, ajax, models){

    var defaultRollback = function () {
        document.body.style.cursor = "";
    }
    , AuthHandler = function (options, user, apiUrl) { /* app_id, fbRootNode */
        var _t = this, loadDefs, loginDefs, e;
        this.prefix = '/net/li';
        this.user = user || {};
        this.apiUrl = apiUrl;
        this.whenLoaded = $.Deferred();
        this.whenLoggedIn = $.Deferred();
        this.initialize && this.initialize(options);
    };
    _.extend(AuthHandler.prototype, Backbone.Events, {
        widgets: {
            'ContactSearch': 'networks/linkedin/contacts'
            ,'SendMessage': 'networks/linkedin/message'
        }
        , isLoggedIn : function () {
            return this.options.accessToken
        }
        , isMe : function (token) {
            return this.options.accessToken == token
        }
        , api: function(path, cb, ctxt){
            $.get(this.getApiUrl(path), function(data, status, xhr){
                cb.apply(ctxt, [data, status, xhr]);
            });
        }
        , getApiUrl: function(path){
            return this.prefix + path+ '?oauth2_access_token='+this.options.accessToken
        }
        , getContact: function(id){
            if(!this.profiles[id]){
                this.profiles[id] = $.Deferred();
                this.api('/people/id='+id+':(first-name,last-name,api-standard-profile-request)', function(data, xhr, status){
                    this.profiles[id].resolve(data);
                }, this);
            }
            return this.profiles[id];
        }
        , getContacts: function(){
            var view = this;
            if(!this.contactDef){
                this.contactDef = $.Deferred();
                this.contacts = new models.Contacts();
                this.api('/people/~/connections', function(data, xhr, status){
                    var result = [];
                    this.contacts.addOrUpdate(data.values);
                    this.contactDef.resolve(this.contacts);
                }, this);
            }
            return this.contactDef;
        }
        , initialize: function(options){
            var _t = this;
            this.options = options;
            this.profiles = {};
            $(".linkedin-widget").each(function(idx, el){
                var $el = $(el), module = _t.widgets[$el.data('widget')];
                require([module], function(init){
                    init(_.extend({$el:$el, auth : _t}, options));
                });
            });
        }
    });
    return {AuthHandler: AuthHandler};
});


