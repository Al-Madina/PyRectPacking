from typing import List
import copy

from rect import Rect   


class Instance:    
    
    def __init__(self, *args):
        self.binWidth = 0
        self.binHeight = 0
        if len(args) == 2:
            self.binWidth = args[0]
            self.binHeight = args[1]
        # Queue for holding rects for this instance
        self.queue = []
    
    
    def loadRectToPack(self, queue: List[Rect]) -> None:
        self.queue = []
        for i in range(len(queue)):
            rect = queue[i] #copy.deepcopy(queue[i])
            rect.id = i
            self.queue.append(rect)
            
    
    def loadRect(self, rect: Rect):
        self.queue.append(rect)
    
    
    def setBinDim(self, binWidth: int, binHeight: int):
        self.binWidth = binWidth
        self.binHeight = binHeight
    
    
    def isInitialized(self) -> bool:
        return len(self.queue) > 0
    
    
    def __len__(self) -> int:
        return len(self.queue)
    
    def __repr__(self) -> str:
        return "Instance size: " + str(len(self.queue))