#   Media Player

-   author: ITWorks4U
-   current version:    *0.5.12.5*
-   written with Python3 (at least with version 3.11.5) for Windows as well as or UNIX/Linux and macOS (expected)

### table of content
1.  general
2.  required modules
3.  how to run
4.  difference between Windows and Linux
5.  origin purpose

### 1.  general
-   runs on Windows, Linux, macOS (expected)
-   playing mp3 files from a detected USB drive
    -   can also be used for playing mp3 files from a local drive as well
-   uses the module *pygame*
-   comes with a config file for:
    -   logging
    -   mount point USB drive (can also be a local drive)
    -   playing the music in a random order
-   you can also use a customized config file as well, **where** the required keys are **must** be identical 
-   comes with signal handling for handling interrupts and process termination to ensure a clean application termination

### 2.  required modules

| module | version | additional informations |
| - | - | - |
| pygame | 2.1.6 (current) | basic module to offer to play mp3 files |
> If this module is missing, then the player can't be used and the application terminates with error code 1.

### 3.  how to run
-   minimal usage: ```python[3.exe] main.py```
-   additional first argument can be ```[[-h | --help |/?] [-c | --create] [custom config file]]```, where:
    -   ```[-h | --help |/?]```: displaying help and terminate with 0
    -   ```[-c | --create]```: create a new config file, located in settings/ and terminate with 0
        -   **This will also overwrite the already existing config file!**
    -   ```[custom config file]```: use a custom config file, where the **keys** must be identical
-   by default, this project comes with a predefined config file
-   depending on required modules and given config settings, the player starts to play the music, if at least one mp3 file has been found
    -   does not repeat the same audio file
    -   does not comes with volume control

### 4.  difference between Windows and UNIX/Linux
-   since Windows does not handle with methods 1:1 like Linux, there're some special methods for Windows only:
    -   on initialize detect the plugged in USB drive
    >   At this point only the first USB drive is in use only.
    >   You can also use a local drive, if you like.
    -   on runtime check, if the detected USB drive has suddenly been removed to stop playing music and terminate the application
    >   If a local drive is in use, this check is not completly in use instead.

### 5.  origin purpose
-   usually, this project was planned to run on a Rasbperry Pi (4, model B) as an own media player, when at any time an USB device has been plugged in to play all media files in a random order