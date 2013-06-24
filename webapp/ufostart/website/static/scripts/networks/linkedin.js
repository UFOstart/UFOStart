define(["tools/hash", "tools/ajax"], function(hashlib, ajax){
    var
    defaultRollback = function () {
        document.body.style.cursor = "";
    }
    , Contact = ajax.Model.extend({
        getPicture: function(){
            return this.get('pictureUrl')
        }
        , getName: function(){
            return this.get('firstName') + ' ' + this.get('lastName');
        }
        , getPosition: function(){
            return this.get("headline")
        }
        , matches: function(query){
            return !!~this.get("firstName").toLowerCase().indexOf(query) || !!~this.get("lastName").toLowerCase().indexOf(query);
        }
    })
    , Contacts = ajax.Collection.extend({model: Contact})


    , numberMap = {48:0,  49:1, 50:2, 51:3, 52:4, 53:5, 54:6, 55:7, 56:8, 57:9, 96:0, 97:1, 98:2, 99:3, 100:4, 101:5, 102:6, 103:7, 104:8, 105:9}
    , AbstractSearch = Backbone.View.extend({
            PAGE_SIZE: 5
            , initialize: function(opts){
                this.id = hashlib.UUID();
                this.template = this.options.template;

                var view = this;
                this.blacklist = opts.blacklist;
                this.doSearch = opts.doSearch;
                this.$searchBox = this.$el.find(".query");
                this.$searchBoxC = this.$el.find(".search-field");
                this.$searchBox
                    .on('keydown', $.proxy(this.keypress, this))
                    .on('keyup',    $.proxy(this.keyup, this));

                this.listenTo(this.model, "updated", this.onSearchResult, this);
                this.listenTo(this.model, "emptied", this.onSearchResult, this);
                this.$resultNode = this.$('.results');
                this.$resultNode.on({'mouseenter' : $.proxy(this.mouseenter, this),
                        'click':_.bind(this.disAmbiguateEvent, this)}, '.search-result-item');
                this.setLoading();
            }
            , prev: function(){
                var curnode = this.$resultNode.find(".active");
                if(curnode.length){
                    curnode.prev().addClass("active").next().removeClass("active");
                } else {
                    this.$resultNode.find(".search-result-item").last().addClass("active");
                }
            }
            , next: function(){
                var curnode = this.$resultNode.find(".active");
                if(curnode.length){
                    curnode.next().addClass("active").prev().removeClass("active");
                } else {
                    this.$resultNode.find(".search-result-item").first().addClass("active");
                }
            }
            , first: function(){
                this.$resultNode.find(".active").removeClass('active');
                this.$resultNode.find(".search-result-item").first().addClass("active");
            }
            , last: function(){
                this.$resultNode.find(".active").removeClass('active');
                this.$resultNode.find(".search-result-item").last().addClass("active");
            }

            , keyup : function(e){
                switch(e.keyCode) {
                    case 40: // down arrow
                    case 38: // up arrow
                        break;
                    case 13: // enter
                        this.disAmbiguateEvent(e);
                        break;
                    case 27: // escape
                        this.$searchBox.val('')
                        break;
                    case 33:
                        this.first();
                        break;
                    case 34:
                        this.last();
                        break;
                    default:
                        if(this.otherKey(e))this.doSearch(e.target.value);
                }
                e.stopPropagation();
                e.preventDefault();
            }
            , otherKey: function(e){
                return true;
            }
            , keypress: function (e) {
                switch(e.keyCode) {
                    case 13: // enter
                    case 27: // escape
                        e.preventDefault()
                        break
                    case 38: // up arrow
                        if (e.type != 'keydown') break
                        e.preventDefault()
                        this.prev()
                        break
                    case 40: // down arrow
                        if (e.type != 'keydown') break
                        e.preventDefault()
                        this.next()
                        break
                    case 48: case 49 :case 50 :case 51 :case 52 :case 53 :case 54 :case 55 :case 56 :case 57 :
                    case 96: case 97 :case 98 :case 99 :case 100:case 101:case 102:case 103:case 104:case 105:
                    if(e.ctrlKey||e.metaKey){
                        var number = numberMap[e.keyCode];
                        this.$resultNode.find(".search-result-item.active").removeClass("active");
                        this.$resultNode.find(".search-result-item[shortcut="+number+"]").addClass("active");
                        if(number == 0){
                            this._extraItemSelected()
                        } else {
                            this.disAmbiguateEvent(e)
                        }
                        e.stopPropagation();
                        e.preventDefault();
                    }
                    break
                }
                e.stopPropagation()
            }
            , disAmbiguateEvent: function(e){
                var res = this.$resultNode.find(".active")
                    , res = res.length?res:this.$resultNode.find(".search-result-item").first();
                if(e.shiftKey){
                    this._metaSelect(res);
                } else {
                    this._select(res);
                }
            }
            , _extraItemSelected: function(){
                this.trigger("extraItemSelected", this.$searchBox.val().trim());
            }
            , _metaSelect: function(item){
                var id = item.data("entityId"), model = this.model.get(id);
                if(model)this.trigger("metaSelected", model);
                else this.trigger("unknownterm:metaSelected", this.$searchBox.val().trim());
            }
            , _select: function(item){
                if(item.hasClass("create-new-entity")){
                    this._extraItemSelected();
                } else {
                    var id = item.attr("data-entity-id"), model = this.model.get(id);
                    if(model){
                        this.$el.trigger("selected", model)
                        this.blacklist.push(model.id);
                        item.remove();
                        model.destroy();
                        this.model.addOrUpdate(this.backlog.unshift(), {preserve:true});
                    }
                    else this.trigger("unknownterm:selected", this.$searchBox.val().trim());
                }
            }
            , onSearchResult: function(collection){
                if(collection){
                    var all = collection.filter(function(m){return !~this.blacklist.indexOf(m.id)}, this)
                        , models = all.slice(0, this.PAGE_SIZE);
                    this.backlog = all.slice(this.PAGE_SIZE);

                    this.$resultNode.html('');
                    _.each(models, function(model){
                        this.$resultNode.append(this.template({model:model}));
                    }, this);
                }
            }
            , setLoading: function(){
                this.$resultNode.html(window.__options__.loadingHtml);
            }
            , mouseenter: function(e){
                this.$resultNode.find(".active").removeClass("active");
                $(e.target).closest(".search-result-item").addClass("active");
            }
        })


    , LinkedContactSearch = Backbone.View.extend({
        initialize: function(opts){
            var view = this;
            this.model = new Contacts();
            this.search = new AbstractSearch({
                el: this.$el
                , model: new Contacts()
                , template: _.template(this.$("script.contact-template").html())
                , blacklist: []
                , doSearch: function(query){
                    var result = [];
                    if(query){
                        var queryId = view.queryId = hashlib.UUID();
                        _.each(view.model.models, function(model){
                            if(model.matches(query))result.push(model.attributes);
                        });
                    } else {
                        view.model.each(function(m){result.push(m.attributes)});
                    }
                    this.model.addOrUpdate(result);
                }
            });
            opts.auth.api('/people/~/connections', function(data, xhr, status){
                var result = [];
                view.model.addOrUpdate(data.values);
                view.model.each(function(m){result.push(m.attributes)});
                view.search.model.addOrUpdate(result);
            }, this);
        }
    })
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
            'LinkedContactSearch': LinkedContactSearch
        }
        , isLoggedIn : function () {
            return this.options.accessToken
        }
        , api: function(path, cb, ctxt){
            $.get(this.prefix + path+ '?oauth2_access_token='+this.options.accessToken, function(data, status, xhr){
                cb.apply(ctxt, [data, status, xhr]);
            });
        }
        , initialize: function(options){
            var _t = this;
            this.options = options;
            $(".linkedin-widget").each(function(idx, el){
                var $el = $(el), widget = _t.widgets[$el.data('widget')];
                new widget(_.extend({el:$el, auth : _t}, options));
            })
        }
    });
    return {AuthHandler: AuthHandler};
});


