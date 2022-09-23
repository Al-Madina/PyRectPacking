__author__  = "Ahmed Hassan"
__license__ = "MIT License"
__email__   = "ahmedhassan@aims.ac.za"
__status__  = "Production"


class Rect:
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.area = width * height
        self.score1 = float('inf')
        self.score2 = float('inf')
        self.x = -1 #not packed yet
        self.y = -1
        self._id = -1
        
        
        def getid(self):
            return self._id
        def setid(self, x):
            self._id = x
        def delid(self):
            del self._id
        rectid = property(getid, setid, delid)

    
    def rotate(self) -> None:
        tmp = self.width
        self.width = self.height
        self.height = tmp
        
    
    def isDegenerate(self) -> bool:
        #if a rect reduces to a line or a point
        return self.width == 0 or self.height == 0
    
    
    def isReadyForPacking(self) -> bool:
        return self.x != -1 and self.y != -1 #position in bin is found
    
    
    def removePackingInfo(self) -> None:
        self.x = -1
        self.y = -1
        self.score1 = float('inf')
        self.score2 = float('inf')
    
    
    def computeCommonHorizLength(self, rect) -> int:
        r1x1 = self.x 
        r1x2 = self.x + self.width
        r2x1 = rect.x 
        r2x2 = rect.x + rect.width
        return min(r1x2, r2x2) - max(r1x1, r2x1)
    
    
    def computeCommonVertLength(self, rect) -> int:
        r1y1 = self.y 
        r1y2 = self.y + self.height
        r2y1 = rect.y 
        r2y2 = rect.y + rect.height
        return min(r1y2, r2y2) - max(r1y1, r2y1)
    

    def isContainedIn(self, rect) -> bool:
        #note that isContained covers equals!
        return self.x >= rect.x and self.y >= rect.y\
               and self.x + self.width <= rect.x + rect.width\
               and self.y + self.height <= rect.y + rect.height
    
    
    def computeCommonLength(self, start1: int, end1: int, start2: int, end2: int) -> int:
        if(start2 >= end1 or end2 <= start1): return 0
        return min(end1, end2) - max(start1, start2)
    
    
    def isOverlapping(self, rect) -> bool:
        #if overlaps horizontally
        if(not(self.x >= rect.x + rect.width or self.x + self.width <= rect.x)):
            if(self.computeCommonLength(self.y, self.y+self.height, rect.y, rect.y+rect.height) > 0):
                return True
        
        #if vertically overlaps
        elif(not(self.y >= rect.y + rect.height or self.y + self.height <= rect.y)):
            if(self.computeCommonLength(self.x, self.x+self.width, rect.x, rect.x+rect.width) > 0):
                return True        
        else:
            return False
        return False
    
        
    def __eq__(self, other) -> bool:        
        if not isinstance(other, self.__class__): return False
        return other.width == self.width and other.height == self.height
    
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, self.__class__): return False
        return self.width*self.height < other.width*other.height
    
    def __le__(self, other) -> bool:
        if not isinstance(other, self.__class__): return False
        return self.__lt__(other) or self.width*self.height == other.width*other.height
    
    def __gt__(self, other) -> bool:
        return not self.__lt__(other) and (self.width*self.height != other.width*other.height)
    
    def __ge__(self, other) -> bool:
        return not self.__lt__(other)

    def __hash__(self):
        var = 7
        var = 79 * var + self.width
        var = 79 * var + self.height
        var = 79 * var + self.x
        var = 79 * var + self.y
        return var
    
    
    def __repr__(self) -> str:
        return "Rect: (" + str(self.width) + ", " + str(self.height) + ", " + str(self.score1) + ")"
    