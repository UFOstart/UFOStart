define([], function(){
    var CARD_CONFIG = [
        {type:'American Express', code:'amex', prefix: [34, 37], length: 15, enabled : true}
        , {type:'Diners Club', code:'dc', prefix:[300,301,302,303,304,305,36], length:14, enabled: false}
        , {type:'Carte Blanche', code:'cb', prefix:[38], length:14, enabled: false}
        , {type:'Discover', code:'dc', prefix:[6011],length:16, enabled: false}
        , {type:'EnRoute', code:'enr', prefix:[2014, 2149], length: 15, enabled: false}
        , {type:'JCB', code:'jcb', prefix: [3], length:16, enabled: false}
        , {type:'JCB', code:'jcb', prefix: [2131, 1800], length: 15, enabled: false}
        , {type:'Master Card', code:'mc', prefix: [51, 52, 53, 54, 55], length: 16, enabled: true}
        , {type:'Visa', code:'visa', prefix:[4], length: 16, enabled: true}
    ]
    , cleanUp = function(cardNo){
        return cardNo.replace(/[_ -]*/g, '');
    }
    , calcLuhn = function(Luhn){
        var sum = 0, i;
        for (i=0; i<Luhn.length; i++ )
        {
            sum += parseInt(Luhn.substring(i,i+1), 10);
        }
        var delta = new Array (0,1,2,3,4,-4,-3,-2,-1,0);
        for (i=Luhn.length-1; i>=0; i-=2 ){
            var deltaIndex = parseInt(Luhn.substring(i,i+1), 10);
            var deltaValue = delta[deltaIndex];
            sum += deltaValue;
        }
        var mod10 = sum % 10;
        mod10 = 10 - mod10;
        if (mod10==10)mod10=0;
        return mod10;
    }
    , checkLuhn = function(Luhn){
        var LuhnDigit = parseInt(Luhn.substring(Luhn.length-1,Luhn.length), 10);
        var LuhnLess = Luhn.substring(0,Luhn.length-1);
        if(calcLuhn(LuhnLess)==parseInt(LuhnDigit, 10)){
            return true;
        }
        return false;
    }
    , guessType = function(cardNo){
        var type = 'Unknown', candidates = [];
        cardNo = cleanUp(cardNo);
        _.each(CARD_CONFIG, function(type){
            if(!type.enabled)return;
            _.each(type.prefix, function(prefix){
                if(cardNo.indexOf(prefix) == 0){
                    candidates.push(type);
                }
            });
        });
        if(cardNo.length > 13){
            candidates = _.filter(candidates, function(candidate){
                return cardNo.length <= candidate.length;
            })
        }
        return {candidates: candidates, sure: cardNo.length > 13 && cardNo.length < 17, success: candidates.length>0,
            valid: candidates.length>0 && candidates[0].length == cardNo.length && checkLuhn(cardNo)};
    };

    jQuery.validator.addMethod("creditcard", function (value, element) {
        return guessType(value).valid;
    }, hnc.translate("Invalid card number."));
    return {guessType: guessType, cleanUp: cleanUp};
});