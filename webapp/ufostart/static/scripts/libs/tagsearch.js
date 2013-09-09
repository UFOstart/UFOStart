define(["tools/hash", "tools/ajax", "libs/abstractsearch"], function(hashlib, ajax, AbstractSearch){
    var
        getRec = hnc.getRecursive
        , re = /-[0-9]+(\.[^-.]+)?$/
        , PlainResult = ajax.Model.extend({
            idAttribute:'name'
            , getSearchLabel: function(){
                return this.id;
            }
        })
        , PlainSearchResult = ajax.Collection.extend({
            model:PlainResult
            , initialize: function(models, opts){
                this.apiResult = opts.apiResult;
            }
            , idAttribute:'name'
            , parse: function(resp){
                return getRec(resp, this.apiResult);
            }
        })
        , TagModels = Backbone.Collection.extend({
            model: PlainResult
        })
        , TagView = Backbone.View.extend({
            events: {'click .close':"destroy"}
            , initialize: function(){
                this.listenTo(this.model, "destroy", this.remove, this);
            }
            , destroy: function(e){
                this.remove();
                this.model.destroy();
            }
            , render: function(opts){
                // same logic implemented as in template, see formencode-lists "form.key-1.name"
                this.setElement(opts.template({model:this.model, name: opts.prefix+"-"+opts.pos, pos:opts.pos}));
                return this.$el;
            }
        })
        , TagSearch = AbstractSearch.extend({
            buildQuery: function(query){
                var extra = this.options.queryExtra;
                return query?_.extend({'name':query}, extra):null;
            }
            , delKey: function(e){
                return true;
            }
            , otherKey: function(e){
                if(e.keyCode == 8 && !this.$searchBox.val()){
                    this.trigger("delKey");
                    return false;
                } else if (e.keyCode == 188 && this.$searchBox.val()){
                    this.$searchBox.val(this.$searchBox.val().replace(",", ""));
                    this.trigger("unknownterm:selected", this.$searchBox.val().trim());
                    return false;
                } else return true;
            }
        })
        , TagSearchView = Backbone.View.extend({
            MODEL_CLS: TagModels
            , initialize: function(opts){
                var view = this;
                this.$input = this.$(".query");

                this.required = this.$input.prop('required') || this.$input.is(".required");
                this.$input.removeClass("required").prop('required', false);
                if(this.required){
                    var requiredMethod = 'required-'+hashlib.UUID()
                        , min = this.$input.addClass(requiredMethod).data('requiredMin');
                    jQuery.validator.addMethod(requiredMethod, function (value, element) {
                        return view.model.length>=min;
                    }, "Please add at least "+min+" tags");
                }

                this.$result = this.$(".current-tags");
                this.tagTemplate = _.template(this.$(".tag-template").html().trim());

                this.model = new this.MODEL_CLS();
                this.model.on("add", this.addOne, this);
                this.model.on("destroy", this.reIndex, this);

                this.search = this.getSearch(opts);
                this.search.on('selected', function(term){
                    view.search.hide();
                    view.model.add(term);
                    view.$input.val("");
                });
                this.search.on("delKey", function(e){
                    var id = view.$result.children().last().find("input").val()
                        , model = view.model.get(id);
                        if (model) model.destroy();
                });

                if(opts.onCreate){
                    require([opts.onCreate], function(View){
                        var v = View.init(function(model){
                            view.model.add(model);
                            view.$input.val("");
                        });
                        view.search.on('extraItemSelected unknownterm:selected unknownterm:metaSelected', v.onCreate);
                        view.$input.trigger("change");
                    });
                } else {
                    this.search.on('extraItemSelected unknownterm:selected unknownterm:metaSelected', function(termname){
                        if(termname){
                            view.search.hide();
                            view.model.add({name: termname});
                            view.$input.val("");
                            view.$input.trigger("change");
                        }
                    });
                }
                var seed = this.$result.find(".label").find("input");
                if(seed.length)
                    this.$(".label").each(function(idx, el){
                        var model = new PlainResult({name: $(el).find("input[name]").val()});
                        view.model.add(model, {silent:true});
                        new TagView({model: model,el:el});
                    });
                this.adjustInput();
            }
            , addOne: function(model){
                this.$result.append((new TagView({model: model})).render({template: this.tagTemplate, prefix: this.options.prefix, pos: this.model.length - 1}));
                this.adjustInput();
                this.search.rePosition();
            }
            , adjustInput: function(){
                var w = (this.$(".search-field").width() - this.$result.width() -21);
                this.$input.css({width: w>100?w+'px':'100%'})
            }
            , reIndex: function(){
                this.$result.find("input[name]").each(function(idx, elem){
                    var elem = $(elem);
                    elem.attr('name', elem.attr('name').replace(re, "-"+(idx)+"$1"));
                });
                this.$input.trigger("change");
                this.adjustInput();
            }
            , getSearch: function(opts){
                return new TagSearch({
                    el:this.$el
                    , suppressExtra: opts.apiAllowNew
                    , model: new PlainSearchResult([], {apiResult: opts.apiResult})
                    , searchUrl: opts.apiUrl
                    , queryExtra: opts.queryExtra
                });
            }
        })
        , widgets = []
        , init = function(opts){
            widgets.push(new TagSearchView(opts));
        };
    return {init: init, TagSearch: TagSearchView};
});