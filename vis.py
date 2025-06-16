import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from tkinter import Tk, Label, Button, Frame, messagebox, BooleanVar, Checkbutton
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import pandas as pd
import serial
import threading
from tkinter import ttk

class GyroscopeSimulation:
    def __init__(self):
        self.TIME_STEP = 0.01
        self.serial_port = "/dev/ttyUSB0"
        self.baud_rate = 115200
        self.serial_connection = None
        self.gyro_data = np.array([0.0, 0.0, 0.0])  # x, y, z angles in degrees
        self.rotation_matrix = np.eye(3)
        self.history_data = []
        self.is_paused = False
        self.start_time = time.time()
        self.gyro_buffer = []
        self.buffer_size = 5
        self.spin_angle = 0.0
        self.omega_spin = 10.0
        
        self.setup_gui()
        self.setup_plots()
        self.setup_3d_gyroscope()

        self.serial_thread = threading.Thread(target=self.read_serial_data)
        self.serial_thread.daemon = True
        self.serial_thread.start()

    def read_serial_data(self):
        try:
            self.serial_connection = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            time.sleep(2)
            while True:
                if self.serial_connection.in_waiting:
                    line = self.serial_connection.readline().decode().strip()
                    parts = line.split()
                    if len(parts) == 3:
                        try:
                            new_data = np.array(list(map(float, parts)))
                            self.gyro_buffer.append(new_data)
                            if len(self.gyro_buffer) > self.buffer_size:
                                self.gyro_buffer.pop(0)
                            self.gyro_data = np.mean(self.gyro_buffer, axis=0)
                        except ValueError:
                            pass
        except serial.SerialException as e:
            print("Serial connection error:", e)
            messagebox.showerror("Serial Error", f"Failed to connect to {self.serial_port}")

    def setup_gui(self):
        self.root = Tk()

        # Enable axes checkbuttons
        self.enable_x = BooleanVar(value=True)
        self.enable_y = BooleanVar(value=True)
        self.enable_z = BooleanVar(value=True)

        self.root.title("Gyroscope 3-Axis Simulation")
        self.root.configure(bg='#2b2b2b')
        control_frame = Frame(self.root, bg='#2b2b2b')
        control_frame.pack(side='left', fill='y', padx=10, pady=10)

        self.status_label = Label(control_frame, text="Rotation Matrix", font=('Helvetica', 12),
                                  bg='#2b2b2b', fg='white')
        self.status_label.pack(pady=10)

        self.pause_button = Button(control_frame, text="Pause", command=self.toggle_pause,
                                   bg='#4a4a4a', fg='white')
        self.pause_button.pack(pady=5)

        self.reset_button = Button(control_frame, text="Reset", command=self.reset_simulation,
                                   bg='#4a4a4a', fg='white')
        self.reset_button.pack(pady=5)

        self.report_button = Button(control_frame, text="Generate Report", command=self.generate_report,
                                    bg='#4a4a4a', fg='white')
        self.report_button.pack(pady=5)

        # Enable axes checkbuttons
        Label(control_frame, text="Enable Axes:", bg='#2b2b2b', fg='white').pack(pady=5)
        Checkbutton(control_frame, text="X", variable=self.enable_x, bg='#2b2b2b', fg='white', 
                    selectcolor='#4a4a4a').pack(anchor='w')
        Checkbutton(control_frame, text="Y", variable=self.enable_y, bg='#2b2b2b', fg='white', 
                    selectcolor='#4a4a4a').pack(anchor='w')
        Checkbutton(control_frame, text="Z", variable=self.enable_z, bg='#2b2b2b', fg='white', 
                    selectcolor='#4a4a4a').pack(anchor='w')

        self.history_tree = ttk.Treeview(control_frame, columns=("Time", "Angle X (°)", "Angle Y (°)", "Angle Z (°)"), show="headings")
        for col in ["Time", "Angle X (°)", "Angle Y (°)", "Angle Z (°)"]:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100, anchor="center")
        self.history_tree.pack(pady=10)

    def setup_plots(self):
        self.fig = plt.figure(figsize=(10, 6))
        gs = gridspec.GridSpec(1, 1)
        self.ax_3d = self.fig.add_subplot(gs[0], projection='3d')
        self.ax_3d.set_title("3D Gyroscope", color='white')
        self.ax_3d.set_facecolor('#2b2b2b')
        self.ax_3d.set_xlim(-2, 2)
        self.ax_3d.set_ylim(-2, 2)
        self.ax_3d.set_zlim(-2, 2)
        self.fig.patch.set_facecolor('#2b2b2b')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='right', fill='both', expand=True)

    def setup_3d_gyroscope(self):
        theta = np.linspace(0, 2*np.pi, 100)
        r = 1
        self.disk_points = np.vstack((r * np.cos(theta), r * np.sin(theta), np.zeros_like(theta)))
        self.axis_line = np.array([[0, 0], [0, 0], [-1, 1]])
        theta_spokes = np.linspace(0, 2*np.pi, 8, endpoint=False)
        self.spoke_points = np.vstack((r * np.cos(theta_spokes), r * np.sin(theta_spokes), np.zeros_like(theta_spokes)))

    def angles_to_rotation_matrix(self, angles):
        """Convert Euler angles (in degrees) to a rotation matrix (ZYX convention)."""
        roll, pitch, yaw = np.radians(angles)  # Convert degrees to radians
        c_r, s_r = np.cos(roll), np.sin(roll)
        c_p, s_p = np.cos(pitch), np.sin(pitch)
        c_y, s_y = np.cos(yaw), np.sin(yaw)
        # ZYX rotation matrix (yaw about Z, pitch about Y, roll about X)
        R = np.array([
            [c_y*c_p, c_y*s_p*s_r - s_y*c_r, c_y*s_p*c_r + s_y*s_r],
            [s_y*c_p, s_y*s_p*s_r + c_y*c_r, s_y*s_p*c_r - c_y*s_r],
            [-s_p,    c_p*s_r,              c_p*c_r]
        ])
        return R

    def apply_rotation(self):
        """Update rotation matrix based on current angles."""
        modified_angles = np.array([
            self.gyro_data[0] if self.enable_x.get() else 0.0,
            self.gyro_data[1] if self.enable_y.get() else 0.0,
            self.gyro_data[2] if self.enable_z.get() else 0.0
        ])
        self.rotation_matrix = self.angles_to_rotation_matrix(modified_angles)

    def update_3d_gyroscope(self):
        c, s = np.cos(self.spin_angle), np.sin(self.spin_angle)
        R_spin = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        spun_disk = R_spin @ self.disk_points
        rotated_disk = self.rotation_matrix @ spun_disk
        spun_spokes = R_spin @ self.spoke_points
        rotated_spokes = self.rotation_matrix @ spun_spokes
        rotated_axis = self.rotation_matrix @ self.axis_line

        self.ax_3d.cla()
        self.ax_3d.plot(rotated_disk[0], rotated_disk[1], rotated_disk[2], 'g-', lw=2)
        for i in range(rotated_spokes.shape[1]):
            self.ax_3d.plot([0, rotated_spokes[0, i]], [0, rotated_spokes[1, i]], 
                           [0, rotated_spokes[2, i]], 'b-', lw=1)
        self.ax_3d.plot(rotated_axis[0], rotated_axis[1], rotated_axis[2], 'r-', lw=2)
        self.ax_3d.set_xlim(-2, 2)
        self.ax_3d.set_ylim(-2, 2)
        self.ax_3d.set_zlim(-2, 2)
        self.ax_3d.set_xlabel("X")
        self.ax_3d.set_ylabel("Y")
        self.ax_3d.set_zlabel("Z")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.pause_button.config(text="Resume" if self.is_paused else "Pause")

    def reset_simulation(self):
        self.rotation_matrix = np.eye(3)
        self.history_data = []
        self.start_time = time.time()
        self.spin_angle = 0.0
        self.gyro_buffer = []
        self.canvas.draw()

    def update_history(self):
        t = time.time() - self.start_time
        gx, gy, gz = self.gyro_data
        self.history_data.append([round(t, 2), round(gx, 2), round(gy, 2), round(gz, 2)])
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)
        for row in self.history_data[-10:]:
            self.history_tree.insert('', 'end', values=row)

    def simulate(self):
        if not self.is_paused:
            self.spin_angle += self.omega_spin * self.TIME_STEP
            self.apply_rotation()
            self.update_3d_gyroscope()
            self.update_history()
            self.canvas.draw()
        self.root.after(int(self.TIME_STEP * 1000), self.simulate)

    def generate_report(self):
        if not self.history_data:
            messagebox.showinfo("Report", "No data available yet!")
            return
        df = pd.DataFrame(self.history_data, columns=["Time", "Angle X (°)", "Angle Y (°)", "Angle Z (°)"])
        stats = df.describe()
        messagebox.showinfo("Report", f"{stats}")
        df.to_csv("gyroscope_3d_data.csv", index=False)

    def run(self):
        self.simulate()
        self.root.mainloop()

if __name__ == "__main__":
    GyroscopeSimulation().run()
