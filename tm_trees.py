"""Assignment 2: Trees for Treemap

=== CSC148 Winter 2019 ===
This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2019 Bogdan Simion, David Liu, Diane Horton, Jacqueline Smith

=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser. You will both add to the abstract class, and complete a
concrete implementation of a subclass to represent files and folders on your
computer's file system.
"""
from __future__ import annotations
import os
import math
from random import randint
from typing import List, Tuple, Optional


class TMTree:
    """A TreeMappableTree: a tree that is compatible with the treemap
    visualiser.

    This is an abstract class that should not be instantiated directly.

    You may NOT add any attributes, public or private, to this class.
    However, part of this assignment will involve you implementing new public
    *methods* for this interface.
    You should not add any new public methods other than those required by
    the client code.
    You can, however, freely add private methods as needed.

    === Public Attributes ===
    rect:
        The pygame rectangle representing this node in the treemap
        visualization.
    data_size:
        The size of the data represented by this tree.

    === Private Attributes ===
    _colour:
        The RGB colour value of the root of this tree.
    _name:
        The root value of this tree, or None if this tree is empty.
    _subtrees:
        The subtrees of this tree.
    _parent_tree:
        The parent tree of this tree; i.e., the tree that contains this tree
        as a subtree, or None if this tree is not part of a larger tree.
    _expanded:
        Whether or not this tree is considered expanded for visualization.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.

    - _colour's elements are each in the range 0-255.

    - If _name is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.

    - if _parent_tree is not None, then self is in _parent_tree._subtrees

    - if _expanded is True, then _parent_tree._expanded is True
    - if _expanded is False, then _expanded is False for every tree
      in _subtrees
    - if _subtrees is empty, then _expanded is False
    """

    rect: Tuple[int, int, int, int]
    data_size: int
    _colour: Tuple[int, int, int]
    _name: str
    _subtrees: List[TMTree]
    _parent_tree: Optional[TMTree]
    _expanded: bool

    def __init__(self, name: str, subtrees: List[TMTree],
                 data_size: int = 0) -> None:
        """Initialize a new TMTree with a random colour and the provided <name>.

        If <subtrees> is empty, use <data_size> to initialize this tree's
        data_size.

        If <subtrees> is not empty, ignore the parameter <data_size>,
        and calculate this tree's data_size instead.

        Set this tree as the parent for each of its subtrees.

        Precondition: if <name> is None, then <subtrees> is empty.
        """
        self.rect = (0, 0, 0, 0)
        self._name = name
        self._subtrees = subtrees[:]
        self._parent_tree = None
        self._colour = (randint(0, 255), randint(0, 255), randint(0, 255))
        self.data_size = 0
        self._expanded = False

        # 1. Initialize self._colour and self.data_size, according to the
        # docstring.
        # 2. Set this tree as the parent for each of its subtrees.

        if self._name is None:
            self._subtrees = []

        if not self.is_empty():
            if len(self._subtrees) == 0:
                self.data_size = data_size
            else:
                for subtree in self._subtrees:
                    self.data_size += subtree.data_size
                    subtree._parent_tree = self

    def is_empty(self) -> bool:
        """Return True iff this tree is empty.
        """
        return self._name is None

    def update_rectangles(self, rect: Tuple[int, int, int, int]) -> None:
        """Update the rectangles in this tree and its descendents using the
        treemap algorithm to fill the area defined by pygame rectangle <rect>.
        """
        # Read the handout carefully to help get started identifying base cases,
        # then write the outline of a recursive step.
        #
        # Programming tip: use "tuple unpacking assignment" to easily extract
        # elements of a rectangle, as follows.
        x, y, width, height = rect
        right_upper = x + width
        left_button = y + height
        self.rect = (x, y, width, height)

        for subtree in self._subtrees:
            if width > height and self.data_size != 0:
                sub_width = math.floor\
                (width * subtree.data_size / self.data_size)
                sub_height = height
                if subtree == self._subtrees[-1]:
                    sub_width = right_upper - x
                subtree.update_rectangles((x, y, sub_width, sub_height))
                x += sub_width

            elif width <= height and self.data_size != 0:
                sub_width = width
                sub_height = math.floor\
                (height * subtree.data_size / self.data_size)
                if subtree == self._subtrees[-1]:
                    sub_height = left_button - y
                subtree.update_rectangles((x, y, sub_width, sub_height))
                y += sub_height

    def get_rectangles(self) -> List[Tuple[Tuple[int, int, int, int],
                                           Tuple[int, int, int]]]:
        """Return a list with tuples for every leaf in the displayed-tree
        rooted at this tree. Each tuple consists of a tuple that defines the
        appropriate pygame rectangle to display for a leaf, and the colour
        to fill it with.
        """
        if not self.is_empty() and self.data_size != 0:
            if self._expanded and len(self._subtrees) != 0:
                new_lst = []
                for subtree in self._subtrees:
                    new_lst = new_lst + subtree.get_rectangles()
                return new_lst
            else:
                return [(self.rect, self._colour)]
        else:
            return []

    def get_tree_at_position(self, pos: Tuple[int, int]) -> Optional[TMTree]:
        """Return the leaf in the displayed-tree rooted at this tree whose
        rectangle contains position <pos>, or None if <pos> is outside of this
        tree's rectangle.

        If <pos> is on the shared edge between two rectangles, return the
        tree represented by the rectangle that is closer to the origin.
        """
        displayed_list = self._helper()
        closest_list = []
        for leaf in displayed_list:
            x, y, width, height = leaf.rect
            if x <= pos[0] <= x + width and y <= pos[1] <= y + height:
                closest_list.append(leaf)

        if len(closest_list) == 0:
            return None
        elif len(closest_list) == 1:
            return closest_list[0]
        else:
            location = (closest_list[0].rect[0], closest_list[0].rect[1])
            closest = closest_list[0]
            for item in closest_list:
                if item.rect[0] <= location[0] and item.rect[1] <= location[1]:
                    location = (item.rect[0], item.rect[1])
                    closest = item
            return closest

    def _helper(self) -> List[TMTree]:
        """Find all leaves in TMTree and return them as a list"""
        new_list = []
        if not self.is_empty():
            if len(self._subtrees) == 0:
                return [self]
            if not self._expanded:
                new_list.append(self)
            else:
                for subtree in self._subtrees:
                    new_list += subtree._helper()
        return new_list

    def update_data_sizes(self) -> int:
        """Update the data_size for this tree and its subtrees, based on the
        size of their leaves, and return the new size.

        If this tree is a leaf, return its size unchanged.
        """
        if not self.is_empty():
            if len(self._subtrees) == 0:
                return self.data_size
            else:
                self.data_size = 0
                for subtree in self._subtrees:
                    self.data_size += subtree.update_data_sizes()
        else:
            self.data_size = 0
        return self.data_size

    def move(self, destination: TMTree) -> None:
        """If this tree is a leaf, and <destination> is not a leaf, move this
        tree to be the last subtree of <destination>. Otherwise, do nothing.
        """
        if not self.is_empty() and not destination.is_empty() and \
                len(self._subtrees) == 0 and len(destination._subtrees) != 0:
            destination._subtrees.append(self)
            if self._parent_tree is not None:
                if len(self._parent_tree._subtrees) == 1:
                    self._parent_tree.data_size = 0
                    self._parent_tree.rect = (0, 0, 0, 0)
                self._parent_tree._subtrees.remove(self)
                self._parent_tree.update_data_sizes()

            self._parent_tree = destination
            destination.update_data_sizes()

    def change_size(self, factor: float) -> None:
        """Change the value of this tree's data_size attribute by <factor>.

        Always round up the amount to change, so that it's an int, and
        some change is made.

        Do nothing if this tree is not a leaf.
        """

        if not self.is_empty() and len(self._subtrees) == 0:
            change = factor * self.data_size
            if change >= 0:
                self.data_size = self.data_size + math.ceil(change)
            else:
                self.data_size = self.data_size + math.floor(change)
            if self.data_size < 1:
                self.data_size = 1
        if self._parent_tree is not None:
            self._parent_tree.update_data_sizes()
        else:
            self.update_data_sizes()

    def expand(self) -> None:
        """Expand the subtrees under the selected TMT tree"""
        if len(self._subtrees) == 0:
            self._expanded = False
        else:
            self._expanded = True

    def expand_all(self) -> None:
        """Expand all the subtrees and its descendents under the selected TMT
        tree"""
        if len(self._subtrees) != 0:
            self._expanded = True
            for subtree in self._subtrees:
                subtree.expand_all()
        else:
            self._expanded = False

    def collapse(self) -> None:
        """Collapse the parent of the selected TMT tree"""

        if self._parent_tree is not None:
            self._parent_tree._expanded = False
            for subtree in self._parent_tree._subtrees:
                subtree._help_collapse()
        else:
            self._expanded = False

    def _help_collapse(self) -> None:
        """Collapse other subtree of the parent of the selected TMT tree"""
        if self._expanded and len(self._subtrees) > 0:
            for x in self._subtrees:
                x._help_collapse()
        self._expanded = False

    def collapse_all(self) -> None:
        """Collapse the whole tree"""
        root_tree = self._find_root()
        root_tree._help_collapse()

    def _find_root(self) -> TMTree:
        """Find the root of all subtrees"""
        tm_tree = self
        if tm_tree._parent_tree is not None:
            tm_tree = tm_tree._parent_tree
            tm_tree = tm_tree._find_root()

        return tm_tree

    # Methods for the string representation
    def get_path_string(self, final_node: bool = True) -> str:
        """Return a string representing the path containing this tree
        and its ancestors, using the separator for this tree between each
        tree's name. If <final_node>, then add the suffix for the tree.
        """
        if self._parent_tree is None:
            path_str = self._name
            if final_node:
                path_str += self.get_suffix()
            return path_str
        else:
            path_str = (self._parent_tree.get_path_string(False) +
                        self.get_separator() + self._name)
            if final_node or len(self._subtrees) == 0:
                path_str += self.get_suffix()
            return path_str

    def get_separator(self) -> str:
        """Return the string used to separate names in the string
        representation of a path from the tree root to this tree.
        """
        raise NotImplementedError

    def get_suffix(self) -> str:
        """Return the string used at the end of the string representation of
        a path from the tree root to this tree.
        """
        raise NotImplementedError


class FileSystemTree(TMTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _name attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/Diane/csc148/assignments'

    The data_size attribute for regular files is simply the size of the file,
    as reported by os.path.getsize.
    """

    def __init__(self, path: str) -> None:
        """Store the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer.
        """
        # Remember that you should recursively go through the file system
        # and create new FileSystemTree objects for each file and folder
        # encountered.
        #
        # Also remember to make good use of the superclass constructor!

        name = os.path.basename(path)
        subtrees = []
        data_size = 0

        if os.path.isdir(path):
            for file in os.listdir(path):
                file_path = os.path.join(path, file)
                new_subtree = FileSystemTree(file_path)
                subtrees.append(new_subtree)
        elif os.path.isfile(path):
            data_size = os.path.getsize(path)
        else:
            name = None

        TMTree.__init__(self, name, subtrees, data_size)

    def get_separator(self) -> str:
        """Return the file separator for this OS.
        """
        return os.sep

    def get_suffix(self) -> str:
        """Return the final descriptor of this tree.
        """
        if len(self._subtrees) == 0:
            return ' (file)'
        else:
            return ' (folder)'


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'math', 'random', 'os', '__future__'
        ]
    })
