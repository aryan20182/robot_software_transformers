import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose2D
import sys
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
class CentralNode(Node):

    def __init__(self, n_camera, robot_id):
        super().__init__('r_'+str(robot_id))
        self.group = MutuallyExclusiveCallbackGroup()
        self.publisher = self.create_publisher(Pose2D, 'r_'+str(robot_id)+'/pose', 1)
        time_period = 1/30
        self.timer = self.create_timer(time_period, self.pub_callback, callback_group=self.group)
        self.n_camera = n_camera
        self.robot_id = robot_id
        self.subs = []
        for i in range(n_camera):
            self.subs.append(self.create_subscription(Pose2D, 'c_'+str(i+1)+'/r_'+str(robot_id), self.subs_callback, 1, callback_group=self.group))
        self.camera_pose = []
    
    def subs_callback(self, msg):
        self.camera_pose.append(msg)

    def pub_callback(self):
        pose_X = 0
        pose_Y = 0
        pose_theta = 0
        if len(self.camera_pose) > 0:
            for pose in self.camera_pose:
                pose_X += pose.x
                pose_Y += pose.y
                pose_theta += pose.theta
            pose_X = pose_X/len(self.camera_pose)
            pose_Y = pose_Y/len(self.camera_pose)
            pose_theta = pose_theta/len(self.camera_pose)
            self.camera_pose = []
            self.publisher.publish(Pose2D(pose_X, pose_Y, pose_theta))
    
def main():
    n_camera = int(sys.argv[1])
    n_robots = int(sys.argv[2])
    print(n_camera, n_robots)
    rclpy.init()
    nodes = []
    try:
        executor = MultiThreadedExecutor(4)
        for i in range(n_robots):
            cnode = CentralNode(n_camera, i+1)
            nodes.append(cnode)
            executor.add_node(cnode)
        try:
            executor.spin()
        finally:
            executor.shutdown()
            for i in range(n_robots):
                nodes[i].destroy_node()
    finally:
        rclpy.shutdown()
    

if __name__ == '__main__':
    main()