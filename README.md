# flicker

<p align=center>
<img src=./images/device-cartoon.jpg width=30% />
</p>


### Summary
During a lucid dream, the dreamer can control their physical eyes by performing directed eye movements within the dream. We built a closed-loop device, _flicker_, to be worn during sleep that monitors for intentional horizontal saccades (i.e., [“flicks”](#how-to-flick)). Upon flick detection, the device plays audio back to the dreamer via bone conduction. Bone conduction plays audio by vibrating bones in the skull rather than the conversion of sound waves through the ear, which results in a sensation of audio playing from “inside the head.” Because the audio can be triggered within the dream, a benefit of _flicker_ is that one can perform external sensory stimulation experiments without an experimenter triggering the stimulation. See [usage](#usage).

The **hardware** is primarily a combination of Arduino microcontroller, MyoWare muscle sensor, and Adafruit audio amplifier (see [parts list](#parts-list)). Outside of the Arduino code placed on the Teensy board, all **software** is in Python (see [conda environment file](./environment.yml) for requirements) driven largely by [PyQt](https://riverbankcomputing.com/software/pyqt/intro), [PyQtGraph](http://www.pyqtgraph.org/), and a [custom "flick detection" algorithm](./src/detectorClass.py) using the [SciPy stack](https://www.scipy.org/).

<p align=center>
<img src=./images/device-wear.jpg width=18% align=center />
<img src=./images/gui-lrlr.png width=60% align=center />
</p>


### Usage
1. Secure sensor near right eye and stimulator on forehead.
2. Start listening for flicks. `$ python runall.py`
3. Go to sleep, become lucid, [send a flick signal](#how-to-flick), and listen for audio.
4. Wake up and end the session by X'ing out the _flicker_ GUI.
5. Check the log file (using any text editor) to see if your flick was detected.


### How to flick
See section 9.1 of [Baird et al., 2019](https://doi.org/10.1016/j.neubiorev.2019.03.008) for in-depth discussion about signaling with eye movements from within a lucid dream. Here, we adopt their suggested set of instructions for sending a signal from a lucid dream:
> When making an eye movement signal, we would like you to look all the way to the left then all the way to the right two times consecutively, as if you are looking at each of your ears. Specifically, we would like you to look at your left ear, then your right ear, then your left ear, then your right ear, and then finally back to center. Make the eye movements without moving your head, and make the full left-right-left-right-center motion as one rapid continuous movement without pausing.

The EOG signal typically results in something like this:
<img src=./images/baird2019-fig1_lrlr.png width=10% align=top />

But because of the MyoWare sensor's on-board processing, in *flicker*'s case it should look something like this:
<img src=./images/lrlr.png width=10% align=top />


### Parts list
The circuit board was designed using [Autodesk EAGLE](https://www.autodesk.com/products/eagle/overview) and ordered through [OSH Park](https://oshpark.com/). Design files/specifications are available in the [design](./design/) directory. Custom casings for the [controller](https://cad.onshape.com/documents/ed15d5b42aa4e13c9ebdd001/w/4501215e34b319a0e4282dd3/e/fc6b625667ca0f5b9852f31f) and [sensor](https://cad.onshape.com/documents/ed15d5b42aa4e13c9ebdd001/w/4501215e34b319a0e4282dd3/e/f00a7b5da7534cec24908e40) were designed using [Onshape](https://www.onshape.com/) and 3D printed locally. The USB isolator case design was pulled from [cyrusdreams](https://www.thingiverse.com/thing:1592996) on [Thingiverse](https://www.thingiverse.com/).

| part | description | price |
| ---- | ----------- | ----: |
| [Teensy 3.6](https://www.pjrc.com/store/teensy36.html) | microcontroller board | 30 |
| [MyoWare muscle sensor](https://www.sparkfun.com/products/13723) | EOG sensor | 38 |
| [Adafruit TPA2012](https://www.adafruit.com/product/1552) | audio amplifier | 10 |
| [Soberton E-12041808](https://www.soberton.com/e-12041808/) | bone conduction speaker | 3 |
| [Adafruit USB isolator](https://www.adafruit.com/product/2107) | safety | 35 |
| [Miscellaneous](#link2wikipage) | &nbsp; | 20 |
| &nbsp; | &nbsp; | **$136** |

<p align=center>
<img src=./images/device.jpg width=15% align=center />
<img src=./images/base-open.jpg width=15% align=center />
<img src=./images/sensor-under.jpg width=15% align=center />
<img src=./images/sensor-wear.jpg width=15% align=center />
<img src=./images/device-wear.jpg width=15% align=center />
</p>


<br><br>

---
<p align=center>
<img src=https://imgs.xkcd.com/comics/tcmp.png width=90% />
</p>
<center><a href=https://xkcd.com/269/>xkcd</a></center>