from math import log2, ceil

# For typing
from typing import MutableSequence, Optional, Union
from Competitor import Competitor


class Tree:
    """This class is a tree-structure.
    This tree-structure is not a normal tree but is adjusted for the needs of this program (for example the structure:
    in each depth ('layer'), the number of nodes is a mutltiple of 2, starting at 2^0=1 at the root node and
    incrementing on the way down.)"""
    
    def __init__(self, competitors: Optional[MutableSequence[Competitor]] = None, root_node: Optional['Node'] = None):
        """Needs to be given either the competitors or the root node, but cannot be given nothing.
        
        If competitors are given: The tree is newly built (for structure -> see class multi-line comment) and puts
        gives all the nodes in the deepest layer (or as many as needed) one competitors as a value.
        
        If a node is given, it makes that node the root node and calculates the depth.
        """
        
        if competitors is not None:
            # Calculate tree size (what tree depth to use to support the given competitors count)
            depth = log2(len(competitors))  # Every layer doubles the possible competitors count
            depth = ceil(depth)
            self.depth = depth + 1  # +1 because log2 returns 0 for len(competitors)==1 but I want the root to count
                # as a layer
            
            # Build tree
            self.competitors = competitors  # Is only needed for building the tree
            self.root = self.__build_tree(depth)
            del self.competitors
        elif root_node is not None:
            self.depth = self.__find_max_depth(root_node)
            self.root = root_node
        else:
            print("Warning: Tree-Initialization: Cannot pass 'None' for both 'competitors' and 'root_node'.")
    
    
    def __build_tree(self, depth: int):
        """Recursively builds the tree. For more details, see the __init__ method."""
        
        # === Base case ===
        if depth == 0:
            # If is at least one competitor left -> use him as the value, else -> use None
            try:
                value = self.competitors.pop()
            except IndexError:
                value = None
            
            return Node(value=value)
        
        # === Non-base case ===
        node = Node()
        node.left = self.__build_tree(depth-1)
        node.left.parent = node
        node.right = self.__build_tree(depth-1)
        node.right.parent = node
        
        return node
    
    
    @staticmethod
    def __find_max_depth(node: 'Node') -> int:
        """Finds the depth of the given node."""
        
        current_node = node
        depth = 1
        
        # Infinitely go one level deeper until there is no deeper level left
        while current_node.left is not None:    # This will indeed find the global max depth because in this
                # implementation of a tree, every route down ends at the same depth.
            current_node = current_node.left
            depth += 1
        
        return depth
    
    
    def debug_print(self):
        """Prints the tree with its structure and the nodes' values in a more or less good overview."""
        
        print("R:", self.root.val)  # R for root
        if self.root.left is not None:
            self.__debug_helper(self.root.left, 1)
        if self.root.right is not None:
            self.__debug_helper(self.root.right, 1)
    
    
    @staticmethod
    def __debug_helper(node, level):
        """Helper functions for the debug_print method. Recursively prints the tree structure and the nodes' values."""
        
        print("    " * (level-1), "|--", sep='', end=' ')
        print("N:", node.val)  # N for node
        if node.left is not None:
            Tree.__debug_helper(node.left, level+1)
        if node.right is not None:
            Tree.__debug_helper(node.right, level+1)


class Node:
    """
    This class provides the Node objects that a tree of the above class consists of. It contains some extra
    functionality adjusted for the needs of this program.
    """
    
    def __init__(self, parent: 'Node' = None, value=None, left=None, right=None):
        """
        
        :param value:
        :param left:
        :param right:
        """
        
        self.parent: 'Node' = parent
        self.val = value
        self.left: 'Node' = left
        self.right: 'Node' = right
        self.winner: Optional['Node'] = None    # Can later be set to either self.left or self.right
        self.loser: Optional['Node'] = None    # Can later be set to either self.left or self.right
    
    
    def set_winner(self, winner: Union[int, 'Node']):
        """Sets the node's winner and loser variable to self.left and self.right.
        :param winner: Can be either child of the Node that the method is called on. Can also be an int (0 ->
                       winner = left; 1 -> winner = right)"""
        
        if isinstance(winner, int):
            if winner == 0:  # -> winner = left
                self.winner, self.loser = self.left, self.right
            else:  # -> winner = right
                self.winner, self.loser = self.right, self.left
        else:
            if winner is self.left:
                self.winner, self.loser = self.left, self.right
            else:
                self.winner, self.loser = self.right, self.left
    
    
    def descends_from(self, other: 'Node'):
        """Recursively checks whether the given Node is a parent of the Node that the method is called on."""
        
        # Base case
        if self.parent is None:  # If arrived at root
            return False
        elif self.parent is other:
            return True
        
        # Non-base case
        if self.parent.descends_from(other):
            return True
        else:
            return False


if __name__ == '__main__':
    """ Test printing
    t = Tree(list(range(13)))
    t.debug_print()
    """
    
    """ Test depth finding
    t = Tree(list(range(26)))
    print(t.depth)
    t2 = Tree(root_node=t.root)
    print(t2.depth)
    """
    
    t = Tree(list(range(3)))
    print(t.depth)
