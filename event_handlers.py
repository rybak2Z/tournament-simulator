import PySimpleGUI as sg
from copy import deepcopy
import threading
import os
import cv2

# Local project imports
import window_layouts as winlay
import data_processing as dp
from ThreadSharedData import ThreadSharedData as tsd

# For typing
from typing import Optional
from Competitor import Competitor
from CompetitionManager import CompetitionManager


# Helper functions #####################################################################################################

def popup_folder_location() -> Optional[str]:
    """Creates a popup that lets the user browse for a folder/directory.
    Also checks if the folder is valid (contains valid contents)."""
    # Create window to gather folder location information
    popup_window = sg.Window("Choose folder", deepcopy(winlay.popup_folder_browser),
                             modal=True)  # modal=True makes other windows inaccessible
    
    # Show window and gather information
    popup_event, popup_values = popup_window.read()
    popup_window.close()
    
    # Handle event and values (closing the window with the cancel button or the x is ignored)
    if popup_event == '-SUBMIT-':
        # Try to get folder path
        try:
            path = popup_values['-BROWSE-']
        except KeyError:
            return
        
        # Process data in folder if valid path is given
        path_is_valid, error_message = dp.is_valid_folder(path)
        if path_is_valid:
            return path
        else:
            print(error_message)  # TODO: Remove later?


def get_ranking_images(window: sg.Window) -> list[sg.Image]:
    """Returns the sg.Image objects of the sub-layout with key '-COL_END_2-'."""
    return [window[f'-COMP_{key_suffix}-'] for key_suffix in ('LEFT', 'MID', 'RIGHT')]


def get_ranking_titles(window: sg.Window) -> list[sg.Text]:
    """Returns the sg.Text objects of the sub-layout with key '-COL_END_2-' that are supposed to display the
    titles of the shown competitors."""
    return [window[f'-RANKS_TITLE_{key_suffix}-'] for key_suffix in ('LEFT', 'MID', 'RIGHT')]


# Start layout events ##################################################################################################

def choose_folder(window: sg.Window, event: str, values: dict):
    """Lets the user browse for a folder/directory and then extracts its data (competitors images).
    Next, a CompetitionManager object is created that is also run by a new thread.
    Also switched to main layout."""
    
    folder_path = popup_folder_location()  # TODO: Give user error message?
    if folder_path is not None:
        # Add path to window metadata (so that if the user later wants to save the ranking, we know the path)
        window.metadata = folder_path
        
        # Create competition manager and add to shared data
        competition_manager = dp.prepare_competition(folder_path, winlay.IMG_RES_MATCH)
        tsd.set('cm', competition_manager)
        
        # Create new thread that runs the competition
        def run_competition():
            """Target for the new thread. Runs the competition and sends event to the window when the winner
             of the whole competitions has been determined."""
            competition_manager.run_primary(evaluation_function=dp.evaluate_winner)
            window.write_event_value(key='-T_WINNER-', value=tsd.get('cm').winner)  # Signal the window that there is a
                    # winner
        t = threading.Thread(target=run_competition, daemon=True)
        t.start()
        
        tsd.set('new_thread', t)
        
        # Switch sub layout
        window['-COL_START-'].update(visible=False)
        window['-COL_MAIN-'].update(visible=True)


def competitors_per_text(window: sg.Window, event: str, values: dict):
    pass  # TODO: Implement text input functionality


# Main layout events ###################################################################################################

def clicked_image(window: sg.Window, event: str, values: dict):
    """Indirectly signals the 2nd thread that a winner has been determined by updating the value with key 'winner'
    in the shared-data-dictionary of the ThreadSharedData class."""
    
    if event.endswith('L-'):  # Clicked on left image
        winner = tsd.get('comps')[0]
    else:  # Clicked on left image
        winner = tsd.get('comps')[1]
    
    tsd.set('winner', winner)


# End layout events ####################################################################################################

# End layout 1

def run_secondary(window: sg.Window, event: str, values: dict):
    """Creates a new thread to run the secondary competition (where every rank after #1 is determined).
    Also switches to main layout."""
    
    # Create new thread that determines the remaining ranks
    def determine_remaining_ranks():
        """Target for the new thread. Runs the secondary competition and sends event to the window when all the
        remaining ranks have been determined."""
        cm = tsd.get('cm')
        cm.run_secondary(evaluation_function=dp.evaluate_winner)
        window.write_event_value(key='-T_FINISHED_SECONDARY-', value=None)
    t = threading.Thread(target=determine_remaining_ranks, daemon=True)
    t.start()
    
    # Switch sub layout
    window['-COL_END_1-'].update(visible=False)
    window['-COL_MAIN-'].update(visible=True)


# End layout 2

rank_idx = 0    # Rank index of competitor shown on the left
image_data_buffer = []    # Temporarily store image data so not all images need to be recalculated


def ranks_previous(window: sg.Window, event: str, values: dict):
    """Updates the shown competitors when the user clicked the left-arrow button (in the end_2 sub-layout)."""
    
    global rank_idx
    global image_data_buffer
    cm: CompetitionManager = tsd.get('cm')
    
    # Check if next-button should be shown
    if rank_idx+2 == cm.count-1:  # (This is before rank_idx is updated) If before, there was no lower (= numerically
            # higher) rank to show
        window['-B_RANKS_NEXT-'].update(visible=True)
    
    # Update rank index and check if previous-button should be hidden
    rank_idx -= 1
    if rank_idx == 0:
        window['-B_RANKS_PREV-'].update(visible=False)
    
    # Prepare image updates
    images = get_ranking_images(window)
    image_data_buffer.pop()  # Remove last element because the right-most element gets thrown away
    
    # For the last two images, show the image of its left neighbor
    for i in range(1, 3):
        # images[i].update(data=images[i-1].Data)    Unfortunately, this somehow does not work
        images[i].update(data=image_data_buffer[i-1])
    
    # For the left image, show next higher (= numerically lower) ranked competitor
    next_comp_to_show: Competitor = cm.ranking[rank_idx]
    img_data = next_comp_to_show.get_img_data(winlay.IMG_RES_RANKS)
    images[0].update(data=img_data)
    image_data_buffer.insert(0, img_data)  # Add data to buffer
    
    # Update titles
    titles = get_ranking_titles(window)
    for title, comp in zip(titles, cm.ranking[rank_idx:rank_idx+3]):
        title.update(comp.title)


def ranks_next(window: sg.Window, event: str, values: dict):
    """Updates the shown competitors when the user clicked the right-arrow button (in the end_2 sub-layout)."""
    
    global rank_idx
    global image_data_buffer
    cm: CompetitionManager = tsd.get('cm')
    
    # Check if previous-button should be shown
    if rank_idx == 0:  # (This is before rank_idx is updated) If before, there was no higher (= numerically lower) rank
            # to show
        window['-B_RANKS_PREV-'].update(visible=True)
    
    # Update rank index and check if next-button should be hidden
    rank_idx += 1
    if rank_idx+3 == cm.count:
        window['-B_RANKS_NEXT-'].update(visible=False)
    
    # Prepare image updates
    images = get_ranking_images(window)
    image_data_buffer.pop(0)  # Remove first element because the left-most element gets thrown away
    
    # For the first two images, show the image of its right neighbor
    for i in range(2):
        # images[i].update(data=images[i+1].Data)    Unfortunately, this somehow does not work
        images[i].update(data=image_data_buffer[i])
    
    # For the right image, show next lower (= numerically higher) ranked competitor
    next_comp_to_show: Competitor = cm.ranking[rank_idx+2]
    img_data = next_comp_to_show.get_img_data(winlay.IMG_RES_RANKS)
    images[-1].update(data=img_data)
    image_data_buffer.append(img_data)    # Add data to buffer

    # Update titles
    titles = get_ranking_titles(window)
    for title, comp in zip(titles, cm.ranking[rank_idx:rank_idx+3]):
        title.update(comp.title)


def save(window: sg.Window, event: str, values: dict):
    """Creates a new folder/directory (at the location where the competitors are saved). Copies all the competitors'
    files to that folder but with their new titles where their ranks are in front of there title.
    (Ex.: old title: 'xXDemonSlayer69_ProHDXx' -> new title: '#4 xXDemonSlayer69_ProHDXx')"""
    
    path = window.metadata  # The path to where the competitors are saved (-> where we want to create the new folder)
    path += "/Competition Ranking"  # Add the new directory name
    
    # Create directory
    try:
        os.mkdir(path)
    except OSError:
        print(f"Warning: Could not create new directory at {path}")
        return
    
    # Add competitor images
    for comp in tsd.get('cm').ranking:
        filepath = path + '/' + comp.title + comp.file_extension
        img = cv2.imread(comp.path)
        cv2.imwrite(filepath, img)


# Thread events ########################################################################################################

def thread_new_competitors(window: sg.Window, event: str, values: dict):
    """Shows the competitors of the new match in the main sub-layout."""
    
    # Get competitors
    comp_1: Competitor
    comp_2: Competitor
    comp_1, comp_2 = values['-T_NEW_COMPS-']
    
    # Show round information
    round_info_func = tsd.get('round_info_func')
    window['-ROUND_INFO-'].update(value=round_info_func())
    
    # Show competitors
    window['-IMG_L-'].update(data=comp_1.get_img_data(winlay.IMG_RES_MATCH))
    window['-IMG_R-'].update(data=comp_2.get_img_data(winlay.IMG_RES_MATCH))
    
    # Show titles
    window['-TITLE_L-'].update(comp_1.title)
    window['-TITLE_R-'].update(comp_2.title)


def thread_winner(window: sg.Window, event: str, values: dict):
    """Switches to the end_1 sub-layout and shows the competition's winner."""
    
    # Show winner
    winner: Competitor = values['-T_WINNER-']
    window['-IMG_WINNER-'].update(data=winner.get_img_data(winlay.IMG_RES_WINNER))
    
    # Show title
    winner_title_split_up = winner.title.split(' ')[1:]    # Split and only take everything after the rank ("#1 ")
    title = " ".join(winner_title_split_up)
    window['-WINNER_TITLE-'].update(f"Winner: {title}")
    
    # Switch sub layout
    window['-COL_MAIN-'].update(visible=False)
    window['-COL_END_1-'].update(visible=True)


def thread_finished_secondary(window: sg.Window, event: str, values: dict):
    """Switches to the end_2 sub-layout and shows the first three places."""
    
    global image_data_buffer
    
    # Get competitors, images and text fields
    top_three_comps: list[Competitor] = tsd.get('cm').ranking[:3]
    images: list[sg.Image] = get_ranking_images(window)
    titles: list[sg.Text] = get_ranking_titles(window)
    
    # Show images and put image data in buffer
    for comp, img, title in zip(top_three_comps, images, titles):
        # Show image and add data to buffer
        img_data = comp.get_img_data(winlay.IMG_RES_RANKS)
        img.update(data=img_data)
        image_data_buffer.append(img_data)
        
        # Show title
        title.update(comp.title)
    
    # Handle next/previous button visibility
    window['-B_RANKS_PREV-'].update(visible=False)
    if tsd.get('cm').count <= 3:
        window['-B_RANKS_NEXT-'].update(visible=False)
    
    # Switch sub layout
    window['-COL_MAIN-'].update(visible=False)
    window['-COL_END_2-'].update(visible=True)
