define(["tools/form", "tools/messaging", "tools/ajax", "text!networks/linkedin/msg.html"], function(formlib, messaging, ajax, tmpl){
    var View = Backbone.View.extend({
        events: {'click .cancel': "close"}
        , template: _.template(tmpl)

        , initialize:function(opts){
            this.$el.appendTo('body');
            this.entity = $("[data-entity=need]").data();
        }
        , render: function(){

        }
        , close:function(e){
            this.$(".modal").modal('hide');
        }
        , addHandler: function(opts){
            var liId = opts.$el.data('entityId')
                , conDef = opts.auth.getContacts();
            opts.$el.on({"click": _.bind(this.onClick, this)});
        }

        , show : function(id, name, contact){
            var view = this
                , params = {
                    sender: window.__options__.user.name
                    , host : window.location.host
                    , link : window.location.href
                    , name: name
                    , company: this.entity.companyName
                    , need:this.entity.name
                }
                , def = contact?null:this.options.auth.getContact(id);

            this.$el.find(".form-validated").off();
            this.$el.html(this.template(params)).find(".modal").modal('show');
            return formlib.validate({root: this.$el.find(".form-validated")
                , submitHandler : function(form){
                  var $form = $(form), data = ajax.serializeJSON($form)
                  , msg = {
                      "recipients": {
                         "values": [{
                           "person": {
                                "_path": "/people/"+id
                             }
                           }]
                         },
                       "subject": data.subject,
                       "body": data.message
                     };
                     if(def){
                        def.done(function(data){
                            var headers = hnc.getRecursive(data, 'apiStandardProfileRequest.headers.values', []);
                            if(!headers.length){
                                messaging.addError({'message': "A Linkedin error occured, you cannot contact this person."})
                                return;
                            }
                            headers = headers[0].value.split(":");
                            msg["item-content"] = {"invitation-request":{"connect-type":"friend","authorization":{'name':headers[0], 'value':headers[1]}}};
                            view.sendMsg($form, msg);
                        });
                     } else view.sendMsg($form, msg);

                  $form.find("button.btn,a.btn").button("loading");
                }
            })
        }
        , sendMsg: function($form, msg){
            var view = this;
            $.ajax({
              type: "POST"
              , url: this.options.auth.getApiUrl("/people/~/mailbox")
              , data: JSON.stringify(msg)
              , success: function(data, status, xhr){
                    messaging.addSuccess({'message': "Message sent!"})
                    $form.find("button.btn,a.btn").button("reset");
                    view.close();
              }
              , error: function(xhr, errorText){
                if(xhr.status==201) {
                    messaging.addSuccess({'message': "Message sent!"})
                    $form.find("button.btn,a.btn").button("reset");
                    view.close();
                } else {
                    messaging.addError({'message': "A Linkedin error occured, you cannot contact this person."})
                   $form.find("button.btn,a.btn").button("reset");
                }
              }
              , complete: function(){
                  messaging.addError({'message': "A Linkedin error occured, you cannot contact this person."})
                  $form.find("button.btn,a.btn").button("reset");
              }

              , dataType: "json"
              , contentType: "application/json; charset=utf-8"
            });

        }
        , onClick: function(e){
            var view = this
                , $el = $(e.currentTarget)
                , id = $el.data("entityId")
                , name = $el.data("entityName")
                , conDef = this.options.auth.getContacts();
                conDef.done(function(collection){
                    view.show(id, name, collection.get(id));
                })
        }
    })
    , instance = null;
    return function(opts){
        if(!instance)instance = new View(opts);
        instance.addHandler(opts);
    };
});