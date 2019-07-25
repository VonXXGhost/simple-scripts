// ==UserScript==
// @name         键盘打开调试信息或只显示预定直播
// @version      0.2
// @description  键盘打开调试信息或只显示预定直播
// @author       VonXXGhost
// @include        https://www.youtube.com/*
// @require      http://code.jquery.com/jquery-3.4.0.min.js
// ==/UserScript==

function rightclick(x,y){
    var ev = document.createEvent("MouseEvent");
    var el = document.elementFromPoint(x,y);
    ev.initMouseEvent(
        "contextmenu",
        true /* bubble */, true /* cancelable */,
        Window.window, null,
        x, y, 0, 0, /* coordinates */
        false, false, false, false, /* modifier keys */
        0 /*left*/, null
    );
    el.dispatchEvent(ev);
}

(function() {
    document.onkeydown = (e) => {
        var code = e.which;
        if (code == 220){    // \键
            rightclick(250, 250);
            $("body > div.ytp-popup.ytp-contextmenu > div > div > div:nth-child(7)").click();
            $("ytd-grid-renderer ytd-grid-video-renderer:contains('前')").remove();
        }
    };
})();
