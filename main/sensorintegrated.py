import asyncio
import logging
import serial

import mini.mini_sdk as MiniSdk
from mini.apis import errors
from mini.dns.dns_browser import WiFiDevice
from mini.apis.api_sound import ChangeRobotVolume
from mini.apis.api_sound import FetchAudioList, GetAudioListResponse, AudioSearchType
from mini.apis.api_sound import PlayAudio, PlayAudioResponse, AudioStorageType
from mini.apis.base_api import MiniApiResultType

# Connect & Disconnect
async def test_get_device_by_name():
    result: WiFiDevice = await MiniSdk.get_device_by_name("2356", 10)
    print(f"test_get_device_by_name result:{result}")
    return result

async def test_connect(dev: WiFiDevice) -> bool:
    return await MiniSdk.connect(dev)

async def test_start_run_program():
    await MiniSdk.enter_program()

async def shutdown():
    await MiniSdk.quit_program()
    await MiniSdk.release()

async def prototype(longTimer: int, shortTimer: int, drinkTimer: int, weight_fluctuation:int, ser):
    # Start timer1
    timer1_task = asyncio.create_task(asyncio.sleep(longTimer * 60)) #convert to minutes

    # Initialize variables
    # previous_weight = 0
    weight=0
    drink_countdown_task = None

    while True:
        # Read serial data from Arduino
        if ser.in_waiting > 0:
            weight = int(ser.readline().decode('utf-8').strip())
            print(weight)

            if weight == 0:
                # Start timer2
                drink_countdown_task = asyncio.create_task(asyncio.sleep(drinkTimer*60))

                try:
                    # Wait for either timer2 or weight change
                    done, pending = await asyncio.wait(
                        [drink_countdown_task, asyncio.sleep(0.1)],
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    
                    new_weight = int(ser.readline().decode('utf-8').strip())
                    
                    # If timer2 completed, check weight change
                    if drink_countdown_task in done:
                        drink_countdown_task = None

                        if new_weight == 0:
                            await test_play_audio()
                        else:
                            # Weight changed before timer2 expiration
                            # Cancel the timer2
                            drink_countdown_task.cancel()
                            #if sensor is not working reliably
                            timer1_task.cancel()
                            timer1_task = asyncio.create_task(asyncio.sleep(longTimer*60))

                            # Check if weight changed after putting the bottle back
                            # if abs(weight - previous_weight) > weight_fluctuation:
                            #     # Reset timer1
                            #     timer1_task.cancel()
                            #     timer1_task = asyncio.create_task(asyncio.sleep(longTimer*60))
                            # else:
                            #     # Continue with the rest of your logic or do nothing
                            #     print("Continuing with usual logic")

                except asyncio.CancelledError:
                    # Drink timer was cancelled before expiration
                    pass

            # elif abs(weight - previous_weight) > weight_fluctuation:
            #     # Weight changed, reset timer1
            #     timer1_task.cancel()
            #     timer1_task = asyncio.create_task(asyncio.sleep(longTimer*60))

            #     # Update previous_weight for the next iteration
            #     previous_weight = weight

        # Check if main timer completed
        if timer1_task.done():
            await test_play_audio()
            break

        await asyncio.sleep(0.1)
  
#Functions
async def test_change_robot_volume(volume: float):
    block: ChangeRobotVolume = ChangeRobotVolume(volume=volume)
    (resultType, response) = await block.execute()

    print(f'test_change_volume_result: {response}')

async def test_play_audio():
    
    block: PlayAudio = PlayAudio(
        url='https://audio.jukehost.co.uk/ekqu4z3yTIjKYry8AcPKzp6vgoRrUqzS',
        storage_type=AudioStorageType.NET_PUBLIC)
    # response is a PlayAudioResponse
    (resultType, response) = await block.execute()
    print(f'test_play_local_audio result: {response}')
    print('resultCode = {0}, error = {1}'.format(response.resultCode, errors.get_speech_error_str(response.resultCode)))

async def test_get_audio_list():
    # search_type: AudioSearchType.INNER refers to the unmodifiable sound effect built into the robot, AudioSearchType.CUSTOM is placed in the sdcard/customize/music directory and can be modified by the developer
    block: FetchAudioList = FetchAudioList(search_type=AudioSearchType.INNER)
    # response is a GetAudioListResponse
    (resultType, response) = block.execute()

    print(f'test_get_audio_list result: {response}')

    assert resultType == MiniApiResultType.Success, 'test_get_audio_list timetout'
    assert response is not None and isinstance(response, GetAudioListResponse), 'test_play_audio result unavailable'
    assert response.isSuccess, 'test_get_audio_list failed'
    

MiniSdk.set_log_level(logging.INFO)
MiniSdk.set_robot_type(MiniSdk.RobotType.EDU)


async def main():
    #setupArduino (change COM3 to the right port)
    ser = serial.Serial('COM3', 9600)

    device: WiFiDevice = await test_get_device_by_name()
    if device:
        await test_connect(device)
        await test_start_run_program()
        # await test_change_robot_volume(0.4)

        #main program
        await prototype(60, 5, 10, 50, ser) #longtimer, shorttimer, drinktimer, weight fluc tolerance
        await shutdown()


if __name__ == '__main__':
    asyncio.run(main())
