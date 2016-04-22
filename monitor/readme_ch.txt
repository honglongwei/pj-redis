
一、Monitor
     1.为每个redis实例开启一个定时线程，用于收集Info数据，并存储如下：
1. Info 但获取失败是保存为 NULL值
并提取如下数据单独存储，便于显示
2. Memory ：peak，current
3. command： 两次差值计算结果
4.Status ： down、Master（detail）、slave（detail），并只有在两次变更时记录
5.Hit rate
6.keys、expires
7.过期数据 expired、evicted

    2.数据量评估
          每3s取一次，那么每小时数据：1200，一次Info数据1.5K；那么一个实例1小时1.8M，那么20个实例一天产生数据：860M。
     Info全量数据还是不准备全量保存一份，无论redis内存占用，还是使用sqllite，压力都大。

         那么不缓存Info，其他数据一次200字节，那么一天下来：120M；设计最长保存7天；由Monitor定时检查。

      redis采用ZSET保存，使用UNIX 时间戳为score，数据内容使用json保存。

二、Web界面：
    Overview + Live

三、使用方式
	redis-live.conf 为json格式配置
	收集到的数据存储目前只能使用redis
	
	启动：
	两个进程： redis-monitor.py 为定时收集进程
				redis-live.py 是站点，端口为：8888
	
安装依赖：
	python2.7
	tornado
	redis-py
	python-dateutil-2.1
	jinja2
	werkzeug
	