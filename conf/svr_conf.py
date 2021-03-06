# -*- coding: utf-8 -*-
import yaml


CONF = {
    # server
    'svr.name': 'example-server',
    'svr.log_conf_on_reload': True,

    # timer 设置 (单位:s)
    'svr.timer.min_span': 1,  # timer的精度
    'svr.timer.run_status_check_time_span': 60,  # 最大无响应时间，超过这个时间没有相应，自动退出
    'svr.timer.summary_output_time_point': 'M',  # 报告输出类型 D(per day), H(per hour), M(per minute)

    # close 信号处理配置
    'svr.close.force_close_delay': 10,

    # log
    'log.console': True,
    'log.console.level': 'INFO',
    'log.console.format': '<%(levelname)s: %(name)s(%(process)d)> [%(filename)s: %(lineno)d] >> %(message)s ',

    'log.syslog': True,
    'log.syslog.level': 'WARN',
    'log.syslog.format': '<%(levelname)s: %(name)s(%(process)d)> [%(filename)s: %(lineno)d] >> %(message)s ',

    'log.file_log': '',
    'log.file_log.level': 'WARN',
    'log.file_log.format': '<%(levelname)s: %(name)s(%(process)d)> [%(filename)s: %(lineno)d] >> %(message)s ',

    'log.email': False,
    'log.email.level': 'ERROR',
    'log.email.format': '<%(levelname)s: %(name)s(%(process)d)> [%(filename)s: %(lineno)d] >> %(message)s ',
    'log.email.config': {'host': ('smtp.163.com', 25),
                         'from': ('xxx@163.com', 'xxx'),
                         'target': ['xxx@163.com']},

    'example.handler.filename': '/tmp/js-count-for-%s.log'
}


try:
    with open('conf/svr_conf.yaml') as yaml_file:
        CONF.update(yaml.load(yaml_file))
except Exception as ex:
    pass
