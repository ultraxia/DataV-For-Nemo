# DataV For Nemo


## 简介
[SNH48-费沁源应援会](https://weibo.com/u/5577610720?topnav=1&wvr=6&topsug=1)基于阿里云DataV的数据可视化系统

## 各组件介绍
`modian_monitor.py`
* 该组件是实现数据可视化的基础，用于实时存储新产生的数据至服务器数据库 

 
`dataCompensation.py`
* 数据补偿模块，受网络环境等因素影响，`modian_monitor.py`有极小概率会丢失订单，`dataCompensation.py`会比对摩点API接口返回数据和服务器数据库中存储数据是否一致，并将遗漏订单及时补偿，保证服务的稳定性


`base_monitor.py`
* 用于监控竞争对手的集资情况，每隔一段时间更新数据库中竞争对手的集资数据

`auto_add_monitor.py`
* 该组件为`base_monitor.py`的升级版，`base_monitor.py`虽能及时更新竞争对手数据，但使用久后暴露出一个问题，若竞争对手开设新项目，需要手动添加至监控列表，人工干预效率极低，`auto_add_monitor.py`通过监控用户主页，能自动将竞争对手新开设的项目加入监控列表，并通过日志提醒，实现整个监控体系的自动化

`jzdaily.py`
* 用于存储当天集资数据概况至本地数据库

##  更新记录

**2018.04.09更新**：初次更新，共开放`auto_add_monitor.py`,`base_monitor.py`,`dataCompensation.py`,`modian_monitor.py`四个组件的源码

**2018.04.14更新**：新增`jzdaily.py`模块，用于存储当天集资概况数据至数据库
