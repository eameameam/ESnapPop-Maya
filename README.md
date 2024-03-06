# ESnapPop: Snapping Popup for Maya

The ESnapPop script provides a snapping popup with default modes.

![ESnapPop Window](/ESnapPop.png)

## Features

1. Popup window with quick access to snap modes.
2. Right-click functionality to turn all snapping modes off.
3. Alt key modifier to activate a single snapping mode exclusively.
4. The pop-up window will auto-close once an option is selected or when the cursor moves away, streamlining the workflow.

## Installation

1. Place the `ESnapPop.py` file in the `scripts` folder of your Maya directory.
2. Place the SnapPopIcons folder in the `prefs/icons` folder of your Maya directory.
3. Assign a hotkey in Maya's Hotkey Editor:
   
```python
import ESnapPop
ESnapPop.create_popup_window()
```

## Usage

Press the assigned hotkey, and the ESnapPop window will appear under your cursor, allowing for immediate access to snap mode toggles.
