#!/usr/bin/python

import psutil
from datetime import datetime
import time
import os
import csv
import collections


log_file = 'proc_log.log'


def get_processes_info():
	now = datetime.now()
	log_year = int(now.strftime("%Y"))
	log_mon = int(now.strftime("%m"))
	log_day = int(now.strftime("%d"))
	log_hour = int(now.strftime("%H"))
	log_min = int(now.strftime("%M"))
	log_sec = int(now.strftime("%S"))
	# the list the contain all process dictionaries
	processes = []
	for process in psutil.process_iter():
		# get all process info in one shot
		with process.oneshot():
			# get the process id
			pid = process.pid
			if pid == 0:
				# System Idle Process for Windows NT, useless to see anyways
				continue
			# get the name of the file executed
			name = process.name()
			# get the time the process was spawned
			try:
				create_time = datetime.fromtimestamp(process.create_time())
			except OSError:
				# system processes, using boot time instead
				create_time = datetime.fromtimestamp(psutil.boot_time())
			try:
				# get the number of CPU cores that can execute this process
				cores = len(process.cpu_affinity())
			except psutil.AccessDenied:
				cores = 0
			# get the CPU usage percentage
			cpu_usage = process.cpu_percent()
			# get the status of the process (running, idle, etc.)
			status = process.status()
			try:
				# get the process priority (a lower value means a more prioritized process)
				nice = int(process.nice())
			except psutil.AccessDenied:
				nice = 0
			try:
				# get the memory usage in bytes
				memory_usage = process.memory_full_info().uss
			except psutil.AccessDenied:
				memory_usage = 0
			# total process read and written bytes
			io_counters = process.io_counters()
			read_bytes = io_counters.read_bytes
			write_bytes = io_counters.write_bytes
			# get the number of total threads spawned by this process
			n_threads = process.num_threads()
			# get the username of user spawned the process
			try:
				username = process.username()
			except psutil.AccessDenied:
				username = "N/A"
			
		processes.append(collections.OrderedDict([
			('log_year', log_year),
			('log_mon', log_mon),
			('log_day', log_day),
			('log_hour', log_hour),
			('log_min', log_min),
			('log_sec', log_sec),
			('pid', pid), 
			('name', name), 
			('cpu_usage', cpu_usage), 
			('memory_usage', memory_usage), 
			('create_time', create_time),
			('cores', cores), 
			('status', status), 
			('nice', nice),
			('read_bytes', read_bytes), 
			('write_bytes', write_bytes),
			('n_threads', n_threads), 
			('username', username)
		]))

	return processes


def write_to_csv(data):
	with open(log_file, 'a') as file:
		w = csv.DictWriter(file, data[0].keys())

		if file.tell() == 0:
			w.writeheader()

		for row in data:
			w.writerow(row)


if __name__ == '__main__':
	result = get_processes_info()
	write_to_csv(result)
