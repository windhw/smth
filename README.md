# smth
和水木社区相关的一些Python代码
## smth_notifier.py
实时监控水木社区指定版面，如果版面出现新的感兴趣（包含指定关键字）的帖子，就给我发邮件。使用场景：比如我需要在二手版上找二手自行车
## smth_user_monitor.py
实时监控水木2站上的所有用户状态，记录下每个用户的发帖行为（id，时间）。使用场景：水木2站匿名版看id, 嘘..
## smth_telnet.py
Telnet进水木社区并挂站（目前只实现了telnet进去，没实现挂站，python的telnet库真心不好用）。使用场景：挂经验值、积分，你懂的。
