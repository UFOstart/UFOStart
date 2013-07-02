define(["tools/messaging", "tools/ajax", "libs/tachymeter"], function(messaging, ajax, Tachymeter){
    var


    userLink = function(slug, name){return '<a href="/u/'+slug+'">' + name + '</a>'}
    , companyLink = function(slug, name){return '<a href="/c/'+slug+'">' + name + '</a>'}
    , productLink = function(slug, name){return '<a href="/c/'+slug+'/1/product">' + name + '</a>'}
    , needLink = function(cSlug, nSlug, name){return '<a href="/c/'+cSlug+'/1/'+nSlug+'">' + name + '</a>'}
    , PledgeModel = ajax.Model.extend({
        key : "Pledge"
        , getPicture :function(){
            return this.get("picture")
        }
        , getLink :function(){
            return "#"
        }
        , getName :function(){
            return this.get("name")
        }
        , getSubTitle :function(){
            return this.get("name")+" pledged to buy " + productLink(this.get("companySlug"), this.get("offerName")) +'.';
        }
    })
    , ApplicationModel = ajax.Model.extend({
        key : "Application"
        , getPicture :function(){
            return this.get("comapnyLogo")
        }
        , getLink :function(){
            return "/c/"+this.get("companySlug")+"/1/"+this.get("needSlug")
        }
        , getName :function(){
            return this.get("companyName")
        }
        , getSubTitle :function(){
            var user = this.get("User")
                , link = user?userLink(user.token, user.name):'<span>Someone</span>';
            return link + ' applied for <a href="'+this.getLink()+'">'+this.get("need")+"</a> at " + companyLink(this.get("companySlug"), this.get("companyName")) + '.';
        }
    })
    , EndorsementModel = ajax.Model.extend({
        key : "Endorsement"
        , getPicture :function(){
            return this.get("endorserPicture");
        }
        , getLink :function(){
            return "/u/"+this.get("endorserToken");
        }
        , getName :function(){
            return this.get("endorserName");
        }
        , getSubTitle :function(){
            return userLink(this.get("endorserToken"), this.get("endorserName")) + " endorsed <strong>"+this.get("endorseeName") + '</strong> for ' + needLink(this.get("companySlug"), this.get("needSlug"), this.get("needName"))+'.';
        }
    })
    , CompanySetupModel = ajax.Model.extend({
        key : "Company"
        , getPicture :function(){
            return this.get("logo");
        }
        , getLink :function(){
            return "/c/"+this.get("slug");
        }
        , getName :function(){
            return this.get("name");
        }
        , getSubTitle :function(){
            return '<a href="'+this.getLink()+'">'+this.get("name") + '</a> was setup by ' + userLink(this.get("creatorToken"), this.get("creatorName")) + '.';
        }
    })
    , PendingModel = CompanySetupModel.extend({
        getSubTitle :function(){
            return '<a href="'+this.getLink()+'">'+this.get("name") + '</a> is waiting for approval.';
        }
    })

    , PublishedModel = CompanySetupModel.extend({
        getSubTitle :function(){
            return '<a href="'+this.getLink()+'">'+this.get("name") + '</a> got approved by ' + userLink(this.get("mentorToken"), this.get("mentorName"))+'.';
        }
    })
    , MentorInviteModel = ajax.Model.extend({
        key : "User"
        , getPicture :function(){
            return this.get("invitorPicture");
        }
        , getLink :function(){
            return "/u/"+this.get("invitorToken");
        }
        , getName :function(){
            return this.get("invitorName");
        }
        , getSubTitle :function(){
            return userLink(this.get("invitorToken"), this.get("invitorName")) + ' invited <strong>' + this.get("name") + '</strong> as a mentor.';
        }
    })
    , MemberInviteModel = MentorInviteModel.extend({
        getSubTitle :function(){
            return userLink(this.get("invitorToken"), this.get("invitorName")) + ' invited <strong>' + this.get("name") + '</strong> as a team member.';
        }
    })
    , TYPE_MAP = {
        'PLEDGE': PledgeModel
        ,'APPLICATION': ApplicationModel
        ,'ENDORSEMENT': EndorsementModel
        , 'WAITING_FOR_APROVAL': PendingModel
        , 'PUBLISHED': PublishedModel
        , 'COMPANY_SETUP': CompanySetupModel
        , 'MENTOR_INVITE': MentorInviteModel
        , 'TEAM_MEMBER_INVITE': MemberInviteModel
    }

    , Activity = ajax.Model.extend({
        getActivity: function(){
            var cls = TYPE_MAP[this.get('type')]
                , obj = new cls();
            obj.set(this.get(obj.key))
            return obj;
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


            this.$activity = this.$(".activity-stream");
            this.model = new ActivityStream();
            this.listenTo(this.model, "add", this.addOne, this);
            ajax.submitPrefixed({
                url: "/web/round/activity"
                , data:{token: this.$activity.data('entityId')}
                , success: function(resp, status, xhr){
                    view.$activity.html('');
                    view.model.addOrUpdate(resp.Activity.Item);
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
