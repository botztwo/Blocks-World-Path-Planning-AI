from state import State
import itertools
import copy

class Plan:
    def __init__(self, initial_state, goal_state):
        """
        Initialize initial state and goal state
        :param initial_state: list of blocks in the initial state
        :type initial_state: list of block.Block objects
        :param goal_state: list of blocks in the goal state
        :type initial_state: list of block.Block objects
        """
        self.initial_state = initial_state
        self.goal_state = goal_state
        self.steps = 0

    def putdown(self, block1):
        """
        Operator to put the block on the table
        :param block1: block1 to put on the table
        :type block1: Object of block.Block
        :return: None
        """
        table = State.find(self.initial_state, "table")
        if block1.air:
            
            block1.on = table
            block1.clear = True
            block1.air = False
            self.steps += 1


    def unstack(self, block1, block2):
        """
        Operator to unstack block1 from block 2
        :param block1: block1 to unstack from block2
        :type block1: Object of block.Block
        :type block2: Object of block.Block
        :return: None   
        """
        if block1.clear:
            block1.clear = False
            block1.air = True
            block1.on = None

            block2.clear = True
            self.steps += 1
    
    def stack(self, block1, block2):
        #Operator to stack block1 onto block 2
        if block2.clear:
            block1.clear = True
            block1.air = False
            block1.on = block2

            block2.clear = False 
            self.steps += 1


    def pickup(self,block1):
        table = State.find(self.initial_state, "table")

        if block1.on == table:
            block1.clear = False
            block1.air = True
            block1.on = None
            self.steps += 1

            
    def move(self,curr):
    
        self.steps += 1
        print("***************")
        print("Moving")
        print("***************")

   
    def neighbors(self,currentstate):
        #Make 5 lists: putdown, unstack, stack, pickup, move
        putdown = []
        unstack =[]
        stack = []
        pickup = []
        move =[]
        #Make a copy of the current state
        curr = copy.deepcopy(currentstate)
        #Make a table with the initial_state
        #blocks in the air list
        #loop through each block in the state and check whether the block is in the air
        #Add those blocks into the list
        air =[]
        for items in curr:
            if items.air == True:
                air.append(items)
        #blocks on the table and clear list
        #loop through each block in the state and check the appropriate conditions for the blocks to be on table and clear
        #Add those blocks into the list
        ontable_clear = []
        for items in curr:
            if repr(items.on) =='table' and items.clear == True:
                ontable_clear.append(items)
        #blocks that are clear and not on the table
        #loop through each block in the state and check the appropriate conditions for
        #the blocks to be not on table and clear
        #Add those blocks into the list
        nottable_clear = []
        for items in curr:
            if repr(items.on) !='table' and items.clear == True and repr(items) != "table":
                nottable_clear.append(items)

        #if block in air list have element(s) then only do putdown and stack
        if air:
            #putdown
            #copy the state
            tryputdown = copy.deepcopy(curr)#Maybe not curr
            for items in air:#get the equivalent block from the copied state
                block_id = State.find(tryputdown, items.id)
                self.putdown(block_id)#apply the operator
                putdown.append((tryputdown, f"putdown {block_id}")) #add those into putdown list (made in the previous step)

            #stack
            clear = ontable_clear + nottable_clear
                #it is a combination of (blocks_air & blocks_clear) (itertool recommendation)
                #loop through all combinations:
            stackblockproduct = itertools.product(air,clear)
            for block,block1 in stackblockproduct:
                if block.id == block1.id:
                    print("cannot do", block1, block)
                    continue
                if block1.type == 2:
                    continue
                trystack = copy.deepcopy(curr)
                    #make a copy 
                # Figure out the Ids for block and block 1 using find
                block_id = State.find(trystack, block.id)
                block1_id = State.find(trystack, block1.id)
                self.stack(block_id,block1_id) 
                stack.append((trystack, f"stack {block_id, block1_id}"))  
                    #get the equivalent block from the copied state
                    #apply operator for the two blocks in the operator
                    #add those into stack list (made in the previous step)
        else:
    #if the block is not in the air - options: pickup, unstack, move (the steps for these should be somewhat the same as putdown and stack)
        #pickup options       
            for items in ontable_clear:
                trypick = copy.deepcopy(curr)
                block_id = State.find(trypick, items.id)
                self.pickup(block_id)
                pickup.append((trypick, f"pickup {block_id}"))

            #apply pick operator on all blocks that are clear and are on the table
            #Add those into the pick list (made in the previous step)
        #unstack
            for items in nottable_clear:
                tryunstack = copy.deepcopy(curr)
                block_id = State.find(tryunstack, items.id)
                block1_id = State.find(tryunstack, items.on.id)
                self.unstack(block_id,block1_id)
                unstack.append((tryunstack, f"unstack{block_id,block1_id}"))
        return stack+pickup+unstack+putdown+move

    def reachedGoal(self,curr,goal):
        for i in range(len(curr)):
            if curr[i].on == goal[i].on and curr[i].clear == goal[i].clear and curr[i].air == goal[i].air:
                continue
            else:
                return False
        return True 
    
    def inVisited(self,curr,visited):
        for i in range(len(visited)):
            for j in range(len(visited[i])):
                if repr(curr[j].on) != repr(visited[i][j].on) or repr(curr[j].clear) != repr(visited[i][j].clear) or repr(curr[j].air) != repr(visited[i][j].air):
                    break
                if j == (len(visited[i])-1):
                    return True 
        return False
            
                

    def gbfs(self,initial_state,goal):
        Priority_Queue = []
        score = []  
        pathTaken = []
        pathTaken.append(initial_state)
        startingFrom = self.hybridHeuristic(initial_state, goal)
        Priority_Queue.append((startingFrom,initial_state, "Initial_State"))
        gbfs_visited = [initial_state]
        if self.reachedGoal(initial_state,goal):
            State.display(initial_state, message= "Goal State Reached")                   
            return initial_state,pathTaken
        while Priority_Queue:
            Priority_Queue.sort()
            (heuristic,curr, move) = Priority_Queue.pop(-1)
            Priority_Queue = []
            pathTaken.append((curr,move))
            if(self.inVisited(curr,gbfs_visited)==False):
                if self.reachedGoal(curr,goal):
                    State.display(curr, message= "Goal State Reached")                   
                    return curr,pathTaken
                else:
                    gbfs_visited.append(curr)

            neighbors= self.neighbors(curr)
            bestN = []
            for i in neighbors:
                if self.inVisited(i[0],gbfs_visited):
                    continue
                score = self.hybridHeuristic(i[0], goal)
                bestN.append((score,i[0],i[1])) 
                Priority_Queue.append((score,i[0],i[1]))             
        return 0

    def hybridHeuristic(self, curr, goal_state):
        curr_score = 0 
        curr_level = self.getLevels(curr)
        level = self.getLevels(goal_state)
        for i in range(1,len(goal_state)):
            goal_object = State.find(goal_state, goal_state[i].id)
            if curr[i].air == True:
                curr_score += level[i-1] 
            if repr(curr[i].on) == repr(goal_object.on):
                if repr(curr[i].on) == 'table':
                    curr_score += 100
                elif curr_level[i-1] == level[i-1]:
                    curr_score += 30
                else:
                    curr_score -= 10
            else:
                if repr(curr[i].on) == 'table':
                    curr_score += 5
            if curr[i].clear == goal_object.clear:
                curr_score += 1        
        return curr_score
    

    def getLevels(self, goal_state):
        lst = []
        for i in range(1,len(goal_state)):
            temp = goal_state[i]
            level = 0 
            while repr(temp.on) != 'table':
                if temp.air ==True:
                    level = None
                    break
                temp = temp.on
                level -= 1
            lst.append(level)
        return lst


    def sample_plan(self):
        stateFound, pathTaken = self.gbfs(self.initial_state, goal_state_blocks)
        print("GOAL STATE FOUND! THE PATH WE TOOK TO SOLVE THAT PROBLEM: ")
        moveCount = 0
        for i in range(1,len(pathTaken)):
            State.display(pathTaken[i][0], message= pathTaken[i][1])
            if i != len(pathTaken)-1:
                self.move(pathTaken[i][0])
                moveCount += 1 
        print("GOAL STATE FOUND!")
        print("Path takes",len(pathTaken)-1,"states and", moveCount, "moves for a total of",(len(pathTaken)-1 + moveCount), "actions!")
        return 0



if __name__ == "__main__":

    # get the initial state
    initial_state = State()
    initial_state_blocks = initial_state.create_state_from_file("input.txt")
    print(initial_state.blocks)

    #display initial state
    State.display(initial_state_blocks, message="Initial State")

    # get the goal state
    goal_state = State()
    goal_state_blocks = goal_state.create_state_from_file("goal.txt")
    

    #display goal state
    State.display(goal_state_blocks, message="Goal State")

    """
    Sample Plan
    """
    
    p = Plan(initial_state_blocks, goal_state_blocks)
    p.sample_plan()