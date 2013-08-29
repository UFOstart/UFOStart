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
            opts.auth.getContacts(); // kick it off now, so dont wait later
            opts.$el.on({"click": _.bind(this.onClick, this)});
        }

        , show : function(widgetData, contact){
            var view = this
                , isIntro = !!widgetData.expertName
                , params = {
                    sender: window.__options__.user.name
                    , text: isIntro?
                                "I've seen this task on http://"+window.location.host+" and thought "+widgetData.expertName+" can help out. Can you introduce me to "+widgetData.expertName+" so I can let him know of this task at "+window.location.href+"."
                                :"I've seen this task on http://"+window.location.host+" and thought you can help out. Your skills match perfectly, so checkout this task at "+window.location.href+"."
                    , name: widgetData.entityName
                    , direct: !!contact
                    , company: this.entity.companyName
                    , need:this.entity.name
                }
                , fetchContact = contact?null:this.options.auth.getContact(widgetData.entityId);

            this.$el.find(".form-validated").off();
            this.$el.html(this.template(params)).find(".modal").modal('show');
            return formlib.validate({root: this.$el.find(".form-validated")
                , submitHandler : function(form){
                  var $form = $(form), msgData = ajax.serializeJSON($form)
                  , msg = {
                      "recipients": {
                         "values": [{
                           "person": {
                                "_path": "/people/"+widgetData.entityId
                             }
                           }]
                         },
                       "subject": msgData.subject,
                       "body": msgData.message
                     };
                     if(fetchContact){
                        fetchContact.done(function(data){
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
              , dataType: "json"
              , contentType: "application/json; charset=utf-8"
            });

        }
        , onClick: function(e){
            var view = this
                , $el = $(e.currentTarget)
                , data = $el.data()
                , conDef = this.options.auth.getContacts();
                conDef.done(function(collection){
                    view.show(data, collection.get(data.entityId));
                })
        }
    })
    , instance = null;
    return function(opts){
        if(!instance)instance = new View(opts);
        instance.addHandler(opts);
    };
});