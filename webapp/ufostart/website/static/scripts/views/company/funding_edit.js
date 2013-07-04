define(["tools/ajax", "form"], function(ajax, Form){
    var View = Backbone.View.extend({
        events : {
            'keyup .data-input': 'dataEntry'
        }

        , initialize:function(opts){
            this.$form = new Form({el: opts.el});

            var $inputs = this.$el.find(".data-input")
                , $targets = this.$el.find(".data-target");

            this.$valuation = $inputs.filter('.valuation');
            this.$amount = $inputs.filter('.amount');
            this.$equity = $targets.filter('.equity');
            this.dataEntry(null);
        }
        , dataEntry : function(e){
            var valuation = parseInt(this.$valuation.val(), 10)
                , amount = parseInt(this.$amount.val(), 10);
            if(isNaN(valuation) || isNaN(amount)){
                this.$equity.html( '---' );
            } else {
                this.$equity.html( ((amount/valuation)*100).toFixed(2)+"%" );
            }
        }
        , render: function(){

        }
    });
    return View;
});