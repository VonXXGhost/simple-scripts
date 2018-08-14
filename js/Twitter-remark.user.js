// ==UserScript==
// HP:           https://greasyfork.org/scripts/31735
// @name         推特备注名
// @namespace    https://github.com/VonXXGhost
// @version      0.3.1
// @description  设置用户备注名并在TL上显示
// @author       VonXXGhost
// @match        https://twitter.com/*
// @grant             GM_setValue
// @grant             GM_getValue
// @require    http://code.jquery.com/jquery-3.2.1.js
// ==/UserScript==

// 初始化json文件
let g_name_json = JSON.parse(GM_getValue('twitter_mark_names', '{}'));

// 保存json文件
function saveSetting(){
	if (g_name_json){
        console.log(JSON.stringify(g_name_json), ' ');
		GM_setValue('twitter_mark_names', JSON.stringify(g_name_json));
	}
}

// 增加导出按钮
function addExportButton(){
    'use strict';
	let position = $('#user-dropdown > div > ul > li:nth-child(10)');
	let code = '<li id="export-backup-item" role="presentation"><a href="#">导出备注名列表</a></li><button type="button" class="hidden" id="mark-backup-export" />';
    position.before(code);
    $('#export-backup-item').on('click', function(e) {
        e.preventDefault();
        $('#mark-backup-export').click();
    });
   $('#mark-backup-export').on('click', function(){
	   prompt("请复制保存到任意文本文件中", JSON.stringify(g_name_json));
    });
}

//增加导入按钮
function addInportButton(){
    'use strict';
	let position = $('#user-dropdown > div > ul > li:nth-child(10)');
	let code = '<li id="inport-backup-item" role="presentation"><a href="#">导入备注名列表</a></li><button type="button" class="hidden" id="mark-backup-inport" />';
    position.before(code);
    $('#inport-backup-item').on('click', function(e) {
        e.preventDefault();
        $('#mark-backup-inport').click();
    });
   $('#mark-backup-inport').on('click', function(){
	   let setting = prompt("请复制备份字符串到下框中，注意：此举动会清空旧设置", '');
	   if (setting){
		   g_name_json = JSON.parse(setting);
		   saveSetting();
	   }
    });
}

// 修改timeline和主页备注名
function changeNames(marks){
    'use strict';
	let usernames = $('.stream span.username.u-dir b');
	usernames.each(function(){
		let user = $(this).text();
		if (marks[user]){
            let mark = ' [' + marks[user] + ']';
            if (user.indexOf('[') === -1){
				$(this).text(user + mark);
			}
		}
	});
    // 修改主页备注名
	let id = $($('b.u-linkComplex-target')[1]);
	if (marks[id.text()]){
		if ($(id.next()).text().indexOf('[') === -1){
            let mark = ' [' + marks[id.text()] + ']';
			let code = '<b>' + mark + '</b>';
			id.after(code);
		}
	}
    // 修改RT备注名
    let RTusernames = $('a.pretty-link.js-user-profile-link');
	RTusernames.each(function(){
		let id = $(this).attr('href').slice(1);
		let username = $($(this).find('b')[0]).text();
		if (username.indexOf('[') === -1){
			if (marks[id]){
				let mark = ' [' + marks[id] + ']';
				let username_len = $(this).children().length;
				if (username_len < 2){
					let code = '<b>' + mark + '</b>';
					$(this).append(code);
				}
			}
		}
	});
}


//---
// 在个人主页增加“添加备注”
function addName(marks){
	let id = $($('b.u-linkComplex-target')[0]).text();
	let markname = prompt("请输入备注名（新备注刷新后生效）", "");
	if (markname){
		marks[id] = markname;
        saveSetting();
	}
}

function addMarkButton(menu){
    let code = '<li class="mark-name-item not-blocked" role="presentation"><button type="button" class="dropdown-link markname-add" role="menuitem">添加备注名</button></li>';
    $(menu).prepend(code);
    $(function(){
    $('.markname-add').on('click', function(){
        addName(g_name_json);
        });
    });
}

function addMark(){
    if ($('li.mark-name-item.not-blocked').length === 0){
        let menu = $('div.dropdown-menu.dropdown-menu--rightAlign.is-autoCentered.is-forceRight > ul')[1];
        addMarkButton(menu);
    }
}


//---
addMark();
addExportButton();
addInportButton();
// 实时添加备注
let timeline = $('#stream-items-id');
window.setInterval(function(){
	changeNames(g_name_json);
    addMark();
}, 1000);
