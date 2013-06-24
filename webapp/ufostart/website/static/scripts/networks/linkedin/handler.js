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
        , api: function(path, cb, ctxt){
            $.get(this.prefix + path+ '?oauth2_access_token='+this.options.accessToken, function(data, status, xhr){
                cb.apply(ctxt, [data, status, xhr]);
            });
        }
        , getContacts: function(cb, ctxt){
            var view = this;
            if(this.contacts)cb.call(ctxt, this.contacts);
            else {
                this.contacts = new models.Contacts();
                this.api('/people/~/connections', function(data, xhr, status){
                    var result = [];
                    this.contacts.addOrUpdate(data.values);
                    cb.call(ctxt, this.contacts);
                }, this);
            }
        }
        , initialize: function(options){
            var _t = this;
            this.options = options;
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


