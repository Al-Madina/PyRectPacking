__author__  = "Ahmed Hassan"
__license__ = "MIT License"
__email__   = "ahmedhassan@aims.ac.za"
__status__  = "Production"


import math
from enum import Enum
from typing import List
from rect import Rect  


class PackingHeuristic(Enum):
    """A class for specifying the packing heuristics"""
    BestAreaFit = 1 
    TouchingPerimeter = 2
    TopRightCornerDistance = 3
   


class Bin:
    """A class for implementing generic bins.

    This class provides basic functionalities common on all bins. The class should be extended 
    to provide concrete implementation of the bin.

    Attributes
    ----------
    binWidth : int
        The width of the bin (the length of the side parallel to  the x-axis).
    binHeight : int
        The height of the bin (the length of the side parallel to  the y-axis).

    See Also
    --------
    maxspace.MaxSpaceBin : A class that inherits from this class
    """    
    
    def __init__(self, binWidth: int, binHeight: int):
        self.binWidth = binWidth
        self.binHeight = binHeight
        self.occupiedArea = 0
        self.touchingPerimeter = 0
        self.packedRects = []
        self.freeRects = []
        self.canRotate = False
        self.packHeur = None 
          
    
    def setupFreeRects(self):
        """Sets up the free spaces inside the bin. This method should be overriden in the descendent classes.

        See Also
        --------
        maxspace.MaxSpaceBin.setupFreeRects : a method that overrides this method
        """
        raise NotImplementedError("Not implemented yet")

                    
    def init(self):
        self.setup()
    
                    
    def setup(self):
        self.packedRects = []
        self.setupFreeRects()
        self.occupiedArea = 0
        self.touchingPerimeter = 0

    
    def evaluatePacking(self, rect, heur: PackingHeuristic):
        """Evaluate the quality of packing an item using the specified packing heuristic.
        
        This method must be overriden in the descendant classes.
        Parameters
        ----------
        rect : rect.Rect
            The item
        heur : PackingHeuristic
            The packing heuristic

        Returns
        -------
        rect.Rect
            A new item with its packing information set if the packing in this bin is possible.
            Otherwise, returns ``None``
        """
        raise NotImplementedError("Not implemented yet")

    
    def insert(self, rect, heuristic: PackingHeuristic):
        """Insert an item in this bin using the specified packing heuristic to determine its location
        inside the bin. 

        This method insert the item immediately if the method evaluatePacking is invoked on this item.
        This is because evaluatePacking determines the location of the item when invoked as a by-product
        of evaluating its packing quality in this bin. If evaluatePacking is not invoked on this item, 
        then this method will call it first.

        This method must be extended in the classes that inherits from this class.

        Parameters
        ----------
        rect : rect.Rect
            The item
        heur : PackingHeuristic
            The packing heuristic

        Returns
        -------
        bool
            True if the item is inserted in  this bin or False if the item cannot be inserted.
        """
        raise NotImplementedError("Not implemented yet")


    def mergeFreeRects(self):
        """Merge free spaces (rects) inside the bin to get more spaces for further packing."""
        for i in range(len(self.freeRects)):
            rectI = freeRects[i]
            for j in range(i+1, len(self.freeRects)):
                rectJ = freeRects[j]
                #Check if two rects extend vertically
                if(rectI.x == rectJ.x and rectI.width == rectJ.width):
                    if(rectI.y == rectJ.y + rectJ.height):
                        rectI.y -= rectJ.height
                        rectI.height += rectJ.height
                        freeRects.remove(j)
                        --j

                    elif(rectI.y + rectI.height == rectJ.y):
                        rectI.height += rectJ.height
                        freeRects.remove(j)
                        --j
                                    
                #Check if two rects extend horizontally
                elif(rectI.y == rectJ.y and rectI.height == rectJ.height):
                    #rectI to the right of rectJ
                    if(rectI.x == rectJ.x + rectJ.width):
                        rectI.x -= rectJ.width
                        rectI.width += rectJ.width
                        freeRects.remove(j)
                        --j
                    
                    #rectI to the left of rectJ
                    elif(rectI.x + rectI.width == rectJ.x):
                        rectI.width += rectJ.width
                        freeRects.remove(j)
                        --j
                    
    def packRect(self, rect):
        """Pack a rect in this bin

        Parameters
        ----------
        rect : rect.Rect
            The rect to be inserted in this bin
        """
        self.packedRects.append(rect) 
        self.occupiedArea += rect.width * rect.height
    

    def isEmpty(self):
        """Check whether this bin is empty."""
        return len(self.packedRects) == 0
    

    def isFeasible(self):
        for i in range(len(self.packedRects)):
            rect1 = self.packedRects[i]
            #if rect1 partially or fully lies outside the bin
            if(rect1.x < 0 or rect1.x > self.binWidth): return False
            if(rect1.y < 0 or rect1.y > self.binHeight): return False
            if(rect1.x + rect1.width > self.binWidth or rect1.y + rect1.height > self.binHeight):
                return False
            for j in range(i+1, len(self.packedRects)):
                rect2 = self.packedRects[j]
                #check wether the two rects overlap
                if(rect1.isOverlapping(rect2)): return False
                    
        return True
    
    
    def computeTouchingPerimeter(self, x, y, width, height):
        perimeter = 0
        if(x == 0 or x + width == self.binWidth):
            perimeter += height
        if(y == 0 or y + height == self.binHeight):
            perimeter += width
        for rect in self.packedRects:
            if(rect.x + rect.width == x or x + width == rect.x):
                perimeter += self.computeCommonLength(y, y+height, rect.y, rect.y+rect.height)
            if(rect.y == y + height or rect.y + rect.height == y):
                perimeter += self.computeCommonLength(x, x + width, rect.x, rect.x + rect.width)

        return perimeter


    def isOverlapping(self, rect1, rect2):
        """Checks whether two items overlap

        Parameters
        ----------
        rect1 : rect.Rect
            The first item.
        rect2 : rect.Rect
            The second item.
        """
        horizSkip = rect1.x >= rect2.x + rect2.width or rect1.x + rect1.width <= rect2.x
        vertSkip = rect1.y >= rect2.y + rect2.height or rect1.y + rect1.height <= rect2.y
        return not (horizSkip or vertSkip)


    def computeCommonLength(self, start1, end1, start2, end2):
        """Compute common length."""
        if(start2 >= end1 or end2 <= start1): return 0
        return min(end1, end2) - max(start1, start2)
    
    
    def computeDistance(self, x1, y1, x2, y2):
        """Compute distance."""
        return math.sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2)) 
            
    
    def getPackedRect(self):
        return self.packedRects #make sure packed rects will never be modified otherwise, returns a copy
    
    
    def getPackedArea(self):
        return int(self.occupiedArea)
    
    
    def getOccupancy(self):
        return self.occupiedArea/(self.binWidth*self.binHeight)
    
    
    def getTouchingPerimeter(self):
        if(self.packedRects.isEmpty()): return 0
        touchingPerimeter = 0
        totalPer = 0
        for rect in self.packedRects:
            touchingPerimeter += computeTouchingPerimeter(rect.x, rect.y, rect.width, rect.height)
            totalPer += 2*(rect.width + rect.height)
        
        return touchingPerimeter/totalPer        


    def __eq__(self, other):
        if not isinstance(other, self.__class__): return False       
        if len(self.packedRects) != len(other.packedRects): return False 
        flag = True
        for i in range(len(self.packedRects)):
            rect1 = self.packedRects[i]
            rect2 = other.packedRects[i]
            if rect1 != rect2:
                flag = False
                break
        return flag
    
    
    def __ne__(self, other):
        return not self.__eq__(other)
    

    def __lt__(self, other):
        if not isinstance(other, self.__class__): return False
        return self.getOccupancy() < other.getOccupancy()
    

    def __le__(self, other):
        return self.__lt(other) or self.getOccupancy() == other.getOccupancy()
    

    def __ge__(self, other):
        return not self.__lt__(other)
    

    def __gt__(self, other):
        return not self.__lt__(other) and self.getOccupancy() != other.getOccupancy()


    def __len__(self) -> int:
        return len(self.packedRects) 
    

    def __hash__(self):
        var = 3
        for rect in self.packedRects:
            var = 59 * var + hash(rect)
        return var
    
    
    def __repr__(self):
        return "Bin: " + str(self.getOccupancy())