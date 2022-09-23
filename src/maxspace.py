__author__  = "Ahmed Hassan"
__license__ = "MIT License"
__email__   = "ahmedhassan@aims.ac.za"
__status__  = "Production"


import copy  

from rect import Rect  
from bin import Bin, PackingHeuristic 


# Does nothing except for enabling the eye-candy "override" notation
def Override(f): return f


class MaxSpaceBin(Bin):
    """A class implementing the maximal space bin.

    Notes
    -----
    Maximal space data structure : https://www.sciencedirect.com/science/article/pii/S0925527313001837
    """
    
    def __init__(self, binWidth, binHeight):
        super().__init__(binWidth, binHeight)
    
    @Override
    def setupFreeRects(self) -> None:
        #Initialize a list for the maximal spaces
        self.freeRects = []
        maxSpace = Rect(self.binWidth, self.binHeight)
        maxSpace.x = 0
        maxSpace.y = 0
        self.freeRects.append(maxSpace)

    
    @Override
    def evaluatePacking(self, rect: Rect, heur: PackingHeuristic) -> Rect:
        """Evaluate the quality of packing an item using a specified packing heuristic.

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
        if not self.packHeur: self.packHeur = heur
        newRect = None
        if heur == PackingHeuristic.BestAreaFit: 
            newRect = self.insertBestArea(rect)
        elif heur == PackingHeuristic.TouchingPerimeter: 
            newRect = self.insertTouchingPerimeter(rect)
        elif heur == PackingHeuristic.TopRightCornerDistance: 
            newRect = self.insertTopRightCornerDistance(rect)
        else:
            raise ValueError("Unkown packing heuristic")
        
        return newRect
    
    
    @Override
    def insert(self, rect: Rect, heuristic: PackingHeuristic) -> bool:
        """Insert an item in this bin using the specified packing heuristic to determine its location
        inside the bin. 

        This method insert the item immediately if the method evaluatePacking is invoked on this item.
        This is because evaluatePacking determines the location of the item when invoked as a by-product
        of evaluating its packing quality in this bin. If evaluatePacking is not invoked on this item, 
        then this method will call it first.

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
        #Check whether rect is ready for packing, i.e., method evaluatePacking has already been invoked on this rect
        if not rect.isReadyForPacking():
            newRect = self.evaluatePacking(rect, heuristic) # returns a degenerate rect if packig is not possible                
        else:
            newRect = rect
        
        #If packing rect is not possible
        if newRect == None:
            return False
        
        #rect can be packed in the bin, update the data structure
        self.packRect(newRect)
        self.generateNewMaxSpaces(newRect)
        #remove degenerate and non-maximal spaces
        self.pruneMaxSpaces()        
        return True

    
    def insertTopRightCornerDistance(self, rect: Rect) -> Rect:
        """Pack an item using ``bin.PackingHeuristic.TopRightCornerDistance`` packing heuristic

        Parameters
        ----------
        rect : rect.Rect
            The item to pack

        Returns
        -------
        rect.Rect
            returns a new rect with its packing information set if the packing in this
            bin is possible. Otherwise, returns ``None``
        """
        largestDist = -1
        bestMaxSpaceIndex = -1
        isRotated = False
        for i in range(len(self.freeRects)):
            maxSpace = self.freeRects[i]
            #Try to fit rect into maxSpace in upright position
            if rect.width <= maxSpace.width and rect.height <= maxSpace.height:
                dist = self.computeDistance(maxSpace.x + rect.width, maxSpace.y + rect.height,\
                                            self.binWidth, self.binHeight)
                if dist > largestDist:
                    largestDist = dist
                    bestMaxSpaceIndex = i
                    isRotated = False                            
            #If rotation is possible, try to fit rect in
            if self.canRotate and rect.height <= maxSpace.width and rect.width <= maxSpace.height:
                dist = self.computeDistance(maxSpace.x + rect.height, maxSpace.y + rect.width, binWidth, binHeight)
                if dist > largestDist:
                    largestDist = dist
                    bestMaxSpaceIndex = i
                    isRotated = True 
                    
        #If rect cannot be inserted into current bin
        if bestMaxSpaceIndex == -1:
            return None
        
        #Insert rect into the best maxSpace with the appropriate orientation
        newRect = Rect(rect.width, rect.height)
        if isRotated: newRect.rotate()
        newRect.x = self.freeRects[bestMaxSpaceIndex].x
        newRect.y = self.freeRects[bestMaxSpaceIndex].y
        newRect.score1 = -largestDist #smaller is better
        return newRect
    
    
    def insertTouchingPerimeter(self, rect: Rect) -> Rect:
        """Pack an item using ``bin.PackingHeuristic.TouchingPerimeter`` packing heuristic

        Parameters
        ----------
        rect : rect.Rect
            The item to pack

        Returns
        -------
        rect.Rect
            returns a new rect with its packing information set if the packing in this
            bin is possible. Otherwise, returns ``None``
        """
        largestTouchingPerimeter = -1
        bestMaxSpaceIndex = -1
        isRotated = False
        for i in range(len(self.freeRects)):
            maxSpace = self.freeRects[i]
            if rect.width <= maxSpace.width and rect.height <= maxSpace.height:
                perimeter = self.computeTouchingPerimeter(maxSpace.x, maxSpace.y, rect.width, rect.height)
                if perimeter > largestTouchingPerimeter:
                    largestTouchingPerimeter = perimeter
                    bestMaxSpaceIndex = i
                    isRotated = False                            
            if self.canRotate and rect.height <= maxSpace.width and rect.width <= maxSpace.height:
                perimeter = self.computeTouchingPerimeter(maxSpace.x, maxSpace.y, rect.height, rect.width)
                if perimeter > largestTouchingPerimeter:
                    largestTouchingPerimeter = perimeter
                    bestMaxSpaceIndex = i
                    isRotated = True
                                    
        if bestMaxSpaceIndex == -1:
            return None
        
        newRect = Rect(rect.width, rect.height)
        if isRotated: newRect.rotate()
        newRect.x = self.freeRects[bestMaxSpaceIndex].x
        newRect.y = self.freeRects[bestMaxSpaceIndex].y
        newRect.score1 = -largestTouchingPerimeter #smaller is better
        return newRect
    
    
    def insertBestArea(self, rect: Rect) -> Rect:
        """Pack an item using ``bin.PackingHeuristic.BestAreaFit`` packing heuristic

        Parameters
        ----------
        rect : rect.Rect
            The item to pack

        Returns
        -------
        rect.Rect
            returns a new rect with its packing information set if the packing in this
            bin is possible. Otherwise, returns ``None``
        """
        bestWastedArea = float('inf')
        bestShortSide = float('inf')
        bestMaxSpaceIndex = -1
        isRotated = False
        for i in range(len(self.freeRects)):
            maxSpace = self.freeRects[i]
            wastedArea = maxSpace.width * maxSpace.height - (rect.width * rect.height)
            if maxSpace.width >= rect.width and maxSpace.height >= rect.height:
                horizLeftOver = maxSpace.width - rect.width
                vertLeftOver = maxSpace.height - rect.height
                shortSide = min(horizLeftOver, vertLeftOver)
                if wastedArea < bestWastedArea or (wastedArea == bestWastedArea and shortSide < bestShortSide):
                    bestWastedArea = wastedArea
                    bestShortSide = shortSide
                    bestMaxSpaceIndex = i
                    isRotated = False                            
            if self.canRotate and maxSpace.width >= rect.height and maxSpace.height >= rect.width:
                horizLeftOver = maxSpace.width - rect.height
                vertLeftOver = maxSpace.height - rect.width
                shortSide = min(horizLeftOver, vertLeftOver)
                if wastedArea < bestWastedArea or (wastedArea == bestWastedArea and shortSide < bestShortSide):
                    bestWastedArea = wastedArea
                    bestShortSide = shortSide
                    bestMaxSpaceIndex = i
                    isRotated = True
                                    
        if bestMaxSpaceIndex == -1:
            return None
        
        newRect = Rect(rect.width, rect.height)
        if isRotated: newRect.rotate()
        newRect.x = self.freeRects[bestMaxSpaceIndex].x
        newRect.y = self.freeRects[bestMaxSpaceIndex].y
        newRect.score1 = bestWastedArea
        newRect.score2 = bestShortSide
        return newRect
    
    
    def generateNewMaxSpaces(self, rect: Rect) -> None:
        """Generates new maximal spaces after packing ``rect``."""
        numFreeRects = len(self.freeRects) #save it because elements will be added
        i = 0
        while i < numFreeRects:
            freeRect = self.freeRects[i]
            if not self.isOverlapping(freeRect, rect): 
                i += 1
                continue
            #Horizontal overlap
            if rect.x < freeRect.x + freeRect.width and rect.x + rect.width > freeRect.x:
                #maxSpace on bottom of rect
                if rect.y >  freeRect.y and rect.y < freeRect.y + freeRect.height:
                    newFreeRect = copy.deepcopy(freeRect)
                    newFreeRect.height = rect.y - freeRect.y
                    self.freeRects.append(newFreeRect)
                
                #maxSpace on top of rect
                if rect.y + rect.height > freeRect.y and rect.y + rect.height < freeRect.y + freeRect.height:
                    newFreeRect = copy.deepcopy(freeRect)
                    newFreeRect.y = rect.y + rect.height
                    newFreeRect.height = freeRect.y + freeRect.height - (rect.y + rect.height)
                    self.freeRects.append(newFreeRect)
                
            
            #Vertical overalp
            if rect.y < freeRect.y + freeRect.height and rect.y + rect.height > freeRect.y:
                #maxSpace left to rect
                if rect.x > freeRect.x and rect.x < freeRect.x + freeRect.width:
                    newFreeRect = copy.deepcopy(freeRect)
                    newFreeRect.width = rect.x - freeRect.x
                    self.freeRects.append(newFreeRect)
                
                #maxSpace right to rect
                if rect.x + rect.width > freeRect.x and rect.x + rect.width < freeRect.x + freeRect.width:
                    newFreeRect = copy.deepcopy(freeRect)
                    newFreeRect.x = rect.x + rect.width
                    newFreeRect.width = freeRect.x + freeRect.width - (rect.x + rect.width)
                    self.freeRects.append(newFreeRect)
                
            
            #FreeRect should be removed as it is intersecting rect
            self.freeRects.pop(i)
            numFreeRects -= 1
            
    
    def pruneMaxSpaces(self):
        """Prune the list of maximal spaces by removing degenerate maximal spaces."""
        toRemove = set()
        for i in range(len(self.freeRects)):
            rectI = self.freeRects[i]
            for j in range(i+1, len(self.freeRects)):
                rectJ = self.freeRects[j]
                #If rect j is contained in rect i
                if rectJ.isContainedIn(rectI):
                    toRemove.add(j)
                
                #If rect i is contained in rect j
                elif rectI.isContainedIn(rectJ):
                    toRemove.add(i)
                    break 
        tmp = [self.freeRects[i] for i in range(len(self.freeRects)) if i not in toRemove]
        self.freeRects = tmp[:]
        if len(self.freeRects) == 0 and self.getOccupancy() < 1.0: raise ValueError("Error")