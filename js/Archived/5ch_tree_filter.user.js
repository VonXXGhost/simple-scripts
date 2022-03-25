// ==UserScript==
// @name         快速筛选多回复楼层
// @version      0.1
// @description  \键只显示多回复楼层
// @author       VonXXGhost
// @match        https://*.5ch.net/test/read.cgi/*
// @require      http://code.jquery.com/jquery-3.4.0.min.js
// ==/UserScript==

(function() {
    document.onkeydown = (e) => {
        let code = e.which;
        if (code == 220){ // \键
            for(let post of $('body > div.container.container_body.mascot > div.thread > div.post')) {
                post = $(post);
                if (post.children('.treeView').length < 3) {
                    post.css('display', 'none');
                }
            }
            $('body > div.container.container_body.mascot > div.thread > br').remove();
        }
    };
})();
