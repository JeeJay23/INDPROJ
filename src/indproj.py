import pyopencl as cl
import dearpygui as dpg
import pyaudio

platforms = cl.get_platforms()
for platform in platforms:
    print("Platform:", platform.name)
    devices = platform.get_devices()
    for device in devices:
        print("  Device:", device.name)
