import tkinter as tk
import socket
import time
import threading
from gui import MQTT_GUI

from socks import SOCKS

gui = MQTT_GUI()

if __name__ == "__main__":
    gui.root.mainloop()

