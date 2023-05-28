## Introduction

This is a small GUI app which uses a given folder containing pictures of the competitors to hold a competition (in tournament bracket style) in which the winner gets chosen by clicking on them.

I wrote this when I started learning Python and programming in general and the main reason I uploaded this is to not lose it. This was way before I started using Git(Hub), and I didn't bother polishing this program. So there are still comments, unfinished parts, quite a few spelling mistakes, and unwanted behaviors like converting .jpg to .png and then not deleting those generated images at the end.

The folder at the chosen path also cannot contain anything other than .png and .jpg files (yes, .jpeg does not work). No other files or folders.

Despite the program using a bracket, it can manage a number of competitors which does not completely fill the bracket, though that results in unfair advantage for those who have to get fewer wins to reach the finals. After having determined the winner, it also provides the options to play more rounds to determine all ranks meaning 2nd place, 3rd place and so on.

## Screenshots

### Start screen
![Start screen](screenshots/start%20screen.jpg)

### Regular round
![Regular round](screenshots/single%20round.jpg)

### Winner screen
![Winner screen](screenshots/competition%20winner.jpg)

### Determining all ranks
![Determining all ranks](screenshots/determining%20the%20rest%20of%20the%20ranks.jpg)

### Complete ranking
![Complete ranking](screenshots/results%20all%20ranks%20determined.jpg)
