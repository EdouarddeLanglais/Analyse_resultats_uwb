import numpy as np
import matplotlib.pyplot as plt


data = np.loadtxt("Results/res_08-08-2025_11-28-48.csv", delimiter=',', dtype=np.float64)

timestamps = data[0]
measures = data[1]
data = data.T

# Initialize the KF matrixes
T = timestamps.shape[0]
F = np.array([[1]])
H = np.array([[1]])
Q = np.array([[0.3]]) #0.075
R = np.array([[1]])
x0 = np.array([0])

x_hat = np.zeros((T, 1))
P = np.zeros((T, 1, 1))
 
x_hat[0] = x0
P[0] = Q
 
for t in range(1, T):
    x_hat[t] = F @ x_hat[t-1]
    P[t] = F @ P[t-1] @ F.T + Q
 

    K = P[t] @ H.T @ np.linalg.inv(H @ P[t] @ H.T + R)
    x_hat[t] = x_hat[t] + K @ (measures[t] - H @ x_hat[t])
    P[t] = (np.eye(1) - K @ H) @ P[t]

fig, ax = plt.subplots()
ax.plot(range(T), 0.01*measures, label='Measures',marker='D')
ax.plot(range(T), 0.01*x_hat, label='Estimated States',marker='o')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Distance (m)')
ax.set_title("Comparison of measured data to 1D Kalman Filter")
ax.legend()

plt.show()
