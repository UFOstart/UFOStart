require(["./tools/hash.js", "./tools/messaging.js", "./tools/ajax.js", "./tools/creditcard.js"], function(hashlib, messaging, ajax, creditcard){
  return {'hashlib':hashlib, 'messaging':'messaging', 'ajax':ajax, 'creditcard':creditcard};
});


