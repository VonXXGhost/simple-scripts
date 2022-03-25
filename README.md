# simple-scripts
各种自用的简单脚本

## 脚本说明

### js浏览器脚本

#### danmaku_close.user.js
b站仅针对番剧自动关闭弹幕，其他默认开弹幕。需结合 [pakku](https://github.com/xmcp/pakku.js) 使用。

#### sakugabooru_to_gif.user.js
在sakugabooru页面添加打开相关稿件微博gif的选项

#### ytb_kb_control.user.js
YouTube 键盘打开调试信息或只显示预定直播


### python

#### bgm_anime_friends_rank.py
获取统计bangumi好友评分数据

#### clean_outdated_file.py
清理指定目录下的过期文件

#### periodic_deposit_manager.py
定期存款管理统计

#### potplayer_auto_save_episode.py
记录本地播放集数。仅windows用。基于win32gui接口的窗口标题文字识别，以存档文件与窗口标题的差异度作为判断基准。
使用前需要更改anime_path为自己的动画存放文件夹，ex_dirs为不需要存档的文件夹。推荐改为pyw后缀以无窗口模式使用。

#### clean_outdated_file.py
清理过期文件


### 弃用存档

#### 5ch_tree_filter.user.js
【*Archived*】5ch 快速筛选多回复楼层。

#### Twitter-remark.user.js
【*Archived*】推特备注名脚本。详见[greasyfork页面](https://greasyfork.org/scripts/31735)

#### twitter_ids_tool.py
【*Archived*】忘了干嘛的了

#### twitter_same_friends.py
【*Archived*】获取两个推特账号相同的关注用户列表

#### update_notifications.py
【*Archived*】用于win10的网站更新桌面提醒，依赖于win10toast、BeautifulSoup等。COOKIES内填写纯文本格式的cookie。
