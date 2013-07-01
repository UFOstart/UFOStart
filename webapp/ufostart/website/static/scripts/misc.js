define(["tools/ajax"], function(ajax){

    // Bootstrap Touch Devices DropDown Fix START
    $('body')
    .on('touchstart.dropdown', '.dropdown-menu', function (e) { e.stopPropagation(); })
    .on('touchstart.dropdown', '.dropdown-submenu', function (e) { e.preventDefault(); })
    // Bootstrap Form inside dropdown prevent close
    .on("click", '.dropdown input, .dropdown label', function(e){e.stopPropagation();});
    // Bootstrap Touch Devices DropDown Fix END

    // TOGGLEABLE FLY OUTS
    $(document).on({click: function(e){
        var $t = $(e.currentTarget), data = $t.data(), target = data.toggleTarget, toggle = data.toggleClass
            , on = (target?$t.closest(target):$t).toggleClass(toggle).hasClass(toggle);
        if(data.toggleText){
            if(on){
                $t.data("backupText", $t.html());
                $t.html(data.toggleText);
            } else {
                $t.html(data.backupText);
            }
        }
    }}, "[data-toggle-class]");
    // hiding server generated messages
    var mCont = $("#message-container");
    if(mCont.length){
        mCont.on({click: function(e){
            var $t = $(this).closest(".alert");
            if(!$t.siblings(".alert").length)
                mCont.hide();
            $t.remove();
        }}, '[data-dismiss="alert"]');
        $(document).on({scroll: function(e){
                var messageTop = mCont.position().top;
                mCont[$(window).scrollTop()>messageTop?"addClass":"removeClass"]("fixed")
        }});
    }
    // IE placeholder plugin
    var NATIVE_PLACEHOLDER = !!("placeholder" in document.createElement( "input" ));
    if(!NATIVE_PLACEHOLDER){
        $('input[placeholder], textarea[placeholder]').placeholder();
    }

    $(document).on({
        click: function(e){
            var data = $(e.target).data();
            require([data.module], function(v){
                v.init(data, $(e.target));
            });
        }
    },  ".js-link");

    var tLoaded = $.Deferred();
    $(".hover-container").one({
        mouseover : function(e){
            var data = $(e.currentTarget).data();
            if(tLoaded.state() != 'resolved')require(["text!templates/profile.html"], function(templ){tLoaded.resolve(_.template(templ))});
            ajax.submitPrefixed({
                url:"/web/user/mini"
                , data: {token: data.entityId}
                , success: function(resp, status, xhr){
                    var user = resp.User;
                    tLoaded.done(function(templ){
                        $(e.currentTarget).append(
                            templ({
                                link: '/u/'+ user.token
                                , startupValue: '$' + hnc.formatNum(user.startupValue)
                                , user: user
                            })
                        )
                    });
                }
            });
        }
    }).find("a").prop('href', null);
    return {NATIVE_PLACEHOLDER:NATIVE_PLACEHOLDER}
});
