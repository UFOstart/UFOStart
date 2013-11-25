define(["tools/ajax", "form"], function(ajax, Form){
    var View = Backbone.View.extend({
        events : {
            'keyup .data-input': 'dataEntry'
        }

        , initialize:function(opts){
            this.$form = new Form({el: opts.el});

            var $inputs = this.$el.find(".data-input")
                , $targets = this.$el.find(".data-target");

            this.$cash = $inputs.filter('.cash');
            this.$equity = $inputs.filter('.equity');
            this.$total = $targets.filter('.total');

            this.cashCur = this.$total.data('currencySymbol');
            this.dataEntry(null);
        }
        , dataEntry : function(e){
            var cash = parseInt(this.$cash.val(), 10)
                , equity = parseInt(this.$equity.val(), 10);
            if(isNaN(cash) || isNaN(equity)){
                this.$total.html( this.cashCur + '---' );
            } else {
                this.$total.html( hnc.formatNum(this.cashCur + (cash + equity)) );
            }
        }
        , render: function(){

        }
    });
    return View;
});