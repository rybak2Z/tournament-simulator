import PySimpleGUI as sg


IMG_RES_MATCH = (325, 325)  # Image resolution during competition
IMG_RES_WINNER = (325, 325)  # Image resolution when winner is shown
IMG_RES_RANKS = (250, 250)  # Image resolution when all ranks are shown


STANDARD_FONTS = {
    1: "Helvetica 8",
    2: "Helvetica 10",
    3: "Helvetica 12",
    4: "Helvetica 14",
    5: "Helvetica 16",
    6: "Helvetica 18",
    7: "Helvetica 18"
}


def std_font(type: int):
    """Returns a font-string with font 'helvetica'. Size is determined by given type."""
    return STANDARD_FONTS[type]


def top_template(bottom_padding: int = 20):
    """Returns a standard layout (2d list) for the window top with the given amount of bottom padding."""
    WINDOW_TOP_TEMPLATE = [[sg.Text("Competition Simulator", font="Helvetica 24")],
                           [sg.HorizontalSeparator(pad=((0, 0), (10, bottom_padding)))]]
    return WINDOW_TOP_TEMPLATE


def exit_button(top_padding: int):
    """Returns a standard layout (as an sg.Column) for the window bottom with the given amount of top padding."""
    EXIT_BUTTON = sg.Column([[sg.HorizontalSeparator(pad=((0, 0), (top_padding, 0)))],
                             [sg.Button("Exit", key='-EXIT-', size=(10, 1), font=std_font(2), pad=((300, 300), (20,
                                                                                                            0)))]],
                            element_justification='center')
    return EXIT_BUTTON


# Main window layouts ##################################################################################################

# Start layout: gather competitors information

pick_folder_column = [[sg.Button("Use images\nand names", key='-B_FOLDER-', size=(15, 3), font=std_font(3))],
                      [sg.Text("Use this button to chose a folder with one image file per competitor. Each image file"
                               "needs to be named \nas its corresponding competitor.", justification='left',
                               size=(30, 4), font=std_font(4))]]

use_text_field_column = [[sg.Button("Use only names", key='-B_TEXT-', size=(15, 3), font=std_font(3))],
                         [sg.Text("Use this button to be provided with a text field in which you can put in all the"
                                  "competitors' names without using any images.", justification='left',
                                  size=(30, 4), font=std_font(4), pad=((20, 0), (0, 0)))]]

start_layout = [*top_template(100),
                [sg.Text("Please use one of the following two options to import the list of competitors:",
                         font=std_font(6), pad=((0, 0), (0, 20)))],
                [sg.Column(pick_folder_column, element_justification='center'), sg.VerticalSeparator(),
                    sg.Column(use_text_field_column, element_justification='center')],
                [exit_button(175)]]


# Main layout: run competition

left_image_column = [[sg.Image(size=IMG_RES_MATCH, enable_events=True, key='-IMG_L-')],
                     [sg.Text(size=(15, None), font=std_font(4), key='-TITLE_L-')]]
left_image_column = sg.Column(left_image_column, element_justification='center')

right_image_column = [[sg.Image(size=IMG_RES_MATCH, enable_events=True, key='-IMG_R-')],
                      [sg.Text(size=(15, None), font=std_font(4), key='-TITLE_R-')]]
right_image_column = sg.Column(right_image_column, element_justification='center')

main_layout = [*top_template(40),
               [sg.Text(size=(30, None), font=std_font(6), key='-ROUND_INFO-')],
               [sg.Text("Click on the image of either competitor to choose the winner.", font=std_font(2),
                        pad=((0, 0), (0, 15)))],
               [left_image_column, sg.VerticalSeparator(), right_image_column],
               [exit_button(25)]]


# End layout: show winner

end_layout_1 = [*top_template(30),
                [sg.Text(size=(30, 2), font=std_font(7), pad=((0, 30), (0, 0)), key='-WINNER_TITLE-')],
                [sg.Image(size=IMG_RES_WINNER, key='-IMG_WINNER-')],
                [sg.Button("Determine remaining ranks", size=(25, 2), key='-B_RUN_SECONDARY-', pad=((0, 0), (25, 0)))],
                [exit_button(25)]]


# End layout: show all ranks

competitor_columns = []    # 3x Image with title
for key_suffix in ('LEFT', 'MID', 'RIGHT'):
    column = [[sg.Image(size=IMG_RES_RANKS, key=f'-COMP_{key_suffix}-')],
              [sg.Text(size=(15, None), key=f'-RANKS_TITLE_{key_suffix}-', font=std_font(3))]]
    competitor_columns.append(sg.Column(column, element_justification='center'))

end_layout_2 = [*top_template(30),
                [sg.Text("Here you can see the whole ranking. Use the arrow buttons on the left and right (if there "
                         "are more than three competitors) to navigate through the ranks. Press the button below to "
                         "create a new folder (in the same directory) to hold a copy of all competitors with their "
                         "ranks in their file names.", size=(100, 3), font=std_font(2), pad=((0, 0), (0, 30)))],
                [sg.Column([[sg.Button('<', key='-B_RANKS_PREV-')]], element_justification='center'),
                    *competitor_columns, sg.Column([[sg.Button('>', key='-B_RANKS_NEXT-')]],
                                                   element_justification='center')],
                [sg.Button("Save ranking in new folder", size=(25, 2), key='-B_SAVE-', pad=((0, 0), (35, 0)))],
                [exit_button(35)]]


# Complete layout: combine all sub-layouts into one to create a pseudo-dynamic window

layout = [[sg.Column(start_layout, key='-COL_START-', element_justification='center'),
           sg.Column(main_layout, key='-COL_MAIN-', element_justification='center', visible=False),
           sg.Column(end_layout_1, key='-COL_END_1-', element_justification='center', visible=False),
           sg.Column(end_layout_2, key='-COL_END_2-', element_justification='center', visible=False)]]


# Popup window layouts #################################################################################################

instructions_text = "Please select your folder containing all the competitors' data.\n" \
                    "The folder must contain one image file per competitor with each\nfile being named" \
                    "by the competitor it's representing."
popup_folder_browser = [[sg.Text(instructions_text, font=std_font(2))],
                        [],
                        [sg.FolderBrowse(key='-BROWSE-', target='-PATH_INPUT-'), sg.InputText(key='-PATH_INPUT-')],
                        [],
                        [sg.Column([[sg.Submit(key='-SUBMIT-'), sg.Cancel(key='-CANCEL-')]],
                                   element_justification='center', justification='center')]]
