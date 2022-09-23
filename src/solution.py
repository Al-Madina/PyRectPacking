__author__  = "Ahmed Hassan"
__license__ = "MIT License"
__email__   = "ahmedhassan@aims.ac.za"
__status__  = "Production"


import random as rng 
from typing import List  

from rect import Rect  
from bin import Bin, PackingHeuristic  
from maxspace import MaxSpaceBin


class RBPSolution:
    """A class implementing a solution for the two-dimensional bin packing problem.

    Attributes
    ----------
    binWidth : int
        The width of the bin (the length of the side parallel to  the x-axis).
    binHeight : int
        The height of the bin (the length of the side parallel to  the y-axis).
    binList : List[bin.Bin]
        The list of bins
    rectList : List[rect.Rect]
        The list of items
    """

        
    def __init__(self, width: int, height: int):
        self.binWidth = width
        self.binHeight = height
        self.binList = [] 
        self.rectList = None
        self.numRects = None
        self.lowerbnd = None        
        


    def seed(self, seed):
        """Seed the random number of this solution with `seed`.

        Parameters
        ----------
        seed : int
            The seed for the random number generator for this solution
        """
        rng.seed(seed)
    

    def pack(self, rectList: List[Rect]=None, heur: PackingHeuristic=None, first=False):
        """Pack the items in `rectList` using a specified packing heuristic.

        Parameters
        ----------
        rectList : List[Rect]
            The list of items to be packed
        heur : PackingHeuristic
            The packing heuristic
        first : bool
            Whether to pack the item in the first available bin (if True) or in the best bin (if False)
        """

        # Compute a continuous lower bound on the number of bins
        self.binList = []
        if rectList: self.rectList = rectList        
        if not self.lowerbnd:
            self.numRects = len(rectList)
            self.lowerbnd = self.computeLowerBound(rectList) 
        self.binList = []

        # Initialize bins
        if not first:
            for i in range(self.lowerbnd):
                self.binList.append(self.openNewBin()) 
        else:
            self.binList.append(self.openNewBin())

        # Consider packing the rects according to their order
        for curRect in self.rectList:            
            bestValue1 = float('inf')
            bestValue2 = float('inf')
            bestBin = None 
            bestRect = None
            
            # Determine the best bin for the current rect
            for abin in self.binList:
                curRect.removePackingInfo()
                newRect = abin.evaluatePacking(curRect, heur) # returns None if rect cannot be inserted
                if newRect != None and (newRect.score1 < bestValue1 or (newRect.score1 == bestValue1 and newRect.score2 < bestValue2)):
                    bestValue1 = newRect.score1
                    bestValue2 = newRect.score2
                    bestBin = abin
                    bestRect = newRect
                            
            #if a bin is found, pack rect
            if(bestBin != None):
                bestBin.insert(bestRect, heur)
            
            #otherwise, open a new bin
            else:
                newBin = self.openNewBin()
                newBin.insert(curRect, heur) #no need to evaluate packing
                self.binList.append(newBin)
    
    
    def removeAndRepack(self, heur: PackingHeuristic, percentage: float, reverse: bool, sort: bool, first=False) -> float:
        """A ruin-and-recreate heuristic.

        Parameters
        ----------
        heur: PackingHeuristic
            The packing heuristic
        percentage: float
            The percentage of items to remove. A percentage of 1.0 means remove all items.
        reverse: bool
            Whether to remove the last-packed items (True) or the first-packed items (False).
        sort: bool
            Whether to sort the removed items before repacking them (True) or perturb them (False).
        first: bool
            Whether to pack the item in the first available bin (if True) or in the best bin (if False)
        """
        
        if percentage < 0 or percentage > 1:
            raise ValueError("The value of percentage should be in the range [0, 1]")

        if not self.rectList:
            raise RuntimeError("The current solution has no items. Please call `Solution.pack` first.")
        
        # Determine the number of items to remove
        number = int(percentage*self.numRects + 1)
        # At least remove two items
        number = max(number, 2)
        
        if reverse:
            subList = self.rectList[:number]
        else:
            subList = self.rectList[self.numRects-number:]
            
        if sort:
            subList.sort(reverse=True)
        else:
            self.perturb(subList) # We perturb it twice if not sort since perturb by design do a small perturbation
        
        # Slicing will create a copy of the list. Need to update the original list
        if reverse:
            self.rectList[:number] = subList
        else:
            self.rectList[self.numRects-number:] = subList

        # Packed the removed items
        self.pack(heur=heur, first=first)
        
    
    def isFeasible(self):   
        """Determines whether the current solution is feasible"""     
        if len(self.binList) < self.lowerbnd: return False
        for aBin in self.binList:
            if not aBin.isFeasible():
                return False            
        return True
            
 
    def openNewBin(self) -> Bin:
        newBin = MaxSpaceBin(self.binWidth, self.binHeight)
        newBin.init()
        return newBin
    
    
    def computeLowerBound(self, rectList) -> int:
        area = 0
        for rect in rectList:
            area += rect.width * rect.height        
        return int(area/(self.binWidth*self.binHeight) + 1) #ceiling
        
    
    def getLeastFilledBin(self) -> Bin:
        least = 2
        leastFilled = None
        for abin in self.binList:
            if abin.getOccupancy() <= 0 or abin.getOccupancy() > 1:
                raise RuntimeError("Wrong occupancy")
            if abin.getOccupancy() < least:
                least = abin.getOccupancy()
                leastFilled = abin
        return leastFilled  
    
    
    def getNumberOfBins(self) -> int:
        return len(self.binList)
    
    
    def solutionValue(self) -> float:
        return self.getNumberOfBins() + self.getLeastFilledBin().getOccupancy()
    
    
    def size(self):
        return self.numRects

    
    def getWastedArea(self):
        wastedArea = 0
        for aBin in self.binList:
            wastedArea += 1 - aBin.getOccupancy()
        return wastedArea
    

    def distance(self, sol):
        return abs(self.getWastedAreas() - sol.getWastedAreas())
    
    
    def swap(self, subList, idx1, idx2):
        tmp = subList[idx1]
        subList[idx1] = subList[idx2]
        subList[idx2] = tmp
            
            
    def perturb(self, subList):
        if len(subList) <= 2:
            return
            
        strength = 0.025 + 0.125*rng.random()             
        number = int(strength*len(subList) + 0.5)
        number = max(number, 1)
        for _ in range(number):
            idx1 = rng.randint(0, len(subList)-1)
            idx2 = rng.randint(0, len(subList)-1)
            while idx2 == idx1:
                idx2 = rng.randint(0, len(subList)-1)
            self.swap(subList, idx1, idx2)
    
    def __repr__(self):
        st = ""
        for i in range(len(self.binList)):
            aBin = self.binList[i]
            st += "Bin " + str(i) + ": n = " + str(len(aBin.getPackedRects())) + " occupancy = " \
                + str(aBin.getOccupancy()) + "\n"        
        return st