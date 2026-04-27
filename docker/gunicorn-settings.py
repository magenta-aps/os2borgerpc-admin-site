# Copyright (C) 2021 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.

# Used by Dockerfile - compose does a few overrides
import multiprocessing

num_workers = multiprocessing.cpu_count() * 3

worker_class = "gthread"
bind = "0.0.0.0:9999"
# The recommendations in regards to both workers and threads are:
# "A positive integer generally in the 2-4 x $(NUM_CORES) range. You’ll want to vary this a bit to find the best for your particular application’s work load."
# https://gunicorn.org/reference/settings/?h=settings#worker-processes
workers = num_workers
threads = num_workers * 4
accesslog = "-"
errorlog = "-"
worker_tmp_dir = "/dev/shm"
# To help reduce potential memory leaks
max_requests = 1500
# To reduce the risk of many workers restarting simultaneously
max_requests_jitter = 50
# The IP of the traefik container - if not specified, gunicorn
# only trusts x forwarded for coming from 127.0.0.1
forwarded_allow_ips = "127.0.0.1,172.18.0.2"
# Default access log format except showing X forwarded for IP instead of host IP, as the host IP is just traefik's
access_log_format = (
    '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
)
