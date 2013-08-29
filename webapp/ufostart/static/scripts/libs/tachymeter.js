define([], function(){

    var View = function(opts){
        var total = 100
            , value = opts.fillRatio
            , w = h = $(opts.el).width()
            , r = new Raphael(opts.el, w, h)
            , strokeWidth = 30
            , R = (w-strokeWidth)*0.5, params = {'stroke': '#ff792a', 'stroke-width': strokeWidth}


        r.canvas.setAttribute('preserveAspectRatio', 'xMidYMid meet');
        r.customAttributes.arc = function (startx, starty, value, total, R) {
            var alpha = 360 / total * value%total,
                a = (90 - alpha) * Math.PI / 180,
                x = startx + R * Math.cos(a),
                y = starty - R * Math.sin(a),
                path;
            if (total == value) {
                path = [["M", startx, starty - R], ["A", R, R, 0, 1, 1, startx-0.01, starty - R]];
            } else {
                path = [["M", startx, starty - R], ["A", R, R, 0, +(alpha > 180), 1, x, y]];
            }
            return {path: path, stroke: '#686868', 'stroke-width': strokeWidth+2};
        };
        var circle = r.circle(w*.5, h*.5, R).attr(params);
        r.path().attr({'stroke-width': strokeWidth, arc: [w*.5,h*.5, value, total, R]});
        return r;
    };
    return View;
});
