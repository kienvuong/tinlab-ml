import math, sys

circle = [1, 0]
cross = [0, 1]

regularNodes = []
inputNodes = []
edges = []

trainingSet = [
    # Rondje (1,0)
    [1, 1, 1,
     1, 0, 1,
     1, 1, 1],

    [0, 1, 0,
     1, 0, 1,
     0, 1, 0],

    # Kruisje (0,1)
    [1, 0, 1,
     0, 1, 0,
     1, 0, 1],

    [0, 1, 0,
     1, 1, 1,
     0, 1, 0]
]


class Node(object):
    def __init__(self):
        self.input = 0
        self.output = 0

    def getInput(self):
        return self.input

    def getOutput(self):
        return self.output

    def setInput(self, input):
        self.input = input

    def setOutput(self, output):
        self.output = output

    #get all edges where this node is source
    def getSourceEdges(self):
        srcEdges = []
        for e in range(0, len(edges)):
            if (edges[e].src == self):
                srcEdges.append(edges[e])
        return srcEdges

    def getDestinationEdges(self):
        destEdges = []
        for e in range(0, len(edges)):
            if (edges[e].dest == self):
                destEdges.append(edges[e])
        return destEdges

    def clearEdges(self):
        self.edges = []

    def sigmoid(self, x):
        return 1 / (1 + math.exp(-x))

    def requestInput(self):
        return None

    def debug(self):
        print("Input: " + str(self.input) + " | Output: " + str(self.output))


class InputNode(Node):
    def __init__(self):
        self.input = 0
        self.output = 0

    def setInput(self, input):
        self.input = input
        self.setOutput(self.sigmoid(self.input))


class RegularNode(Node):
    def getValue(self):
        for edge in self.edges:
            v = self.input + (edge.dest.getValue() * edge.weight)
            # print("DEBUG: " + str(self.input) + " | " + str(edge.dest.getValue()) + " | " + str(edge.weight) + " | " + str(v))
            self.input = v
        self.output = self.sigmoid(self.input)
        # print("DEBUG: "  + str(self.output))
        return self.output

    def requestInput(self):
        for edge in self.getDestinationEdges():
            self.input += (edge.src.getOutput() * edge.weight)
            # print("[DEBUG] self.input: " + str(self.input) + " | edge.src.getOutput: " + str(edge.src.getOutput()) + " | edge.weight: " + str(edge.weight))
        self.output = self.sigmoid(self.input)
        # print("[DEBUG] self.output: " + str(self.output))


class Edge:
    def __init__(self, src, dest, weight):
        self.src = src
        self.dest = dest
        self.weight = weight

    def setWeight(self, weight):
        self.weight = weight

    def getWeight(self):
        return self.weight


def debugInputNodes():
    for i in range(0, len(inputNodes)):
        print(str(inputNodes[i].getInput()) + " | " + str(inputNodes[i].getOutput()))

def debugWeights():
    for i in range(0, len(edges)):
        print(str(edges[i].getWeight()))


def setInputs(matrix):
    for i in range(0, len(matrix)):
        inputNodes[i].setInput(matrix[i])

# alles klaarzetten
def init():
    for i in range(0, 9):
        inputNodes.append(InputNode())

    for i in range(0, 2):
        regularNodes.append(RegularNode())

#iNodes verbinden met rNodes dmv edges
def connectEdges():
    for r in range(0, len(regularNodes)):
        for i in range(0, len(inputNodes)):
            edge = Edge(inputNodes[i], regularNodes[r], 0)
            edges.append(edge)


def normalize(x, y):
    ox = x
    x = x * x
    oy = y
    y = y * y
    z = x + y
    z = math.sqrt(z)
    x = ox / z
    y = oy / z
    return [x, y]


def calcDistance(v1, v2):
    x1 = v1[0]
    y1 = v1[1]
    x2 = v2[0]
    y2 = v2[1]

    return math.sqrt(math.pow((x1 - x2), 2) + math.pow((y1 - y2), 2))


def main():
    # Create empty nodes
    init()
    # Connect empty nodes
    connectEdges()

    #Debug edge connections
    # print(inputNodes[0].getSourceEdges())
    # print("---------------------------------------------------")
    # print(inputNodes[0].getDestinationEdges())
    # print("---------------------------------------------------")
    # print(regularNodes[0].getDestinationEdges())
    # print("_____________________________________________________")

    # Test request input
    # setInputs(trainingSet[0]) #Set values to first matrix in trainingset
    # regularNodes[0].requestInput() #Request all their outputs and set them as inputs for this node
    # regularNodes[1].requestInput() #Request all their outputs and set them as inputs for this node
    # vector = normalize(regularNodes[0].getOutput(), regularNodes[1].getOutput())
    # print(vector)

    #Training/set weights in correct values
    increment = 0.1 #Value to increment weight with
    for x in range(0, 1000):
        bestDistance = 999999999999999999999999.999999999999999999999
        bestIndex = 0
        for i, edge in enumerate(edges):
            #Update weights
            if(i > 0): #If is not first edge then reset previous edge weight
                edges[i-1].weight -= increment
            else: #If first edge then reset last edge weight
                if(x > 0):
                    edges[len(edges)-1].weight -= increment
            edges[i].weight += increment #Increment edge weight

            counter = 0
            distance = 0
            #Loop through training set
            for matrix in trainingSet:
                setInputs(matrix) #Set inputNode inputs to selected matrix in training set
                regularNodes[0].requestInput()  # Request all their outputs and set them as inputs for this node
                regularNodes[1].requestInput()  # Request all their outputs and set them as inputs for this node
                vector = normalize(regularNodes[0].getOutput(), regularNodes[1].getOutput()) #Get vector from both RegularNodes outcomes
                # print(vector)
                if (counter < 2): #If selected matrix in trainingset is circle
                    # print("Distance: " + str(calcDixstance(vector, circle)))
                    distance += calcDistance(vector, circle) #Calculate distance between vector outcome and expected circle vector (1,0)
                else: #If selected matrix in trainingset is cross
                    # print("Distance: " + str(calcDistance(vector, cross)))
                    distance += calcDistance(vector, cross)  #Calculate distance between vector outcome and expected cross vector (0, 1)
                counter += 1
            avgDistance = distance/4 #Devide total distances by 4 to get average distance
            if(avgDistance < bestDistance): #If this distance is closer (better) then the current best distance, use this one instead
                bestDistance = avgDistance
                bestIndex = i
            # print("Total distance: " + str(distance) + " | AVG: " + str(avgDistance))
            # debugWeights()
            # print("--------------------------------------------")
        edges[bestIndex].weight += increment
        # print("Best distance: " + str(bestDistance) + " | Best index: " + str(bestIndex))
        # debugWeights()
    edges[len(edges) - 1].weight -= increment #Reset last weight after loop
    debugWeights() #Debug the edge weights

    #Test with a broken circle
    brokenCircle = [1,1,0,1,0,1,1,1,1]
    setInputs(brokenCircle)
    regularNodes[0].requestInput()  # Request all their outputs and set them as inputs for regular node (0)
    regularNodes[1].requestInput()  # Request all their outputs and set them as inputs for regular node (1)
    vector = normalize(regularNodes[0].getOutput(), regularNodes[1].getOutput()) #Get vector from outputs of regular node
    print(vector)

if __name__ == "__main__":
    main()


