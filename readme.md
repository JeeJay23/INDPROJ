# DSP node editor

The DSP node editor is a python application which leverages the gpus parallel processing power to apply audio filters to a live audio stream. Currently it can generate sine waves, apply filters and visualize the frequency spectrum of the audio. These operations are all performed on the gpu.

## Features
* Node based editing system
* Sine wave generator
* Audio visualization
* Frequency spectrum visualization
* Low pass filter
* Gain filter

## Installation
1. Clone the repository
2. Create a virtual environment

```bash
python -m venv path/to/venv
# activate the virtual environment
./path/to/venv/Scripts/activate
# install the dependencies
pip install -r requirements.txt
# run the application from the root of the project
python src/node_editor.py
```
## Usage
Add nodes from de add menu to the interface. Connect the nodes by dragging a connection from the output of one node to the input of another. Adding a connection to an audio output node will play the audio.

## Improvements
* There is a clicking sound when audio processed by the gpu is played back. This could be because of the lack of synchronization between the gpu and the audio output.
* Not all filters have a corresponding node in the node editor. 