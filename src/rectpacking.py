__author__  = "Ahmed Hassan"
__license__ = "MIT License"
__email__   = "ahmedhassan@aims.ac.za"
__status__  = "Production"

import random as rng  
import copy 

from typing import List  

from rect import Rect   
from solution import RBPSolution
from bin import PackingHeuristic
from instance import Instance
  
  
class RectPacking:
    """A class to implement the two-dimensional bin packing problem.

    Attributes
    ----------
    seed : int
        a seed for the random number generator
    """     
    
    
    
    def __init__(self, seed):
        self.seed = seed
        rng.seed(seed)        
        self.instanceID = -1
        # instance list
        self.instanceList = []
        # default packing heuristic
        self.packHeur = PackingHeuristic.BestAreaFit        

        
    def loadInstance(self, path: str):
        """Read the problem instance from a file.

        Parameters
        ----------
        path : str
            Path to the file defining the problem instance
        """
        line = None
        rectList = []
        numItems = -1
        #Count the number of headings
        headingLines = 0 
        #Mark the beginning of reading a new instance. A problem file contains 50 instances
        isNewInstance = False 
        instance = Instance()
        f = open(path, 'r')
        for line in f:
            tokens = line.split()
            if len(tokens) == 0: #file contains new lines to separate instance
                instance.loadRectToPack(rectList)
                self.instanceList.append(instance)
                continue              
            if "PROBLEM" in line:
                isNewInstance = True
                headingLines += 1
                instance = Instance()
                continue #read the next             
            if(isNewInstance):
                #First heading is number of items
                if headingLines == 1:
                    numItems = int(tokens[0].strip())
                    rectList = []
                    headingLines += 1
                #Second heading is the numbering of the instances
                elif headingLines == 2:
                    headingLines += 1
                #Third heading is the bin dimensions
                elif headingLines == 3:
                    binWidth = int(tokens[0].strip())
                    binHeight = int(tokens[1].strip())
                    instance.setBinDim(binWidth, binHeight)
                    headingLines = 0 #heading lines are done. reset the count
                    isNewInstance = False
                else: pass                            
            else: #Not a new instance
                width = int(tokens[0].strip())
                height = int(tokens[1].strip())
                rect = Rect(width, height)
                #instance.loadRect(rect)
                rectList.append(rect)
        f.close()
    

    def getProblemSize(self) -> int:
        """Get the problem size which is the number of items to be packed.

        Returns
        -------
        int
            The problem size
        """
        return instanceList[instanceID].size()
           
    
    def getEmptySolution(self) -> RBPSolution:
        """Get an empty solution.

        A solution is empty if does not have any bins. Use this method if you
        want to pack the items using your defined packing heuristic instead of
        the default packing heuristic.

        Returns
        -------
        solution.RBPSolution
            An empty solution
        """
        instance = self.instanceList[self.instanceID]
        sol = RBPSolution(instance.binWidth, instance.binHeight) 
        # Get a random seed
        sol.seed(rng.randint(1, 1e5))
        return sol

    
    def setInstanceID(self, instanceID: int) -> None:
        """Set the instance to be solved.

        Recall that there 50 instances defined in each file.

        Parameters
        ----------
        instanceID : int
            A unique integer identifier for the instance in [0, 49].
        """
        self.instanceID = instanceID 
            
    
    def initializeSolution(self, sort=True) -> None:
        """Initialize a solution.

        Parameters
        ----------
        sort : bool
            Whether to sort the items before packing ``sort=True`` or shuffle the items ``sort=False``
        """
        instance = self.instanceList[self.instanceID]
        sol = RBPSolution(instance.binWidth, instance.binHeight) 
        sol.seed(rng.randint(1, 1e5))
        #Get a clone of the items
        rectList = self.getPackingQueue() 
        
        if sort:
            # Sort rects by their areas
            rectList.sort(reverse=True)
        else:
            # Randomize the order
            rng.shuffle(rectList)

        # Pack rects
        sol.pack(rectList, self.packHeur)

        # Comment the following two lines if you want to skip checking whether the created solution 
        # is valid. If you leave it, this will slow the initial solution creation a bit.
        if not sol.isFeasible():
            raise RuntimeError("Initial solution is not feasible")
        return sol
        
    
    def getPackingQueue(self) -> List[Rect]:
        """Get the list of items to be packed.

        Returns
        -------
        List[Rect]
            A list of items to be packed
        """
        instance = self.instanceList[self.instanceID]
        return copy.deepcopy(instance.queue)
    

    def getDefaultPackHeur(self) -> PackingHeuristic:
        """Get the default packing heuristic that is used when initializing new solutions.

        Returns
        -------
        bin.PackingHeuristic
            The default packing heuristic
        """
        return self.packHeur
            

    def setDefaultPackHeur(packHeur: PackingHeuristic) -> None:
        """Set the default packing heuristic that is used when initializing new solutions."""
        this.packHeur = packHeur
    


if __name__ == "__main__":
    problem = RectPacking(12345)
    filename = "D:\\Data\\RBP\\Class_10.2bp"
    print("Loading: ", filename)
    problem.loadInstance(filename)
    instID = 0
    print("Solving instance: ", instID)    
    problem.setInstanceID(instID)    
    # Create an initial solution
    # sort=False means that the items will be randomly shuffled before packing
    # If sort=True the items will be sorted in a descending order of their area
    solution = problem.initializeSolution(sort=False)
    # Check if the solution is valid
    if not solution.isFeasible():
        raise RuntimeError("Infeasible solution")
    print("Number of bins = ", solution.getNumberOfBins())
    print(f"Packing heuristic used: {problem.packHeur}\n")

    print("Solving instance: ", instID)  
    soltuion = problem.getEmptySolution()
    rectList = problem.getPackingQueue()
    rng.shuffle(rectList)
    solution.pack(rectList, PackingHeuristic.TouchingPerimeter)
    if not solution.isFeasible():
        raise RuntimeError("Infeasible solution")
    print("Number of bins = ", solution.getNumberOfBins())
    print("Packing heuristic used: ", PackingHeuristic.TouchingPerimeter)    
