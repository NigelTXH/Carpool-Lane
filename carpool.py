from ctypes import py_object
from typing import TypeVar, Generic
import math
T = TypeVar('T')


class ArrayR(Generic[T]): #Credit to FIT1008 for giving me this class
    def __init__(self, length: int) -> None:
        """ Creates an array of references to objects of the given length
        :complexity: O(length) for best/worst case to initialise to None
        :pre: length > 0
        """
        if length <= 0:
            raise ValueError("Array length should be larger than 0.")
        self.array = (length * py_object)() # initialises the space
        self.array[:] =  [None for _ in range(length)]

    def __len__(self) -> int:
        """ Returns the length of the array
        :complexity: O(1)
        """
        return len(self.array)

    def __getitem__(self, index: int) -> T:
        """ Returns the object in position index.
        :complexity: O(1)
        :pre: index in between 0 and length - self.array[] checks it
        """
        return self.array[index]

    def __setitem__(self, index: int, value: T) -> None:
        """ Sets the object in position index to value
        :complexity: O(1)
        :pre: index in between 0 and length - self.array[] checks it
        """
        self.array[index] = value




class Heap2(Generic[T]): #Credit to FIT1008 for giving me this class. However, I had to modify for a minheap and vertices
    MIN_CAPACITY = 1

    def __init__(self, max_size: int) -> None:
        self.length = 0
        self.the_array = ArrayR(max(self.MIN_CAPACITY, max_size) + 1)

    def __len__(self) -> int:
        return self.length

    def is_full(self) -> bool:
        return self.length + 1 == len(self.the_array)

    def rise(self, k: int) -> None:
        """
        Rise element at index k to its correct position
        :pre: 1<= k <= self.length
        """
        while k > 1 and self.the_array[k].distance < self.the_array[k // 2].distance:
            self.swap(k, k // 2)
            k = k // 2
            
    def swap(self,k1,k2):
        """
        Function Description: Swaps the position of 2 elements given both elements' position.
        Only difference from a standard heap is that the element is a vertex, so I also need
        to manually change the vertex's pos property manually.
        """
        temp = self.the_array[k2]
        self.the_array[k2] = self.the_array[k1]
        self.the_array[k1] = temp
        
        temp = self.the_array[k2].pos
        self.the_array[k2].pos = self.the_array[k1].pos
        self.the_array[k1].pos = temp
        

    def add(self, element: T) -> bool:
        """
        Function description: Adds an element and rise it. Only difference from a normal heap
        is that an element which is the vertex, the vertex.pos is self.length because
        self.the_array[self.length] = element.
        """
        has_space_left = not self.is_full()
        if has_space_left:
            self.length += 1
            self.the_array[self.length] = element
            element.pos = self.length
            self.rise(self.length)   
        return has_space_left

    def smallest_child(self, k: int) -> int:
        """
        Returns the index of the smallest child of k.
        pre: 2*k <= self.length (at least one child)
        """
        if 2 * k == self.length or self.the_array[2 * k].distance < self.the_array[2 * k + 1].distance:
            return 2*k
        else:
            return 2*k+1
        
    
    def smallest_child2(self, k: int) -> int:
        """
        Returns the smallest child of k.
        pre: 2*k <= self.length (at least one child)
        """
        if 2 * k == self.length or self.the_array[2 * k] < self.the_array[2 * k + 1]:
            return self.the_array[2 * k]
        else:
            return self.the_array[2 * k + 1]
        
    def get_min(self,k):
        lst = []
        while self.length != 0:
            lst.append(self.the_array[1])
            temp = self.the_array[1]
            self.the_array[1] = self.the_array[self.length]
            self.the_array[self.length] = temp
            self.length -= 1       
            self.sink(1)
        return lst
            
    def serve(self):
        if self.length != 0:
            self.swap(1,self.length)
            serve = self.the_array[self.length]
            self.length -= 1
            self.sink(1)     
            return serve
        return "Empty"

    def sink(self, k: int) -> None:
        """ Make the element at index k sink to the correct position """
        while 2*k <= self.length:
            child = self.smallest_child(k)
            if self.the_array[k].distance <= self.the_array[child].distance:
                break
            self.swap(child, k)
            k = child


class Graph:
    def __init__(self,start, V, passengers, min_element,end) -> None:
        """
        Function description: Constructor in the graph class. When this object is created initially,
                              Creates a graph with (2 * original number of locations) starting from the min_element
                              to V. After that, check if the location with passengers are valid and link it with the
                              alternate equivalent (An alternate location would be the original location + V//2).
        Approach description (if main function):
        :Input:
        Start: The location expressed as an integer used to check if the location of passenger is at the starting location
        V: An integer telling the amount of locations in the graph
        passengers: A list of integers which tells which locations have passengers
        min_element: An integer to tell the location with the smallest number.
        :Postcondition:
        A graph will be created with locations from [min_element,V+min_element]. After that, add an edge from the location with passengers
        with the alternate equivalent of the location with passengers which is (passenger location + V//2).
        :Time complexity:
        self.vertices: O(|L|) because we extend the original list by V times
        self.link: O(|P|log(|L|)) because we perform an addEdge function which is O(log(|L|))
                   time complexity |P| times.
        First for loop (for i in range(V)): O(|L|) because we are replacing all the None with the vertex object and there are V amount of None
        
        In the worst case, the maximum amount of passengers possible is V-2, so |P| = O(V).
        Hence O(|L| + |P| + |L| + |L|log(|L|)) so O(|L|log(|L|))
        :Aux space complexity:
        self.vertices = O(|L|) because self.vertices will have 2 * |L|
        The other variables are O(1), excluding the input
        So worst case aux space complexity is O(|L|)
        """
        self.vertices = [None] * V #O(2V)
        self.link = False

        for i in range(V): # O(2V)
            self.vertices[i] = Vertex(i+min_element)
        self.link = self.can_link(passengers,start,end) #O(P)

            
    def can_link(self, passengers, start,end): #O(|P|log(|L|))
        """
        Function description: Takes in passengers which is a list of locations with passengers, start which is starting location
        and end which is the destination. Outputs true if one of the locations are valid to have passengers. For every valid passenger,
        add an edge. Time complexity is O(|P|log(|L|)) because if all locations are valid, then the addEdge function
        which runs O(log(|L|)) runs |P| times so O(|P|log(|L|)). The aux space complexity is O(P) because an edge
        is added to each valid passenger location. 
        """
        output = False
        if len(passengers) > 0:
            for vertex in passengers:
                if (vertex != start or vertex != end) and vertex < (len(self.vertices)//2): #Check if passenger is start or end
                    self.addEdge(vertex,int(vertex + (len(self.vertices)/2)),0)             #Also check if only in original locations, not alternate
                    output = True
        return output                                                                      
                    


            
    def findVertex(self, key, low, high): #Taken from https://www.programiz.com/dsa/binary-search
        #O(log(V))
        if high >= low:

            mid = low + (high - low)//2
            # If found at mid, then return it
            if self.vertices[mid].id == key:
                return self.vertices[mid]

            # Search the left half
            elif self.vertices[mid].id > key:
                return self.findVertex(key, low, mid-1)

            # Search the right half
            else:
                return self.findVertex(key, mid + 1, high)
        else:
            return "Not found"
            
    def addEdge(self,source,destination,weight):
        """
        Function description: A function when given the source, destination and weight,
        will append the edge to the vertex. Time complexity is O(log(|L|)) due to find_vertex
        function. The aux space complexity is O(1) because only 1 edge classes are appended to an
        already existing list.
        """
        start = self.findVertex(source,0,len(self.vertices)-1)
        
        end = self.findVertex(destination,0,len(self.vertices)-1)
        if start.id == source and end.id == destination:
            start.edges.append(Edge(source,destination,weight))        
            
    def addTuple(self, tuple: tuple, V: int): # O(2logV) so just O(logV),
        """
        Function description: A function that when given a tuple in the form
        (u,v,w1,w2) where u is source, v is destination, w1 is one of the weight
        which is only travelled if no extra passengers and w2 is the other weight
        where it is travelled if have extra passengers. V is the amount of locations.
        Two edges will be appended to the original vertex and the alternate equivalent.
        The time complexity is O(log(|L|)) due to find_vertex function, the aux space complexity is O(1) because
        2 edge classes are appended and other than that, no other data structures
        were created.
        """
 
        start = self.findVertex(tuple[0],0,len(self.vertices)-1)
        end = self.findVertex(tuple[1],0,len(self.vertices)-1) 
        if start.id == tuple[0] and end.id == tuple[1]:
            for i in range(2):
                start = self.findVertex(tuple[0] + (i * V),0,len(self.vertices)-1) #O(logV)
                start.edges.append(Edge(tuple[0] + (i * V),tuple[1] + (i * V),tuple[2+i]))
                
    #Worst case is O(Elog(V)) because in worst case, every vertices is visited
                                            # which results in E edges visited.
    def dijkstra(self, source, destination):
        """
        Function description: A function used to find the optimal route from source to destination.
                              Compared to a normal dijkstra algorithm, since there are 2 * (orignal number of locations) unless there are no passengers.
                               
                              If there are passengers, the first half of the locations will represent the distance and route to the destination
                              if there are no extra passengers and the second half of the locations represents the distance and route to the destination 
                              if there are extra passengers. Therefore comparing the 2 destinations to see which
                              distance is the best and returning the favourable route to get to the best distance.
                              
                              If there are no passengers, then self.link is false because there are no passengers
                              and will find the shortest path towards the destination without any comparison to
                              anything else.
                              
        Approach description:
        :Input:
        source: Starting location from the set {0,1...L-1} where L is total locations
        destination: Ending location from the set {0,1...L-1} where L is total locations
        
        :Output:
        A path represented by a list so for example [0,1,2,1] represents going from location 0 to location 1
        to location 2 and back to location 1.
        
        :Time complexity:
        Adding the source to the heap called discovered: O(|1|) because no rises ever occur
        While loop: Runs O(|L|) time complexity because all locations can be met twice
        Variable called served: O(|L|log(|L|)) because of the sink operation which is O(log(|L|)) running O(|L|) times
        return_statement: At worst, backtracking to the source node totalling up to |R| so O(|R|) and findvertex function
                               is O(log(|L|)) but is ran |R| times so in total is O(|R|log(|L|))
        Second for loop (for vertex in self.vertices:): O(|L|) because I am resetting all the properties for each location
        Third for loop (for t in range(len(return_statement))): O(|E|) because return_statement variable can never go beyond a length of 2 * |E|
        Fourth for loop (for p in range(len(return_statement))): O(|E|) because return_statement variable can never go beyond a length of 2 * |E|
        Fifth for loop (Finding adjacent locations): O(|L|^2) because at most the original destination and alternate destination will have |L|-1 neighbours but
                                                     since that it is running O(|L|) times so O(|L|^2)
        discovered.add(): O(|L|^2log(|L|)) worst case when a location will have |L|-1 neighbours and adds all these
                        neighbours which takes O(log(|L|)) because of the rise operation running O(|L^2|) times
                        because of the fifth for loop.
        discovered.rise(): O(|L|^2log(|L|)) worst case when there are approximately |L| locations and the rise takes
                          O(log(|L|)). However, it is running O(|L^2|) times because of the fifth for loop thus it will
                          be O(|L|^2log(|L|))
                          
        In total, it will be O(1 + |L| + |L|log(|L|) + |L| + |L|+ |L| + |L|^2 + |L|^2log(|L|) + |L|^2log(|L|))
        The highest order is O(|L|^2log(|L|)) and since that the edges represents roads, the maximum amount of roads
        is O(|L|^2) so O(|R|) = O(|L|^2). Therefore this algorithm takes O(|R|log(|L|))
                                                     
        :Aux space complexity:
        visited_vertices: O(|L|) because at most, 2 * |L| are visited
        discovered: O(|L|) because less than 2*L will be added to discovered
        return_statement: O(|R|) because backtracking function can add to the list a total of |R| times
        true_return: Same as return_statement
        served.previous: O(1)
        child.previous: Same as served.previous
        served.edges: Worst case is where all stored adjacent edges are used to loop so O(|R|)
        
        In total is O(|L| + |L| + |L| + |L| + |L| + |R|)
        Therefore the aux space complexity is O(|L| + |R|)
        """
        
        def backtracking(vertex): #OElogV (Explained in the dijkstra documentation)
            if vertex.previous == None:
                return []
            return backtracking(self.findVertex(vertex.previous,0,len(self.vertices)-1)) + [vertex.previous]

        
        source_vertex = self.findVertex(source,0,len(self.vertices)-1)
        source_vertex.discovered = True
        source_vertex.distance = 0
        visited_vertices = [] # O(V)
        discovered = Heap2(len(self.vertices) * 2) # O(V)
        discovered.add(source_vertex)
        count = 0
        best = 0 #Best distance for destination
        best_vertex = 0 #Best vertex to choose for destination
        return_statement = [] # O(V), is equivalent to worst case of child.previous variable

            
        
        while len(discovered) > 0: # O(V) because in worst case, all vertices are visited
            served = discovered.serve() #O(logV) because of the sink operation which is O(log(V))
            visited_vertices.append(str(served))
            served.visited = True
            if served.is_destination:
                true_return = [] #Space goes up to O(V), same as return_statement
                count += 1
                if (best > served.distance) and count > 1:
                    best = served.distance
                    best_vertex = served
                elif count == 1:           
                    best = served.distance
                    best_vertex = served
                #reset all the vertices discovered and visited because if ran twice, the discovered and visited does not reset
                if count == 2 or self.link == False:
                    return_statement = backtracking(best_vertex)
                    return_statement.append(best_vertex.id)
                    for vertex in self.vertices: #O(V)
                        vertex.visited = False
                        vertex.discovered = False
                        vertex.distance = 0
                        vertex.previous = -1
                        vertex.is_destination = False
                    for t in range(len(return_statement)): #O(V) worst case
                        if return_statement[t] >= len(self.vertices)//2 + self.vertices[0].id:
                            return_statement[t] -= len(self.vertices)//2
                            
                    for p in range(len(return_statement)): #O(V) worst case
                        if p + 1 == len(return_statement):
                            true_return.append(return_statement[p])
                        elif not return_statement[p] == return_statement[p+1]:
                            true_return.append(return_statement[p])
                    print(best)
                    return true_return

            for edge in served.edges: # O(V) because at most a vertex will have V-1 neighbours
                #In total will be O(VlogV) because the algorithm goes through an edge and may rise it
                child = self.findVertex(edge.destination,0,len(self.vertices)-1)
                
                if child.discovered == False:
                    child.discovered = True
                    child.distance = served.distance + edge.weight
                    child.previous = served.id #V-1 vertices can be visited (a line of vertices
                                                                  #and last vertex is the destination) so O(V)
                    discovered.add(child) #O(log(V))
                    
                elif child.visited == False:
                    if child.distance > served.distance + edge.weight:
                        child.distance = served.distance + edge.weight
                        child.previous = served.id
                        discovered.rise(child.pos) #O(log(V)) because will not have more than 2V and 
                    
    def addVertex(self, V): #O(V) complexity to check every vertices
        addToList = True
        for vertex in self.vertices:
            if V == vertex.id:
                addToList = False              
        if addToList == True:
            self.vertices.append(Vertex(V))
        else:
            print("no")
                          
    def __str__(self) -> str:
        return_string = ""
        for vertex in self.vertices:
            expand_edges = ""
            for edge in vertex.edges:
                expand_edges = str(edge) + expand_edges
            return_string = return_string + "Vertex " + str(vertex) + expand_edges + "\n"
        return return_string
    
class Vertex:
    def __init__(self, id) -> None:
        self.pos = 1 
        self.id = id
        self.edges = []
        self.visited = False
        self.discovered = False
        self.distance = math.inf
        self.previous = None
        self.is_destination = False
     
    def __str__(self) -> str:
        return_string = str(self.id)
        return return_string
    
class Edge:
    def __init__(self,source,destination,weight) -> None:
        self.source = source
        self.destination = destination
        self.weight = weight
 
    def __str__(self) -> str:
        return_string = ""
        return_string = " " + str(self.destination) + "/" + str(self.weight) + " | "
        return return_string