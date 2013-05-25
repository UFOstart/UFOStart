define(["tools/ajax"], function(ajax){
    var View = Backbone.View.extend({
        events: {"click .need-btn": "addRemove"}
        , initialize:function(opts){
            this.$(".form-validated").each(function(idx, elem){
                ajax.ifyForm({root: elem})
            });
            $(".need-detail").qtip({
                content: {
                    title: function(api) {
                        return $(this).text()
                    }
                    , text: function(api) {
                        return $(this).data("description")
                    }
                }
                , style: {
                    tip: {
                        width: 20,
                        height: 20
                    }
                }
                , position: {
                    my: 'bottom center', at: 'top center'
                }
                , hide:"unfocus"
            });
        }
        , addRemove : function(e){
            var $el = $(e.target);
            if($el.hasClass("add")){
                this.sortedInsert(this.$(".needs-list.in-use"), $el.closest(".single-need").detach());
                $el.removeClass("add").addClass("remove").html("×");
            } else if($el.hasClass("remove")){
                this.sortedInsert(this.$(".needs-list.library"), $el.closest(".single-need").detach());
                $el.removeClass("remove").addClass("add").html("+");
            }
        }
        , sortedInsert: function(root, el){
            var i=0 , tmp
                , sortIndex = el.data("entitySort")
                , nodes = root.children()
                , len = nodes.length
                , inserted = false;
            for(;i<len;i++){
                tmp = nodes.eq(i);
                if(tmp.data("entitySort")>sortIndex){
                    tmp.before(el);
                    inserted = true;
                    break;
                }
            }
            if(!inserted){
              root.append(el);
            }
            el.addClass("inserted")
        }
        , render: function(){

        }
    });
    return View;
});