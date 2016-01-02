# PPMAdapter - An RC PPM decoder and joystick emulator
# Copyright 2016 Nigel Sim <nigel.sim@gmail.com>
#
# PPMAdapter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PPMAdapter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PPMAdapter.  If not, see <http://www.gnu.org/licenses/>.

import pyaudio
import argparse
import sys
from evdev import UInput, ecodes
import struct


class PPMDecoder(object):
    """Decodes the audio data into PPM pulse data, and then into uinput
    joystick events.
    """
    def __init__(self, rate):
        """
        Parameters
        ----------
        rate : int
            sample rate
        """
        self._rate = float(rate)
        self._lf = None
        self._t = 0
        self._threshold = 15000
        self._last = None
        self._ch = None

        # Size in sampling intervals, of the frame space marker
        self._marker = int(2.0 * 0.0025 * self._rate)

        # Mapping of channels to events
        self._mapping = {0: ecodes.ABS_X,
                         1: ecodes.ABS_Y,
                         2: ecodes.ABS_Z,
                         3: ecodes.ABS_THROTTLE}

        events = [(v, (0, 255, 5, 0)) for v in self._mapping.values()]

        self._ev = UInput(name='ppmadapter',
                          events={
                                  ecodes.EV_ABS: events,
                                  ecodes.EV_KEY: {288: 'BTN_JOYSTICK'}
                          })

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self._ev.close()

    def feed(self, data):
        """Feeds the decoder with a block of sample data.

        The data should be integer values, and should only be a single channel.

        Parameters
        ----------
        data : list
            sample data
        """
        for i in range(len(data)):
            this = data[i] > self._threshold
            if self._last is None:
                self._last = this
                continue

            t = self._t + i
            if this and not self._last:
                # rising
                if self._lf is not None:
                    self.signal(t - self._lf)
            elif not this and self._last:
                # falling
                self._lf = t

            self._last = this

        self._t = self._t + len(data)

    def signal(self, w):
        """Process the detected signal.

        The signal is the number of sampling intervals between the falling
        edge and the rising edge.

        Parameters
        ----------
        w : int
            signal width
        """
        if w > self._marker:
            self._ch = 0
            self._ev.syn()
            return

        if self._ch is None or self._ch not in self._mapping:
            return

        duration = float(w) / self._rate
        value = int((duration - 0.0007) * 1000 * 255)
        self._ev.write(ecodes.EV_ABS, self._mapping[self._ch], value)

        self._ch += 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help="input audio device name", default='default')
    parser.add_argument('action', default='run', choices=['run', 'inputs'])

    args = parser.parse_args()

    if args.action == 'inputs':
        print("Input audio devices")
        print("-------------------")
        a = pyaudio.PyAudio()
        for i in range(a.get_device_count()):
            d = a.get_device_info_by_index(i)
            print d['name']

        return 0

    in_ix = None
    rate = None
    in_name = None
    a = pyaudio.PyAudio()
    for i in range(a.get_device_count()):
        d = a.get_device_info_by_index(i)
        if args.i == d['name']:
            in_ix = d['index']
            rate = int(d['defaultSampleRate'])
            in_name = d['name']
            break
        if args.i in d['name']:
            in_ix = d['index']
            rate = int(d['defaultSampleRate'])
            in_name = d['name']

    print("Using input: %s" % in_name)

    chunk = 8192

    stream = a.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk,
                    input_device_index=in_ix)

    try:
        with PPMDecoder(rate) as ppm:
            while True:
                sample = stream.read(chunk)
                sample = struct.unpack('%dh' % (len(sample)/2, ), sample)
                ppm.feed(sample)
    finally:
        stream.close()

if __name__ == '__main__':
    sys.exit(main())
