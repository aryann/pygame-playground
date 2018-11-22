import pyaudio
import numpy
import matplotlib.pyplot as plt

CHUNK = 1024 * 2
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = int(44100 / 2)
RECORD_SECONDS = 1000
WAVE_OUTPUT_FILENAME = "output.wav"


def display_plots():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

    frames = []

    plt.ion()
    plt.show()
    plt.figure(figsize=(15, 15))
    
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = numpy.fromstring(stream.read(CHUNK), dtype=numpy.int16)
        peak = numpy.average(numpy.abs(data)) * 2
        fourier_transform = numpy.fft.rfft(data)
        ft_db = numpy.abs(fourier_transform)
        freq_bins = numpy.fft.rfftfreq(data.shape[-1], d=1 / RATE)
        
        plt.clf()
        plt.ylim([0, 1000000])
        plt.xlim([300, 3400])  # human voice range in Hz
        plt.plot(freq_bins, ft_db)
        plt.draw()
        plt.pause(0.01)
        

    stream.stop_stream()
    stream.close()
    p.terminate()
    


if __name__ == '__main__':
    display_plots()
