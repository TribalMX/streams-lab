#!/usr/bin/env python

import sys, getopt
import time
from scipy.io import wavfile
from scipy.fftpack import fft
import numpy as np
# from numpy.fft import fft

def log(msg, obj=None):
    print time.asctime(time.localtime(time.time())), msg, obj

# returns a list of timestamps for a moment matching a set of frequency bands
def getmoments(FF, NUMWINDS, EVENTBANDS, bands, BANDMEANS):
    moments = []
    for i in xrange(0, NUMWINDS):
        t = i / FF
        # rank is just the sum of the amplitudes in the relevant
        # bands. TODO. make it a measure of how frequency ratios match
        # the crowd cheering
        rank = 0
        for k in EVENTBANDS:
            rank += bands[k][i]
        moments.append([t, rank])
    return moments

def writemoments(FILE, moments):
    log("INFO. moments.py:writemoments", FILE)
    momentsdat = open(FILE, 'w')
    for m in moments:
        t = m[0]
        rank = m[1]
        momentsdat.write("%d %f\n" % (t, rank))
    momentsdat.close()

def main(argv):
    WAV_FILE = ""
    MOMENTS_FILE= ""
    HELPLINE = 'SCRIPT_NAME.py --audio <WAV_FILE> --moments <MOMENTS_FILE>'
    try:
        opts, args = getopt.getopt(argv, "", ["help", "audio=", "events=", "moments="])
        for opt, arg in opts:
            if opt in ("--help"):
                print(HELPLINE)
                sys.exit(0)
            elif opt in ("--audio"):
                WAV_FILE = arg
            elif opt in ("--moments"):
                MOMENTS_FILE = arg
    except getopt.GetoptError:
        print(HELPLINE)
        sys.exit(1)

    FS, DATA = wavfile.read(WAV_FILE) # FS == sample rate of the audio, e.g. 10000 Hz. todo use FS = 8192 so no need to convert from fft coeffs to freqs
    N = 8192 # number of samples per window
    FF = float(FS) / N # fundamental frequency, also scaling factor between window index i and real time t: i == t * FF

    if len(DATA.shape) == 0:
        print("ERROR. moments.py: audio has no channel")
        sys.exit(1)
    elif len(DATA.shape) == 1:
        CHAN1 = DATA
    else: # has more than 1 channel. TODO. use both channels
        CHAN1 = DATA.T[0]

    NUMWINDS = len(CHAN1) / N

    BANDSIZE = 25 # Hz. width of frequency bands. TODO. try different BANDSIZE
    NUMBANDS = FS / 2 / BANDSIZE # FS / 2 because fft can only resolve up to half the sampling rate FS
    BANDMULT = BANDSIZE * N / FS # conversion factor from band frequency index to fft coefficient index

    bands = [[] for i in range(NUMBANDS)] # NOTE don't use [[]] * NUMBANDS cause all the sublists will point to the same list. very bad

    for i in xrange(0, NUMWINDS):
        t = i / FF
        if i == NUMWINDS - 1: # last window
            b = CHAN1[i * N:]
        else:
            b = CHAN1[i * N:(i + 1) * N]
        c = fft(b * np.hamming(len(b)))
        c = abs(c[:len(c)/2])
        for j in xrange(0, NUMBANDS):
            amp = max(c[j * BANDMULT:(j + 1) * BANDMULT])
            bands[j].append(amp)

    BANDMEANS = [np.mean(b) for b in bands]
    CHEER_BANDS = [43, 44, 45, 46, 47, 48, 49, 50, 51] # for FS == N == 8192

    cheermoments = getmoments(FF, NUMWINDS, CHEER_BANDS, bands, BANDMEANS)
    writemoments(MOMENTS_FILE, cheermoments)

if __name__ == "__main__":
    main(sys.argv[1:])
