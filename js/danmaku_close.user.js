// ==UserScript==
// @name         番剧关闭弹幕
// @version      0.2
// @description  番剧关闭弹幕
// @author       VonXXGhost
// @match        https://www.bilibili.com/bangumi/play/*
// @match        https://www.bilibili.com/video/*
// ==/UserScript==

function danmaku_close() {
    if($("div.bilibili-player-video-danmaku-root > div.bilibili-player-video-danmaku-switch.bui.bui-switch > label > span.bui-switch-body > span").css('margin-left') === '-18px'){
        $("div.bilibili-player-video-danmaku-root > div.bilibili-player-video-danmaku-switch.bui.bui-switch > input").click();
        console.log("番剧关闭弹幕:关闭弹幕");
    }
    else {
        console.log("番剧关闭弹幕:弹幕已关闭，不操作");
    }
};

function danmaku_open() {
    if($("div.bilibili-player-video-danmaku-root > div.bilibili-player-video-danmaku-switch.bui.bui-switch > label > span.bui-switch-body > span").css('margin-left') != '-18px'){
        $("div.bilibili-player-video-danmaku-root > div.bilibili-player-video-danmaku-switch.bui.bui-switch > input").click();
        console.log("番剧关闭弹幕:打开弹幕");
    }
    else {
        console.log("番剧关闭弹幕:弹幕已打开，不操作");
    }
};

window.addEventListener('message', (x) => {
    console.log('番剧关闭弹幕:' + x.data.type);
    if (x.data.type == "pakku_event_danmaku_loaded") {
         if (window.location.href.indexOf("bangumi/play/") > 0) {
            setTimeout(danmaku_close, 1000);
        } else {
            setTimeout(danmaku_open, 1000);
        }
    }
});
