#!/usr/bin/python

import rospy
import rosbag
import datetime
from std_msgs.msg import Int16, Float32, Bool
from sensor_msgs.msg import Image
from threading import Lock


def bag_filename(dir="."):
    new_file_name = datetime.datetime.now().isoformat('_').replace(":","-") + ".bag"
    if dir != ".":
        new_file_name = dir + '/' + new_file_name

    return new_file_name  


def make_float_msg(value):
    msg = Float32()
    msg.data = value
    return msg


def make_int_msg(value):
    msg = Int16()
    msg.data = value
    return msg


class RecordTelemetry(object):
    def __init__(self):
        self.last_steering = 0.0
        self.last_throttle = 0.0
        self.lock = Lock()
        self.bag = None
        rospy.init_node('record_telemetry')
        rospy.Subscriber("/steering_value", Float32, self.steering_callback)
        rospy.Subscriber("/throttle_value", Float32, self.throttle_callback)
        rospy.Subscriber("/front_camera/image_warped", Image, self.image_callback)
        rospy.Subscriber("/record_telemetry", Bool, self.record_callback)
        
        rospy.spin()

    
    def record_callback(self, msg):
        self.lock.acquire()
        if msg.data and self.bag is None:
            self.bag = rosbag.Bag(bag_filename(), 'w')
            self.bag.write("/steering_value", make_float_msg(self.last_steering))
            self.bag.write("/throttle_value", make_float_msg(self.last_throttle))
        elif not msg.data and self.bag is not None:
            self.bag.close()
            self.bag = None
        self.lock.release()


    def steering_callback(self, msg):
        self.last_steering = msg.data
        self.lock.acquire()
        if self.bag is not None:
            self.bag.write("/steering_value", msg) 
        self.lock.release()


    def throttle_callback(self, msg):
        self.last_throttle = msg.data
        self.lock.acquire()
        if self.bag is not None:
            self.bag.write("/throttle_value", msg) 
        self.lock.release()


    def image_callback(self, msg):
        self.lock.acquire()
        if self.bag is not None:
            self.bag.write("/front_camera/image_warped", msg)
        self.lock.release()


if __name__ == "__main__":
    try:
        RecordTelemetry()
    except rospy.ROSInterruptException:
        rospy.logerr('Could not start telemetry recorder node.')

