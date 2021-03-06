#!/usr/bin/python

import rospy
from geometry_msgs.msg import Pose2D, Twist
from std_msgs.msg import Float32

class SpheroCtrl:

    def __init__(self):
        rospy.init_node('sphero_ctrl')
        self.cmd_vel_pub = rospy.Publisher('cmd_vel', Twist, queue_size=1)
        self.cmd_turn_pub = rospy.Publisher('cmd_turn', Float32, queue_size=1)
 
        #self.sphero_target_sub = rospy.Subscriber("sphero_pos", Pose2D, self.sphero_pos_callback)
        #self.sphero_position_sub = rospy.Subscriber("sphero_target_pos", Pose2D, self.sphero_target_pos_callback)
        self.sphero_target_sub = rospy.Subscriber("tracked_pos", Pose2D, self.sphero_pos_callback)
        self.sphero_position_sub = rospy.Subscriber("target_pos", Pose2D, self.sphero_target_pos_callback)
        
        self.sphero_target_pos = [-1,-1]
        self.runnable = False
    
        self.Kp = 0.0
        self.Kd = 0.0
        self.Kp = rospy.get_param('/gains/P')
        self.Kd = rospy.get_param('/gains/D')
      
        print "P " + str(self.Kp) + " D " + str(self.Kd)
        self.last_time = None 

    def start(self):
        self.runnable = True

    def stop(self):
        cv = Twist()
        cv.linear.x = 0.0
        cv.linear.y = 0.0
        cv.linear.z = 0.0
        cv.angular.x = 0.0
        cv.angular.y = 0.0
        cv.angular.z = 0.0
        self.cmd_vel_pub.publish(cv)
        
        self.runnable = False

    def sphero_pos_callback(self, msg):
        if self.runnable == True:
            current_pos = [float(msg.x), float(msg.y)]

            if current_pos[0] < 0 or current_pos[1] < 0:
                # stop when running out of view
                cv = Twist()
                cv.linear.y = 0.0
                cv.linear.y = 0.0
                cv.linear.z = 0.0
                cv.angular.x = 0.0
                cv.angular.y = 0.0
                cv.angular.z = 0.0
                self.cmd_vel_pub.publish(cv)
              
            elif self.sphero_target_pos[0] >= 0 and self.sphero_target_pos[1] >= 0:
                delta_x = self.sphero_target_pos[0] - current_pos[0]
                delta_y = self.sphero_target_pos[1] - current_pos[1]

                d_delta_x = 0.0
                d_delta_y = 0.0          
                if self.last_time == None:
                   self.last_time = rospy.get_time()
                   self.last_x = current_pos[0]
                   self.last_y = current_pos[1]
                else:
                   new_time = rospy.get_time()
                   delta_t = new_time - self.last_time
                   delta_last_x = current_pos[0] - self.last_x 
                   delta_last_y = current_pos[1] - self.last_y
                   self.last_time = new_time
                   self.last_x = current_pos[0]
                   self.last_y = current_pos[1]
                   d_delta_last_x = delta_last_x / delta_t
                   d_delta_last_y = delta_last_y / delta_t

                gain_x = self.Kp * delta_x + self.Kd * d_delta_last_x
                gain_y = self.Kp * delta_y + self.Kd * d_delta_last_y
 
                cv = Twist()
                if gain_x > 0: 
                    cv.linear.x = min(- gain_x , -20.0)
                elif gain_x < 0:
                    cv.linear.x = max(- gain_x , 20.0)
                if gain_y > 0:
                    cv.linear.y = max( gain_y, 20.0)
                elif gain_y < 0:
                    cv.linear.y = min( gain_y, -20.0)
                cv.linear.z = 0.0
                cv.angular.x = 0.0
                cv.angular.y = 0.0
                cv.angular.z = 0.0
                if cv.linear.x != 0.0 and cv.linear.y != 0.0:
                    #print "tar : " + str(self.sphero_target_pos)
                    #print "curr : " + str(current_pos)
                    #print "del : " + str([delta_x, delta_y])
                    print "d_t : " + str(delta_t)
                    print "d_del : " + str([d_delta_last_x, d_delta_last_y])
                    print "vel : " + str([cv.linear.x, cv.linear.y])           
                self.cmd_vel_pub.publish(cv)
                

    def sphero_target_pos_callback(self, msg):
        self.sphero_target_pos = [float(msg.x), float(msg.y)]
        print "target pos : " + str(self.sphero_target_pos)



if __name__ == '__main__':

    ctrl = SpheroCtrl()
    ctrl.start()
    rospy.spin()
    ctrl.stop()

    
