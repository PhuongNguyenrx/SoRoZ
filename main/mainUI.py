import tkinter as tk
from datetime import timedelta
import asyncio
import time

from mini.dns.dns_browser import WiFiDevice
from maintest import test_connect, shutdown
from maintest import test_get_device_by_name, test_start_run_program, test_change_robot_volume, test_play_audio

class CountdownApp(tk.Tk):
    def __init__(self,loop:asyncio.ProactorEventLoop):
        super().__init__()
        self.loop=loop

        self.title("Water Reminder")
        self.geometry("1200x200")

        self.label = tk.Label(self, text ="Remember to drink water within 1 hour", font=("Helvetica", 48)).pack()

        self.original_time = timedelta(minutes=5)
        self.time_left = self.original_time

        self.loop.create_task(self.countdown())
        # self.countdown()

        self.reset_button = tk.Button(self, text="I have already drunk", command=self.reset_timer)
        self.reset_button.pack(pady=10)

        self.stop_button = tk.Button(self, text="Stop", command=lambda: self.loop.create_task(self.stop()))
        self.stop_button.pack(pady=10)

    async def show(self):
         while True:
            self.update()
            await asyncio.sleep(.1)
            
        
    def reset_timer(self):
        self.time_left = self.original_time
        
    async def stop(self):
        print("Shutting down")
        await shutdown()
        self.loop.stop()
        self.destroy()

    async def countdown(self):
        if self.time_left.total_seconds() > 0:
            self.time_left -= timedelta(seconds=1)
            self.print_time()
            await asyncio.sleep(1)
            await self.countdown()
        else:
            if self.time_left.total_seconds() <= 0:
                await test_play_audio()
                print("Timer expired. Do something. Resetting to 5 seconds then try again.")
                self.time_left = timedelta(minutes=1)
                await self.countdown()

    def print_time(self):
        print(self.time_left)

async def main():
    device: WiFiDevice = await test_get_device_by_name()
    if device:
        await test_connect(device)
        await test_start_run_program()
        await test_change_robot_volume(0.4)
        loop = asyncio.get_event_loop()
        a = CountdownApp(loop)
        await a.show()
        

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except:
        pass
    