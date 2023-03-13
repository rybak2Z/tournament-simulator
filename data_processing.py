# Dependencies
import os
import time

# Local project imports
from Competitor import Competitor
from CompetitionManager import CompetitionManager
from ThreadSharedData import ThreadSharedData as tsd


DELAY_WAIT_FOR_WINNER = 0.1    # Time period after which the 2nd thread should check if a winner has been evaluated


def is_valid_folder(path: str) -> (bool, str):
    """Checks if the given folder/directory-path is valid (if it contains valid contents)."""
    
    file_names = os.listdir(path)
    
    # Check if folder contains only images and count num of image files
    img_file_counter = 0
    for file_name in file_names:
        if not file_name.endswith(('.png', '.jpg', '.jpeg')):
            return (False, "The folder can only contain image files (.png, .jpg) and nothing else.")
        else:
            img_file_counter += 1
    
    # Check if there are at least 2 image files
    if img_file_counter < 2:
        return (False, "The folder must contain at least two image files (.png, .jpg).")
    
    # If no check failed
    return (True, "")


def prepare_competition(path: str, image_resolution: tuple[int, int]) -> CompetitionManager:
    """Extracts the competitors' information of the folder at the given path and creates a CompetitionManager
    object."""
    
    # Get competitors
    file_names = os.listdir(path)
    competitors = []
    for f_name in file_names:
        new_comp = Competitor(path=path+'/'+f_name, img_resolution=image_resolution)
        competitors.append(new_comp)
    
    return CompetitionManager(competitors)


def evaluate_winner(comp_1: Competitor, comp_2: Competitor) -> Competitor:
    """This will only be called by the 2nd thread. It evaluates the winner of the current match by indirectly waiting
    for the user input."""
    
    # Send event & value to window
    tsd.get('window').write_event_value(key='-T_NEW_COMPS-', value=(comp_1, comp_2))
    # Share competitors
    tsd.set('comps', (comp_1, comp_2))
    
    # Wait for the user to choose a winner
    winner = None
    while winner is None:
        time.sleep(DELAY_WAIT_FOR_WINNER)
        winner = tsd.get('winner')
    # Reset winner
    tsd.set('winner', None)
    
    return winner
