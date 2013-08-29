define(["tools/ajax"], function(ajax){
    var
        Contact = ajax.Model.extend({
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
        , Contacts = ajax.Collection.extend({model: Contact});

    return {Contact:Contact, Contacts:Contacts};
});