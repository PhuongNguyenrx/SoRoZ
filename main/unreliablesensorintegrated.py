import asyncio
import logging
import serial

import mini.mini_sdk as MiniSdk
from mini.apis import errors
from mini.dns.dns_browser import WiFiDevice
from mini.apis.api_sound import ChangeRobotVolume
from mini.apis.api_sound import PlayAudio, PlayAudioResponse, AudioStorageType
from mini.apis.base_api import MiniApiResultType

# <summary>
# Main prototype being used currently (with sensor)
# </summary>

# Connect & Disconnect
async def test_get_device_by_name():
    result: WiFiDevice = await MiniSdk.get_device_by_name("2356", 10) #replace with robot ID (last numbers)
    print(f"test_get_device_by_name result:{result}")
    return result

async def test_connect(dev: WiFiDevice) -> bool:
    return await MiniSdk.connect(dev)

async def test_start_run_program():
    await MiniSdk.enter_program()

async def shutdown():
    await MiniSdk.quit_program()
    await MiniSdk.release()

# Main program
async def prototype(longTimer: int, shortTimer: int, drinkTimer: int, weight_fluctuation:int, ser):
    # Start timer1
    timer_task = asyncio.create_task(asyncio.sleep(longTimer*60)) #convert to minutes

    # Initialize variables
    # previous_weight = 0
    weight=0
    drink_countdown_task = None

    try:
        while True:
            # Read serial data from Arduino
            if ser.in_waiting > 0:
                weight = int(ser.readline().decode('utf-8').split('=')[-1].strip())
                print(weight)

                if weight == 0:
                    # Start timer2
                    timer_task.cancel()
                    drink_countdown_task = asyncio.create_task(asyncio.sleep(drinkTimer*60))
                    print("Bottle lifted")

                try:
                    while not drink_countdown_task.done():
                        new_weight = int(ser.readline().decode('utf-8').split('=')[-1].strip())

                        if new_weight != 0:
                            # If weight changes during the countdown, cancel the task and reset timers
                            drink_countdown_task.cancel()
                            timer_task = asyncio.create_task(asyncio.sleep(longTimer*60))
                            print("Reset the timer")
                            break  

                        await asyncio.sleep(0.1)  # Small delay to avoid constant polling

                    # If the countdown completes without weight change, play audio
                    if drink_countdown_task.done() and new_weight == 0:
                        print("Bottle not measuring")
                        await put_bottle_down_audio()
    
                except KeyboardInterrupt:
                    await shutdown()

            if timer_task.done() and not timer_task.cancelled():
                print("Need to drink")
                await play_reminder_audio()
                
                timer_task.cancel()

                timer_task = asyncio.create_task(asyncio.sleep(shortTimer*60))

            await asyncio.sleep(0.1)

    except KeyboardInterrupt:
        await shutdown()

#Functions
async def test_change_robot_volume(volume: float):
    block: ChangeRobotVolume = ChangeRobotVolume(volume=volume)
    (resultType, response) = await block.execute()

    print(f'test_change_volume_result: {response}')

async def play_reminder_audio():
    
    block: PlayAudio = PlayAudio(
        url='https://audio.jukehost.co.uk/ekqu4z3yTIjKYry8AcPKzp6vgoRrUqzS',
        storage_type=AudioStorageType.NET_PUBLIC)
    #NL
    # block: PlayAudio = PlayAudio(
    #     url='https://audio.jukehost.co.uk/hvc12qSsSK1eEnEWA7Pio9IuSa9iHSzv',
    #     storage_type=AudioStorageType.NET_PUBLIC)
    
    (resultType, response) = await block.execute()
    print(f'test_play_local_audio result: {response}')
    print('resultCode = {0}, error = {1}'.format(response.resultCode, errors.get_speech_error_str(response.resultCode)))

async def put_bottle_down_audio():
    
    block: PlayAudio = PlayAudio(
        url='https://audio.jukehost.co.uk/CnIGEqhQqdcc0TvebF8SKBx7ZAtemQ1y',
        storage_type=AudioStorageType.NET_PUBLIC)
    #NL
    # block: PlayAudio = PlayAudio(
    #     url='https://audio.jukehost.co.uk/io4M8f37pYS8p6NB2hzulVm7xtECfHKq',
    #     storage_type=AudioStorageType.NET_PUBLIC)

    (resultType, response) = await block.execute()
    print(f'test_play_local_audio result: {response}')
    print('resultCode = {0}, error = {1}'.format(response.resultCode, errors.get_speech_error_str(response.resultCode)))

MiniSdk.set_log_level(logging.INFO)
MiniSdk.set_robot_type(MiniSdk.RobotType.EDU)


async def main():
    #setupArduino (change COM3 to the right port)
    ser = serial.Serial('COM5', 9600)

    device: WiFiDevice = await test_get_device_by_name()
    if device:
        await test_connect(device)
        await test_start_run_program()
        # await test_change_robot_volume(0.4)

        #main program
        await prototype(0.2, 0.1, 0.1, 50, ser) #longtimer, shorttimer, drinktimer, weight fluc tolerance
        await shutdown()

if __name__ == '__main__':
    asyncio.run(main())
