define(["tools/ajax"], function(ajax){
    var View = Backbone.View.extend({

        events : {}
        , initialize:function(opts){
            var evt = window.Modernizr.touch?'touchstart':'click', view = this;
            this.events[evt+" .add-remove-btn"] = "addRemove";
            this.events[evt+" .in-library"] = "addRemove";
            this.events[evt+" .addNeedsBtn"] = "doAddNeeds";

            this.$(".form-validated").each(function(idx, elem){
                ajax.ifyForm({root: elem})
            });


            var f = function(e){
                if(!e.keyCode|| e.keyCode == 13){
                    view.switchPanes();
                }
            };
            $(document).on({ click:f , keyup:f}, ".switchLibrary");

            this.$library = this.$(".task-library");
            this.$tasks = this.$(".tasks-used");
        }
        , addRemove : function(e){
            var $el = $(e.currentTarget)
                , $need = $el.closest(".single-need")
                , taskId = $need.data("entityId")
                , $category = $need.closest(".category-task-list")
                , catId = $category.data("entityId");

            if($el.hasClass("in-library")){
                if($need.hasClass("in-use"))return;
                $need.toggleClass("marked-for-use");
            } else if($el.hasClass("remove")){
                this.$library
                    .find(".category-task-list")
                    .filter("[data-entity-id="+catId+"]")
                        .children()
                        .filter("[data-entity-id="+taskId+"]")
                        .removeClass("in-use");
                $need.remove();
            }
        }
        , doAddNeeds: function(e){
            var view = this;
            this.$library.find(".category-task-list").each(function(idx, libCat){
                var catId = $(libCat).data("entityId")
                    , $targetCat = view.$tasks
                            .find(".category-task-list")
                            .filter("[data-entity-id="+catId+"]");
                $(libCat).find(".marked-for-use").each(function(idx, libNeed){
                    $(libNeed).addClass("in-use").removeClass("marked-for-use");
                    $targetCat.append($(libNeed).clone().removeClass("in-library"));
                });
            });
            this.switchPanes();
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
        , switchPanes: function(){
            this.$library.toggleClass("hide")
            this.$tasks.toggleClass("hide")
        }
        , render: function(){

        }
    });
    return View;
});