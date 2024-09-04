# 工蜂IDE设置指引

[TOC]

## 工蜂IDE介绍
工蜂 IDE 是一款云 IDE 产品，为开发者提供云端运行环境。每个工作空间是一个独立的开发容器，在创建工作空间时，能够根据所选的环境模板来初始化开发环境，[更多介绍](https://km.woa.com/articles/show/605044)

## 模板介绍
目前，基于`FastFlyer`框架的项目已在工蜂IDE定制配套IDE模板，可以一键初始化，开箱即用，强烈推荐参与项目开发者使用。

![template](../static/gongfeng-ide2.png)

## 操作指引

### 创建个人分支

在工蜂代码库或智研需求管理中新建个人feature分支备用，建议命名为：`feature/xxxxxxx`

### 创建工作空间

1. 打开工蜂模板市场地址：[https://git.woa.com/dashboard/ide/templates](https://git.woa.com/dashboard/ide/templates)，如图点击【使用此环境】开始创建工作空间。

![template](../static/gongfeng-ide3.png)

`注：若看不到模板请联系 jagerzhang 授权。`


2. 如图配置工作空间，只需要修改红框栏位即可，注意选择关联个人feature分支，且不要勾选同步配置文件

![template](../static/gongfeng-ide4.png)

点击【新建工作空间】后，等待初始化完毕后就能看到IDE界面了。

### SwaggerUI

正常加载IDE之后，FastFlyer的服务也会自动启动，此时请按照以下方式打开 FastFlyer 的 SwaggerUI 界面：

![template](../static/gongfeng-ide5.png)

### 本地化IDE

工蜂IDE默认是在浏览器上操作，实际上谷歌内核的浏览器是支持安装工蜂IDE应用的，使用IDE应用启动，可以让WEB IDE脱离浏览器，直接本地化展示，更贴近于本地的IDE操作方式（本地化之后，主要可以解决 `Ctrl+W / Command+W`会误关闭整个浏览器标签的问题）。

如图在浏览器地址栏右侧点击安装应用，就能脱离浏览器使用IDE了，和本地VSCODE一样的使用体验。另外，安装后，也会在操作系统桌面生成【工蜂IDE】的应用图标，后续可以直接点击图表快速启动项目IDE（多个项目的话可以重命名一下这个图标便于识别）。

![template](../static/gongfeng-ide1.png)


<!-- 
#### IDE推荐设置

1. 打开IDE设置界面，搜索 `format` 关键词，找到如图位置，如红框所示，格式化方法使用yapf、勾选在保存文件的时候自动格式化：

![settings](../static/gongfeng-ide5.png)


2. 在IDE设置界面，搜索`flake8`，然后如图位置添加配置选项 `--max-line-length=120`：设置`flake8`的代码行宽限制规则，`flake8`默认的代码行不能超过`79`个字符，公司代码规范为`120`字符，这里按公司代码规范要求修改约束，方便开发。

![settings](../static/gongfeng-ide6.png)


#### IDE可选配置

1. 修改IDE颜色主题，如图选择一款自己喜欢的主题配色，有助于提升开发效率，喜欢暗色的推荐选择：`Solarized Dark`，喜欢亮色的推荐选择：`Solarized Light`

![settings](../static/gongfeng-ide7.png)

2. 修改为中文界面，喜欢中文本土化语言环境的可以如图设置下中文界面，有助于提升开发、设置效率，配置步骤如下：
使用键盘快捷键`Ctrl + Shift + P`（Windows/Linux）或`⌘ + Shift + P`（Mac）打开命令面板，然后键入`display`以筛选并显示`Configure Display Language`命令。按`Enter`，然后会按区域设置显示安装的语言列表，选择中文（Chinese）即可。  -->
