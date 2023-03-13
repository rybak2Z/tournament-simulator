import random

# Local project imports
from Tree import Tree, Node
from ThreadSharedData import ThreadSharedData as tsd

# For typing
from Competitor import Competitor
from typing import MutableSequence, Callable, Optional


class CompetitionManager:
    """

    """
    
    def __init__(self,
                 competitors: Optional[MutableSequence[Competitor]] = None,
                 shuffle: bool = True,
                 tree_to_copy: Tree = None
                 ):
        """

        :param competitors:
        :param shuffle:
        :param tree_to_copy:
        """
        
        self.ranking: list[Competitor] = []  # Later, here will be all competitors sorted by rank
        self.count: int = len(competitors)
        
        if shuffle:
            random.shuffle(competitors)
        
        # Generate or copy tree
        if competitors is not None:
            self.tree = Tree(competitors)
        elif tree_to_copy is not None:
            self.tree = tree_to_copy
        else:
            print("Warning: CompetitionManager-Initialization: Cannot pass 'None' for both 'competitors' and "
                  "'tree_to_copy'.")
    
    
    def run_primary(self, evaluation_function: Callable[[Competitor, Competitor], Competitor]):
        """

        :param evaluation_function:
        :return:
        """
    
        # Check prerequisite: Competition must not have run before
        if len(self.ranking) != 0:
            print("Warning: Refused to run (primary) competition. self.ranking must be of length 0 but it contains"
                  f"{len(self.ranking)} elements.")
            return
    
        # Evaluate winner
        for layers_down in range(self.tree.depth-1, 0, -1):
            tsd.set('round_info_func', self.get_round_info_maker(2**layers_down))  # Share round_info function
            self.__evaluate_layer(self.tree.root, layers_down, evaluation_function)
        
        # Add winner to ranking and change title
        winner: Competitor = self.tree.root.val
        self.ranking.append(winner)
        winner.title = '#1 ' + winner.title
    
    
    @staticmethod
    def __evaluate_layer(starting_node: Node,
                         layers_down: int,
                         evaluation_function: Callable[[Competitor, Competitor], Competitor]
                         ):
        """
        
        :param starting_node:
        :param layers_down:
        :param evaluation_function:
        :return:
        """
        
        # Base case: Determine winner of match
        if layers_down == 1:
            left_c, right_c = starting_node.left.val, starting_node.right.val  # 'c' -> competitor
            
            if left_c is not None and right_c is not None:
                winner = evaluation_function(left_c, right_c)
            elif left_c is None:
                winner = right_c
            else:  # If right is None
                winner = left_c
            
            starting_node.val = winner
            starting_node.set_winner(0 if winner is starting_node.left.val else 1)
            return
        
        # Non-base case: Go down one layer and repeat
        CompetitionManager.__evaluate_layer(starting_node.left, layers_down-1, evaluation_function)
        CompetitionManager.__evaluate_layer(starting_node.right, layers_down-1, evaluation_function)
    
    
    def run_secondary(self, evaluation_function: Callable[[Competitor, Competitor], Competitor]):
        """

        :param evaluation_function:
        :return:
        """
        
        # Check prerequisite: Winner must have been evaluated
        if len(self.ranking) != 1:
            print("Warning: Refused to run (secondary) competition. self.ranking must be of length 1 but it contains"
                  f"{len(self.ranking)} elements.")
            return
        
        # Get list of all losers, sorted by max reached level/layer
        losers = []
        for layer in range(1, self.tree.depth):  # Go through each layer from top to bottom
            # Grab all losers of that layer
            losers += self.__get_losers_from_layer(starting_node=self.tree.root, layers_down=layer)
        losers = [loser.val for loser in losers]  # Replace every Node in losers by its value
        losers = list(filter(lambda x: x is not None, losers))  # Filter out NoneTypes
        
        # Determine remaining ranks
        for i in range(1, self.count):  # Go through each rank
            leader = losers[0]  # Since the list of losers is kinda sorted, make the first one the leader
            tsd.set('round_info_func', lambda: f"Rank #{i+1}")  # Share information about current rank searched
            
            # Compare leader against all other losers
            for competitor in losers:
                if competitor is not leader:
                    leader = evaluation_function(leader, competitor)  # Declare new or stick with old leader
            
            losers.remove(leader)
            self.ranking.append(leader)
        
        # Change titles: Add rank in front
        for i, comp in enumerate(self.ranking[1:]):
            comp.title = f"#{str(i+2)} {comp.title}"
    
    
    def __get_losers_from_layer(self, starting_node: Node, layers_down: int):
        """
        
        :return:
        """
        
        # Base case: Return loser of next layer
        if layers_down == 1:
            return [starting_node.loser]
        
        # Non-base case: Go down layers until layers_down == 1, then get the next layer's losers
        losers = []
        losers += self.__get_losers_from_layer(starting_node.left, layers_down=layers_down - 1)
        losers += self.__get_losers_from_layer(starting_node.right, layers_down=layers_down - 1)
        
        return losers
    
    
    @staticmethod
    def get_round_info_maker(competition_stage: int) -> Callable[[], str]:
        i = 0
        round_title_beginning = "Round of "
        
        if competition_stage >= 16:
            round_title_beginning += str(competition_stage)
        elif competition_stage == 8:
            round_title_beginning = 'Quarterfinal'
        elif competition_stage == 4:
            round_title_beginning = 'Semifinal'
        elif competition_stage == 2:
            round_title_beginning = 'Final'
        
        def round_info() -> str:
            nonlocal round_title_beginning
            nonlocal i
            
            i += 1
            
            if round_title_beginning != 'Final':
                round_title = round_title_beginning + f" ({i}/{int(competition_stage/2)})"
            else:
                round_title = round_title_beginning
            
            return round_title
    
        return round_info
    
    
    @property
    def winner(self):
        return self.tree.root.val


if __name__ == '__main__':
    """
    # Test primary evaluation and debug_print
    comps = list(range(13))
    eval_fun = max
    cm = CompetitionManager(comps)
    cm.tree.debug_print()
    cm.run_primary(evaluation_function=eval_fun)
    cm.tree.debug_print()
    print("\nwinner:", cm.winner)
    """
    
    """
    # Test 'descends_from' function
    comps = list(range(13))
    eval_fun = max
    cm = CompetitionManager(comps)
    cm.run_primary(evaluation_function=eval_fun)
    print("should be false:", cm.tree.root.descends_from(Node()))
    print("should be true:", cm.tree.root.left.descends_from(cm.tree.root))
    """
    
    """
    # Test loser seaching (only worked when run_secondary returned losers)
    comps = list(range(40))
    eval_fun = max
    cm = CompetitionManager(comps)
    cm.run_primary(evaluation_function=eval_fun)
    _losers = list(cm.run_secondary(eval_fun))
    _losers = [loser.val for loser in _losers]
    print("\nlosers:", _losers)
    print(len(_losers))
    # test which numbers are missing
    test_list = list(range(40-1))
    test_list = list(filter(lambda x: x not in _losers, test_list))
    print("the following losers are missing:", test_list)
    """
    
    # Test run_secondary
    comps = list(range(20))
    eval_fun = max
    cm = CompetitionManager(comps)
    cm.run_primary(eval_fun)
    cm.run_secondary(eval_fun)
    print(cm.ranking)
