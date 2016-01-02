PPM Adapter
===========

This is a userspace application that reads the PPM audio stream produced by
many RC controllers, and produces a virtual joystick using the uinput system.

Firstly
-------

Ignore any input like the following, it is a consequence of using the Port Audio library from what I can tell.:: 

        ALSA lib pcm.c:2267:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.rear
        ALSA lib pcm.c:2267:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.center_lfe
        ALSA lib pcm.c:2267:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.side
        ALSA lib pcm_route.c:867:(find_matching_chmap) Found no matching channel map
        Cannot connect to server socket err = No such file or directory
        Cannot connect to server request channel
        jack server is not running or cannot be started


Usage
-----

You may have to give your user access to the /dev/uinput device. This is beyond the scope of this document, but there are options using udev rules, or just chmod. 

You can use the built in microphone port, or the USB one provided with some (cheap?) adapters. To see a list of candidate input devices type::
               
        python -m ppmadapter inputs
        
You will get a list like this::

        HDA ATI SB: VT2020 Analog (hw:0,0)
        HDA ATI SB: VT2020 Digital (hw:0,1)
        HDA ATI SB: VT2020 Alt Analog (hw:0,2)
        HDA NVidia: HDMI 0 (hw:1,3)
        HDA NVidia: HDMI 0 (hw:1,7)
        HDA NVidia: HDMI 0 (hw:1,8)
        HDA NVidia: HDMI 0 (hw:1,9)
        USB Headphone Set: Audio (hw:2,0)
        sysdefault
        front
        surround21
        surround40
        surround41
        surround50
        surround51
        surround71
        iec958
        spdif
        pulse
        dmix
        default

Then, to start the application with a specific card::

        python -m ppmadapter -i hw:2 run

A partial match will be done on the name to find the right adapter. At this point if you run ``dmesg`` you should see something like the following, indicating that the device has been created.::

        input: ppmadapter as /devices/virtual/input/input62

License
-------
GPL v3


