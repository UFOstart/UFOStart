define([], function(){

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

    jQuery.validator.addMethod("tagsearch-required", function (value, element) {
        return $(element).closest(".tagsearch-container").find(".tag").length > 0;
    }, hnc.translate("Please add at least one tag."));

    return {NATIVE_PLACEHOLDER:NATIVE_PLACEHOLDER}
});
