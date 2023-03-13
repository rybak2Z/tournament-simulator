# Dependency imports
import PySimpleGUI as sg

# Local project imports
import window_layouts as winlay
import event_handlers as eh
from ThreadSharedData import ThreadSharedData as tsd
from Competitor import Competitor


window = sg.Window("Competition Simulator",
                   winlay.layout,
                   text_justification='center',
                   element_justification='center',
                   size=(1080, 650))

# Set up shared data
tsd.init()
tsd.set('window', window)
tsd.set('winner', None)

# (For the event loop) Dict with key-function-pairs to avoid if-elif-else structure in event loop
event_handling_functions = {
    '-B_FOLDER-'            : eh.choose_folder,
    '-B_TEXT-'              : eh.competitors_per_text,
    '-B_RUN_SECONDARY-'     : eh.run_secondary,
    '-B_RANKS_PREV-'        : eh.ranks_previous,
    '-B_RANKS_NEXT-'        : eh.ranks_next,
    '-B_SAVE-'              : eh.save,
    
    '-T_NEW_COMPS-'         : eh.thread_new_competitors,
    '-T_WINNER-'            : eh.thread_winner,
    '-T_FINISHED_SECONDARY-': eh.thread_finished_secondary,
    
    '-IMG_L-'               : eh.clicked_image,
    '-IMG_R-'               : eh.clicked_image
}

# Run event loop
while True:
    event, values = window.read()
    
    if event == sg.WIN_CLOSED or event.startswith('-EXIT'):  # If user wants to exit
        break
    else:
        try:
            event_handling_functions[event](window, event, values)
        except KeyError:
            print(f"Warning: Unsupported event: '{event}'")

# Clean up
try:
    Competitor.delete_files()
except FileNotFoundError:    # If exited before end
    print("Warning: Could not delete file")
window.close()
