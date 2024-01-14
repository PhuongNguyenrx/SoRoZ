import asyncio
import logging

import mini.mini_sdk as MiniSdk
from pytimedinput import timedInput
from mini.apis import errors
from mini.dns.dns_browser import WiFiDevice
from mini.apis.api_sound import ChangeRobotVolume
from mini.apis.api_sound import FetchAudioList, GetAudioListResponse, AudioSearchType
from mini.apis.api_sound import PlayAudio, PlayAudioResponse, AudioStorageType
from mini.apis.base_api import MiniApiResultType

# Setting up
async def test_get_device_by_name():
    result: WiFiDevice = await MiniSdk.get_device_by_name("2356", 10)
    print(f"test_get_device_by_name result:{result}")
    return result

async def test_connect(dev: WiFiDevice) -> bool:
    return await MiniSdk.connect(dev)

async def test_start_run_program():
    await MiniSdk.enter_program()

async def prototype(timer:int):
    userInput,timedOut= timedInput("Timer starts",timeout=timer,resetOnInput=False)
    if (timedOut):
        await test_play_audio()
        await prototype(10)
    elif userInput == "C":
        await shutdown()
    else:   
        await prototype(40)
  
async def test_change_robot_volume(volume: float):
    block: ChangeRobotVolume = ChangeRobotVolume(volume=volume)
    (resultType, response) = await block.execute()

    print(f'test_change_volume_result: {response}')

async def test_play_audio():
    
    # block: PlayAudio = PlayAudio(
    #     url='https://audio.jukehost.co.uk/ekqu4z3yTIjKYry8AcPKzp6vgoRrUqzS',
    #     storage_type=AudioStorageType.NET_PUBLIC)
    # NL
    block: PlayAudio = PlayAudio(
        url='https://audio.jukehost.co.uk/lIlfxyLCtfCj76jlXaDhmxBLWAyPBHbK',
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
    
async def shutdown():
    await MiniSdk.quit_program()
    await MiniSdk.release()

MiniSdk.set_log_level(logging.INFO)
MiniSdk.set_robot_type(MiniSdk.RobotType.EDU)


async def main():
    
    device: WiFiDevice = await test_get_device_by_name()
    if device:
        await test_connect(device)
        await test_start_run_program()
        await test_change_robot_volume(0.4)
        await prototype(40)
        await shutdown()


if __name__ == '__main__':
    asyncio.run(main())
