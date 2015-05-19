#!/usr/local/bin/python
# Application Task Scheduling Algorithm for ADON paper
# Author: Cui Longhai
import subprocess
import xmlrpclib
import re
from SimpleXMLRPCServer import SimpleXMLRPCServer

#Network Resource e.g. Layer2/3 network link bewteen MU and OSU
class Overlay:
    def __init__(self, id, src, dst, total_bandwidth, available_bandwidth, scheduled_tasks=[], queue=[]):
        self.id = id
        self.src = src
        self.dst = dst
        #SLA percent can be added here
        self.total = total_bandwidth

        self.available = available_bandwidth # 15gbps

        self.scheduled_tasks = scheduled_tasks
        self.queue = queue

    def __repr__(self):
        return 'overlay_id: %d from %s to %s available bandwidth : %d\n scheduled_tasks: %s \n queue: %s' % (
            self.id, self.src, self.dst, self.available, self.scheduled_tasks, self.queue)

    def update_queue_in_overlay(self):
        self.queue = sorted(self.queue, key=lambda task: -task.priority)
        print self.queue

#Application Demanding Science DMZ resource e.g. iRods SoyKB transfer
#The quality specification(Q-Spec) for network resource is currently only difined as bandwidth requirement of the application
class Application:
    def __init__(self, id, conflicts, bandwidth):
        self.id = id
        self.conflicts = conflicts
        self.bandwidth = bandwidth

    def __repr__(self):
        return 'app_id: %d bandwidth needed: %d\n conflicts: %s' % (
            self.id, self.bandwidth, self.conflicts)

#Application task instances
#Each application can have multiple instances of task request for ADON server
class Task:
    def __init__(self, id, overlay_id, app_id, priority):
        self.id = id
        self.overlay_id = overlay_id
        self.app_id = app_id
        self.priority = priority

    def __repr__(self):
        return 'task_id: %s overlay_id: %d app_id: %d priority: %d\n' % (
            self.id, self.overlay_id, self.app_id, self.priority)

#Main class of the Adon task scheduler
class Scheduler:
    def __init__(self, overlays, applications):
        self.overlays = overlays
        self.app_map = {}
        for app in applications:
            self.app_map[app.id] = app
            #print app

    def get_all_overlay_ids(self):
        overlay_ids = []
        for overlay in self.overlays:
            overlay_ids.append(overlay.id)
        return overlay_ids

    def get_overlay_by_id(self, overlay_id):
        for overlay in self.overlays:
            if overlay_id == overlay.id:
                return overlay

    def schedule_tasks(self, tasks):
        for task in tasks:
            if task.overlay_id not in self.get_all_overlay_ids():
                raise Exception("There is no such overlay_id: %d ! Please check if the task is on the correct overlay "
                                "network." % task.overlay_id)

            overlay = self.get_overlay_by_id(task.overlay_id)
            overlay.queue.append(task)

        overlay.update_queue_in_overlay()

        scheduled_task_ids = []
        for overlay in self.overlays:
            for task in overlay.queue:
                app = self.app_map[task.app_id]
                print "available: ", overlay.available, app.bandwidth
                if overlay.available >= app.bandwidth:
                    overlay.available -= app.bandwidth
                    print "available:",overlay.available
                    overlay.scheduled_tasks.append(task)
                    scheduled_task_ids.append(task.id)

        for scheduled_task_id in scheduled_task_ids:
            for task in overlay.queue:
                if scheduled_task_id == task.id:
                    overlay.queue.remove(task)
        print overlay

    def add_task(self, task):
        str = ""
        if task.overlay_id not in self.get_all_overlay_ids():
                raise Exception("There is no such overlay_id: %d ! Please check if the task is on the correct overlay "
                                "network." % task.overlay_id)
        overlay = self.get_overlay_by_id(task.overlay_id)
        app = self.app_map[task.app_id]
        if overlay.available >= app.bandwidth:
            overlay.scheduled_tasks.append(task)
            overlay.available -= app.bandwidth
            str += "Task %s scheduled in overlay %d" % (task.id, overlay.id)
            print str
            return True
        else:
            overlay.queue.append(task)
            overlay.update_queue_in_overlay()
            str += "There is not enough resource. Put task %s in Layer  %d Queue" % (task.id, overlay.id)
            print str
            return False

        print overlay

    #Parsing the result of
    def add_task_from_client(self, id, app_id, priority):
    #Use subprocess to call iperf terminal command
	    p = subprocess.Popen([r'iperf3','-c', '128.146.162.35', '-t', '1', '-p', '12345'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.communicate()
        #output type is a list, the bandwidth information is in the first position of the list, the type is a string
        print output[0]
        print type(output[0])
        #Parsing the result of iperf to get the bandwidth
    #Different format of the iperf result may require different parsing rules
    vs  =re.findall(r'\d+', output[0])
	#i=0
        #for v in vs:
        #    print i, v
        #    i+=1
        #print vs[43]
	l2_throughput = int(vs[43])	

	print "l2 throughput is",l2_throughput,"Mbps"

	p = subprocess.Popen([r'iperf3','-c', '128.146.162.35', '-t', '1', '-p', '54321'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.communicate()
        print output[0]
        print type(output[0])
        vs = re.findall(r'\d+', output[0])
        i=0
        #for v in vs:
        #    print i, v
        #    i+=1
        #print 42,vs[42]
	#print 43,vs[43]
	#print 44,vs[44]
        l3_throughput = int(vs[-2])

	print "l3 throughput is",l3_throughput,"Mbps" 
	#print type(l2_throughput), l2_throughput
	#print type(l3_throughput), l3_throughput
	if l2_throughput>=l3_throughput:
            install_l2_rule_for_iRODS()
	    oid = 2
            #print l2_throughput, l3_throughput  	
		
        if l2_throughput<l3_throughput:
	    install_l3_rule_for_iRODS()
	    oid = 3
	    #print l2_throughput, l3_throughput
	
	#print "overlay_id", overlay_id
	print "oid", oid
	task = Task(id, oid, app_id, priority)
        str = ""
	if self.add_task(task):
            str += "Task %s scheduled in Layer %d" % (id, oid)
        else:
            str += "There is not enough resource. Put task %s in Layer  %d Queue" % (id, oid)
        return str

#Layer 2 overlay network 10Gbps
overlay1 = Overlay(2, 'MU', 'OSU', 100000, 5000 )
#Layer 2 overlay network 1Gbps
overlay2 = Overlay(3, 'MU', 'OSU', 10000, 500)
overlays = [overlay1,overlay2]

#SoyKB QSpec throughput 300
app1 = Application(1, [], 300)
#SoyKB QSpec throughput 50
app2 = Application(2, [], 50)
app3 = Application(3, [], 2)
app4 = Application(4, [], 1)
apps = [app1, app2, app3, app4]

task1 = Task('A', 1, 1, 3)
task2 = Task('B', 1, 2, 10)
task3 = Task('C', 1, 3, 5)
task4 = Task('D', 1, 3, 2)

scheduler = Scheduler(overlays, apps)

def add_task(id, app_id, priority):
    str = scheduler.add_task_from_client(id, app_id, priority)
    print "add_task(id, app_id, priority)", scheduler.overlays
    print "hahahahha"
    return str

def install_l2_rule_for_iRODS():
    print "Using Layer 2 for iRODS transfer"
    #Macth dst port = 1247 Action Vlan id = 350
    #subprocess.proxy("active(10)")

def install_l3_rule_for_iRODS():
    print "Using Layer 3 for iRODS transfer"
    #Macth dst port = 1247 Action Vlan id = 1751
    #subprocess.proxy("active(11)")

#Use xmlrpc protocol for server-client communication.
server = SimpleXMLRPCServer(("localhost", 8888))
print "Listening on port 8888..."
#Register the add_task function for adding different application tasks.
server.register_function(add_task, "add_task")
#Run forever until the KeyboardInterrupt event. Press control+c to terminate.
server.serve_forever()

