# Sound Pong

This is a experimental project developed at the Sonic Thinking course at HPI-UP.

## Description

Sound Pong is a simple pong game in which you can play using your voice as input. The frequency of the vocal sound may command your pallete up or down, and you play against another player which use keyboards as input.

## Setup and run

Install the packages from `requirements.txt`.

```
pip install -r requirements.txt
```

Each person has a different vocal spectrum, therefore you need to make one special adjustment on the code.

Run the `audio_test.py`, make some vocal sounds and whistle to understand the plot behaviour, then adjust the `LOWER_FREQ` and `HIGHER_FREQ` constants to achieve a better comand.
```
LOWER_FREQ = 100    # lower frequency limit of your voice sound 
HIGHER_FREQ = 2000  # higher frequency limit of you whistle sound
```
When you are ready, copy your `LOWER_FREQ` and `HIGHER_FREQ` values to the `sound_pong.py` file and run it.

## Playing

Find another player to play with you!

Left player:
* Produce a whistle to make the palett go up.
* Make a lower sound with your voice to make the palett go up.

Right player:
* Up arrow key to make the palett go up.
* Down arrow key to make the palett go up.