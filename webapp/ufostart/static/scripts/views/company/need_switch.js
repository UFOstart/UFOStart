define(["tools/ajax", "libs/abstractsearch", "text!templates/need_searchresult.html"], function(ajax, AbstractSearch, search_result_template){
    var
    getRec = hnc.getRecursive
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
            this.preExisting = opts.preExisting;
        }
        , idAttribute:'slug'
        , parse: function(resp){
            var c = this, result = getRec(resp, this.apiResult);
            _.each(result, function(elem){
                elem.alreadyExists = !!~c.preExisting.indexOf(elem.slug);
            });
            return result;
        }
    })
    , TypeAheadSearch = AbstractSearch.extend({
        template:_.template(search_result_template)
        , buildQuery: function(query){
            return query?{type: this.options.apiType, name:query}:null;
        }
    })
    , PlainTypeAhead = Backbone.View.extend({
        initialize: function(opts){
            var view = this;
            this.$filter = this.$(".query");
            this.current = new PlainResult({name: this.$filter.val()});
            this.search = this.getSearch(opts);
            this.search.on('selected', function(term){
                view.search.hide();
                view.$filter.val(term.getSearchLabel());
                view.switch_general_need(term);
                view.current = term;
            });
        }
        , switch_general_need: function(term){
            var view = this, path = location.pathname.split('/');
            path[3] = term.id;
            path = path.join("/");

            if(term.get('alreadyExists') || !(window.history && history.pushState)){
                location.pathname = path;
            } else {
                window.history.pushState(null, term.get('name'), path);
                $("[data-entity-property]").each(function(idx, elem){
                   var $e = $(elem), attr = $e.data('entityProperty')
                    $e.html(term.get(attr));
                });
                view.$el.closest(".form-validated").find(".tagsearch-container.js-form-widget").each(function(idx, elem){
                   var $e = $(elem), attr = $e.data('apiResult');
                   $e.find(".query").trigger("replaceModels", [term.get(attr)]);
                });
            }
        }
        , getSearch: function(opts){
            return new TypeAheadSearch({
                el:this.$el
                , suppressExtra: true
                , model: new PlainSearchResult([], {apiResult: opts.apiResult, preExisting: this.$el.closest(".form-validated").data("roundTasks")})
                , apiType: opts.apiType
                , searchUrl: opts.apiUrl
            });
        }
    })
    , widgets = []
    , init = function(opts){
        widgets.push(new PlainTypeAhead(opts));
    };
    return {init: init, PlainTypeAhead: PlainTypeAhead};
});