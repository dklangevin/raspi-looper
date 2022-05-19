import pyaudio
from noalsaerr import noalsaerr
from test_gpio import setup_gpio    # Setup gpio pins with custom function
import numpy as np
import itertools

CHUNK = 32

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
DEVICE_INDEX = 1
LOOP_COUNT = 2
MAX_I = int(RATE / CHUNK * RECORD_SECONDS)

AUDIO_INTERFACE_NAME = 'USB Audio CODEC'

BUTTON_PINS = {
        31: 1,
        33: 2,
        35: 3,
        37: 4
}

with noalsaerr():
    p = pyaudio.PyAudio()

# Open stream
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK,
    input_device_index=DEVICE_INDEX,
    output_device_index=DEVICE_INDEX
)

def is_audio_interface_detected():
    global DEVICE_INDEX
    device_cnt = p.get_device_count()
    for i in range(0, device_cnt):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            if AUDIO_INTERFACE_NAME in p.get_device_info_by_host_api_device_index(0, i).get('name'):
                DEVICE_INDEX = i
                return True
    return False

def run(channel):

    if is_audio_interface_detected():

        print('Device index:', DEVICE_INDEX)

        print(f'Button {BUTTON_PINS[channel]} pressed!')

        print(f'Recording for {RECORD_SECONDS} seconds...')
        print(f'Chunk size: {CHUNK}')   

        # First loop
        signal = [0] * MAX_I
        for i in range(0, MAX_I):
            data = stream.read(CHUNK, exception_on_overflow = False)
            stream.write(data, CHUNK)
            data = np.frombuffer(data, dtype='int16')
            signal[i] = data

        # Subsequent loops
        print('Looping...')
        for loop in range(LOOP_COUNT - 1):
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK, exception_on_overflow = False)
                signal[i] = (signal[i] + np.frombuffer(data, dtype='int16')).astype(np.int16)
                data = signal[i].tobytes()
                stream.write(data, CHUNK)

        print('Done')
    
    else:
        print('Audio interface is not detected!')

    # Clean up
    stream.stop_stream()
    stream.close()
    p.terminate()





setup_gpio(run)