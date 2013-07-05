define(["tools/messaging", "tools/ajax", "libs/tachymeter"], function(messaging, ajax, Tachymeter){
    var


    userLink = function(slug, name){return '<a href="/u/'+slug+'">' + name + '</a>'}
    , userPic = function(url){return url || "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm";}
    , companyLink = function(slug, name){return '<a href="/c/'+slug+'">' + name + '</a>'}
    , productLink = function(slug, name){return '<a href="/c/'+slug+'/1/product">' + name + '</a>'}
    , needLink = function(cSlug, nSlug, name){return '<a href="/c/'+cSlug+'/1/'+nSlug+'">' + name + '</a>'}

    , getPledgeModel = function(model){
        var key = "Pledge", actor = model.get(key);
        return {
            picture: userPic(actor.picture)
            , link: "#"
            , name: actor.name
            , subTitle : actor.name+" pledged to buy " + productLink(actor.companySlug, actor.offerName) +'.'
        }
    }
    , getApplicationModel = function(model){
        var key = "Application"
            , actor = model.get(key)
            , actorLink = "/c/"+actor.companySlug+"/1/"+actor.needSlug
            , user = actor.User
            , uLink = user?userLink(user.token, user.name):'<span>Someone</span>';
        return {
            picture: actor.comapnyLogo
            , link: actorLink
            , name: actor.companyName
            , subTitle : uLink + ' applied for <a href="'+actorLink+'">'+actor.need+"</a> at " + companyLink(actor.companySlug, actor.companyName) + '.'
        }
    }
    , getEndorsementModel = function(model){
        var key = "Endorsement"
            , actor = model.get(key)
            , actorLink = "/u/"+actor.endorserToken;
        return {
            picture: userPic(actor.endorserPicture)
            , link: actorLink
            , name: actor.endorserName
            , subTitle : userLink(actor.endorserToken, actor.endorserName) + " endorsed <strong>"+actor.endorseeName + '</strong> for ' + needLink(actor.companySlug, actor.needSlug, actor.needName)+'.'
        }
    }
    , getCompanySetupModel = function(model){
        var key = "Company"
            , actor = model.get(key)
            , actorLink = "/c/"+actor.slug
            , user = actor.User;
        return {
            picture: actor.logo
            , link: actorLink
            , name: actor.name
            , subTitle : user?'<a href="'+actorLink+'">'+actor.name + '</a> was setup by ' + userLink(user.token, user.name) + '.':''
            , actor: actor
        }
    }
    , getPendingModel = function(model){
        var result = getCompanySetupModel(model);
        result.subTitle = '<a href="'+result.link+'">'+result.name + '</a> is waiting for approval.';
        return result;
    }
    , getPublishedModel = function(model){
         var key = "Company"
            , actor = model.get(key)
            , actorLink = "/c/"+actor.slug
            , user = actor.Mentors, links = [];
        _.each(user, function(m){
            links.push(userLink(m.token, m.name));
        });
        return {
            picture: actor.logo
            , link: actorLink
            , name: actor.name
            , subTitle: '<a href="'+actorLink+'">'+actor.name + '</a> got approved by ' + links.join(", ")+'.'
            , actor: actor
        }
    }
    , getInviteModel = function(role){
        return function(model){
            var actor = model.get("Invitor"), user = model.get("User"), uLink = user.token?userLink(user.token, user.name):'<strong>' + user.name + '</strong>';
            return {
                picture: userPic(actor.picture)
                , link: '/u/'+actor.token
                , uLink: uLink
                , name: actor.name
                , subTitle: userLink(actor.token, actor.name) + ' invited '+uLink+' as a '+role+'.'
                , actor : actor
                , user : user
            }
        }
    }
    , getAcceptModel = function(role){
        return function(model){
            var actor = model.get("User");
            return {
                picture: userPic(actor.picture)
                , link: '/u/'+actor.token
                , name: actor.name
                , subTitle: userLink(actor.token, actor.name) + ' is now a '+role+' of this company.'
            }
        }
    }
    , getMemberInviteModel = function(model){
        var result = getMentorInviteModel(model);
        result.subTitle = userLink(result.actor.token, result.actor.name) + ' invited '+result.uLink+' as a team member.';
        return result;
    }
    , TYPE_MAP = {
        'PLEDGE': getPledgeModel
        ,'APPLICATION': getApplicationModel
        ,'ENDORSEMENT': getEndorsementModel
        , 'COMPANY_SETUP': getCompanySetupModel
        , 'WAITING_FOR_APROVAL': getPendingModel
        , 'PUBLISHED': getPublishedModel
        , 'MENTOR_INVITE': getInviteModel('mentor')
        , 'MENTOR_ACCEPT': getAcceptModel('mentor')
        , 'TEAM_MEMBER_INVITE': getInviteModel('member')
        , 'TEAM_MEMBER_ACCEPT': getAcceptModel('member')
    }

    , Activity = ajax.Model.extend({
        getActivity: function(){
           return TYPE_MAP[this.get('type')](this);
        }
        , getDate: function(){
            return this.get("created")?hnc.formatDate(hnc.parseDate(this.get("created"))):'';
        }
    })
    , ActivityStream = ajax.Collection.extend({model : Activity})

    , ActivityView = Backbone.View.extend({
        tagName : 'div'
        , className: 'single-activity'
        , initialize: function(opts){
            var activity = this.model.getActivity();
            if(activity)this.$el.html(opts.template({model: this.model, activity: activity}));
        }
    })

    , View = Backbone.View.extend({
        events: {
            'click .remove': "removeNeed"
            , 'keyup .remove': "removeNeed"

            , 'click .workflow-link': "highlightTarget"
            , 'keyup .workflow-link': "highlightTarget"
        }
        , template: _.template($("#template-activity").html())
        , initialize:function(opts){
            var lengths = [], max, min, view = this;
            if(opts.tacho) this.tacho = new Tachymeter(opts.tacho);

            this.$el.find(".form-validated").each(function(idx, form){
                ajax.ifyForm({form:form});
            });


            this.$activity = this.$(".activity-stream");
            this.model = new ActivityStream();
            this.listenTo(this.model, "add", this.addOne, this);
            ajax.submitPrefixed({
                url: "/web/round/activity"
                , data:{token: this.$activity.data('entityId')}
                , success: function(resp, status, xhr){
                    view.$activity.html('');
                    view.model.addOrUpdate(hnc.getRecursive(resp, 'Activity.Item', []));
                }
            })
        }

        , addOne: function(model){
            this.$activity.append(new ActivityView({template: this.template, model:model}).$el).removeClass("empty text-center");
        }

        , highlightTarget: function(e){
            if(!e.keyCode||e.keyCode == 13){
                var $t = $($(e.currentTarget).attr("href")).closest(".highlight-target");
                $t.addClass("highlighted");
                setTimeout(function(){
                    $t.removeClass("highlighted");
                }, 1000);
            }
        }

        , removeNeed: function(e){
            if(!e.keyCode||e.keyCode == 13){
                var $t = $(e.currentTarget)
                    , $need = $t.closest($t.data("target"))
                    , roundToken = this.$el.data('entityId');
                if(confirm("Do you really want to delete this need?")){
                    ajax.submitPrefixed({url: '/web/round/removeneed'
                        , data: {token:roundToken, Needs: [{token: $need.data("entityId")}]}
                        , success: function(resp, status, xhr){
                            $need.remove();
                            messaging.addSuccess({message:"Need successfully removed!"})
                        }
                    });
                }
            }
        }
        , render: function(){

        }
    });
    return View;
});
