import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def quaternion_to_euler(qw, qx, qy, qz):
    """
    Convert quaternion to Euler angles (roll, pitch, yaw).
    
    Parameters:
    qw, qx, qy, qz: Quaternion components.

    Returns:
    Roll, Pitch, Yaw in radians.
    """

    # Convert quaternion to Euler angles
    roll = np.arctan2(2 * (qw * qx + qy * qz), 1 - 2 * (qx**2 + qy**2))
    pitch = np.arcsin(2 * (qw * qy - qz * qx))
    yaw = np.arctan2(2 * (qw * qz + qx * qy), 1 - 2 * (qy**2 + qz**2))
    return roll, pitch, yaw

def update_position(imu_data, delta_t):
    """
    Update position based on IMU data.
    
    Parameters:
    imu_data: Dictionary containing acceleration and quaternion data.
    delta_t: Time interval in seconds.

    Returns:
    Positions list: List of (x, y, z) positions.
    """
    # Initialize position and velocity
    positions = []
    vx, vy, vz = 0.0, 0.0, 0.0
    x, y, z = 0.0, 0.0, 0.0

    for ax, ay, az, qw, qx, qy, qz in zip(imu_data["ax"], imu_data["ay"], imu_data["az"], 
                                          imu_data["qw"], imu_data["qx"], imu_data["qy"], imu_data["qz"]):
        
        # Convert quaternion to Euler angles
        roll, pitch, yaw = quaternion_to_euler(qw, qx, qy, qz)

        # Create rotation matrix from Euler angles
        R = np.array([
            [np.cos(pitch) * np.cos(yaw), np.cos(pitch) * np.sin(yaw), -np.sin(pitch)],
            [np.sin(roll) * np.sin(pitch) * np.cos(yaw) - np.cos(roll) * np.sin(yaw),
             np.sin(roll) * np.sin(pitch) * np.sin(yaw) + np.cos(roll) * np.cos(yaw),
             np.sin(roll) * np.cos(pitch)],
            [np.cos(roll) * np.sin(pitch) * np.cos(yaw) + np.sin(roll) * np.sin(yaw),
             np.cos(roll) * np.sin(pitch) * np.sin(yaw) - np.sin(roll) * np.cos(yaw),
             np.cos(roll) * np.cos(pitch)]
        ])

        # Rotate acceleration to global frame
        accel_global = R @ np.array([ax, ay, az])
        
        # Update velocities
        vx += accel_global[0] * delta_t
        vy += accel_global[1] * delta_t
        vz += accel_global[2] * delta_t

        # Update positions
        x += vx * delta_t
        y += vy * delta_t
        z += vz * delta_t

        # Store the position
        positions.append((x, y, z))

    return positions

# Example IMU data
imu_data = {
    "ax": [0.0, 0.1, 0.2, 0.1],   # Simulated acceleration in x-axis
    "ay": [0.0, 0.0, 0.0, 0.0],   # Simulated acceleration in y-axis
    "az": [9.8, 9.7, 9.6, 9.5],   # Simulated acceleration in z-axis
    "qw": [1, 1, 1, 1],           # Quaternion values (w component)
    "qx": [0, 0, 0, 0],           # Quaternion values (x component)
    "qy": [0, 0, 0, 0],           # Quaternion values (y component)
    "qz": [0, 0, 0, 0],           # Quaternion values (z component)
}

delta_t = 0.1  # Time interval in seconds
positions = update_position(imu_data, delta_t)

# # Visualization
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')

# # Unzip the positions for plotting
# x_positions, y_positions, z_positions = zip(*positions)

# # Plot the ball's path
# ax.plot(x_positions, y_positions, z_positions, marker='o', markersize=5)

# # Plot the final position as a ball
# ax.scatter(x_positions[-1], y_positions[-1], z_positions[-1], color='red', s=100)  # Final position

# # Set labels
# ax.set_xlabel('X Position')
# ax.set_ylabel('Y Position')
# ax.set_zlabel('Z Position')
# ax.set_title('3D Position of the Ball')

# plt.show()