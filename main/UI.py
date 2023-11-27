import tkinter as tk
from datetime import timedelta
import asyncio

from mini.dns.dns_browser import WiFiDevice
from maintest import test_connect, shutdown
from maintest import test_get_device_by_name, test_start_run_program, test_change_robot_volume, test_play_audio

class CountdownApp:
    def __init__(self,root):
        self.root=root
        self.original_time = timedelta(seconds=10)
        self.time_left = self.original_time

        self.countdown()

        self.reset_button = tk.Button(root, text="Reset", command=self.reset_timer)
        self.reset_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop", command= self.stop)
        self.stop_button.pack(pady=10)

    def reset_timer(self):
        self.time_left = self.original_time
        
    def stop(self):
        print("Shutting down")
        self.root.destroy()
        asyncio.get_event_loop().run_until_complete(shutdown())

    def countdown(self):
        if self.time_left.total_seconds() > 0:
            self.time_left -= timedelta(seconds=1)
            self.print_time()
            self.root.after(1000, self.countdown)
        else:
            if self.time_left.total_seconds() <= 0:
                asyncio.get_event_loop().run_until_complete(test_play_audio())
                print("Timer expired. Do something. Resetting to 5 seconds then try again.")
                self.time_left = timedelta(seconds=5)
                self.countdown()

    def print_time(self):
        print(self.time_left)

async def main():
    device: WiFiDevice = await test_get_device_by_name()
    if device:
        await test_connect(device)
        await test_start_run_program()
        await test_change_robot_volume(0.4)
        root = tk.Tk()
        app = CountdownApp(root)
        root.mainloop()
     


if __name__ == '__main__':
    asyncio.run(main())
    