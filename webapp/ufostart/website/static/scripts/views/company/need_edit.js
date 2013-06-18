define(["tools/ajax", "form"], function(ajax, Form){
    var View = Backbone.View.extend({
        events : {
            'keyup .data-input': 'dataEntry'
        }

        , initialize:function(opts){
            this.$form = new Form({el: opts.el});

            var $inputs = this.$el.find(".data-input")
                , $targets = this.$el.find(".data-target");
            this.$total = $inputs.filter('.value');
            this.$ratio = $inputs.filter('.ratio');
            this.$cash = $targets.filter('.cash');
            this.$equity = $targets.filter('.equity');

            this.cashCur = this.$cash.data('currencySymbol');
            this.equityCur = this.$equity.data('currencySymbol');

            this.dataEntry();

        }
        , dataEntry : function(e){
            var total = parseInt(this.$total.val(), 10)
                , ratio = parseInt(this.$ratio.val(), 10) / 100;
            if(isNaN(total) || isNaN(ratio)){
                this.$cash.html( this.cashCur + '---' );
                this.$equity.html( this.equityCur + '---' );
            } else {
                this.$cash.html( this.cashCur + ((1-ratio)*total).toFixed(0) );
                this.$cash.next("input").val( ((1-ratio)*total).toFixed(0) );

                this.$equity.html( this.equityCur + (ratio*total).toFixed(0) );
                this.$equity.next("input").val( (ratio*total).toFixed(0) );
            }
        }
        , render: function(){

        }
    });
    return View;
});