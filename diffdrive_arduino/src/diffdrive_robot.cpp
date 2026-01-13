#include <memory>
#include <thread>

#include "rclcpp/rclcpp.hpp"
#include "controller_manager/controller_manager.hpp"
#include "diffdrive_arduino/diffdrive_arduino.h"

int main(int argc, char **argv)
{
  rclcpp::init(argc, argv);

  auto node = std::make_shared<rclcpp::Node>("diffdrive_robot");

  // Instantiate the hardware interface
  auto robot = std::make_shared<DiffDriveArduino>();

  // Create the controller manager with the node and the hardware
  controller_manager::ControllerManager cm(node, {robot});

  // Executor to spin the node (so controller_manager services / topics work)
  rclcpp::executors::MultiThreadedExecutor executor;
  executor.add_node(node);
  std::thread spin_thread([&executor]() { executor.spin(); });

  // Main control loop
  const double loop_hz = 10.0;
  rclcpp::Rate loop_rate(loop_hz);
  rclcpp::Duration period = rclcpp::Duration::from_seconds(1.0 / loop_hz);

  while (rclcpp::ok())
  {
    // Read sensors from the hardware
    robot->read();

    // Update controller manager with current time and period
    cm.update(node->now(), period);

    // Write commands to the hardware
    robot->write();

    loop_rate.sleep();
  }

  executor.cancel();
  spin_thread.join();
  rclcpp::shutdown();

  return 0;
}
