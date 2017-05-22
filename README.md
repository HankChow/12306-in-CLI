# 命令行版12306

## 功能
在命令行下实现对 12306 的余票查询，免去打开网页的麻烦。

## 依赖
* Python 3.x
* requests 库
* prettytable 库（非必需）

## 用法
执行`python3 train.py [options]`即可，各命令行参数如下：

* （必填）`-d`, `--date=`：需要查询的订票日期，格式为YYYYDDMM或YYYY-DD-MM；
* （必填）`-f`, `--from=`：需要查询的出发站；
* （必填）`-t`, `--to=`：需要查询的到达站；
* （可选）`-s`, `--sort=`：按照查询出来结果的某一字段进行排序，默认为升序排序；
* （可选）`--desc`：当有此参数时，排序结果变为降序排序，且仅在有参数`-s`或`--sort=`存在时有效；
* （可选）`--filter=`：对查询结果进行筛选。

## 文件
* `train.py`：主文件；
* `stationsYYYYMMDD`：存放车站名与车站代码对应关系，后八位为最后更新日期。每次运行主文件时会检查该文件是否需要更新，如需更新，将会自动更新并修改文件名后八位为最新更新日期。

## 杂项
* 输出结果默认使用表格显示，因此需要 prettytable 库。若无 prettytable 库或不需要表格显示，在`train.py`中将`DISPLAY_IN_TABLE`值改为`False`即可。
* 后续加入余票提醒模块。