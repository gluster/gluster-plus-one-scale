"""This module is handeling the logging of plus one scale in gluster."""


import logging

# logger decides what to log
glogger = logging.getLogger(__name__)
glogger.setLevel(logging.INFO)

# file handler decides where and how to log those logs of logger
gf_log_handler = logging.FileHandler("/var/log/glusterfs/gluster-plus-one-scale.logs")

format_string = '%(asctime)s:%(funcName)s:%(levelname)s:%(lineno)d:%(message)s'
gf_log_formatter = logging.Formatter(format_string)
gf_log_handler.setFormatter(gf_log_formatter)

glogger.addHandler(gf_log_handler)
