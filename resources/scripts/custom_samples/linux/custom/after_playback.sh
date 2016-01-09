#!/bin/bash

# raise the volume to the previous level
pamixer --increase 10

# kill teh current keybindings that were used just for netflix
killall -KILL xbindkeys
