# Quick Start Guide

1. Install **Python 3.10** or newer and make sure **ffmpeg** can run from the command line.
2. Copy your `PokemonRed.gb` game file into this folder.
3. Open a terminal, go into the `v3` directory:
   ```
   cd v3
   ```
4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
5. Start the pretrained agent:
   ```
   python run_pretrained_interactive.py
   ```
6. Use the arrow keys to move. Press **a** for the A button and **s** for the B button.
   To pause the AI, open `agent_enabled.txt` and change `yes` to `no`.

Have fun exploring!
