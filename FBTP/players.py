# coding=utf-8


class Player:

    def __init__(self, key):
        self.id = key  # player's ID
        self.connectedTo = {}  # the connection to other players --> {players' id: similarity}
        self.abilities = {}  # player's ability --> {ability ID: value}
        self.position = None  # position
        self.salary = 0  # players' salary

    def add_neighbor(self, nbr, weight=0):
        self.connectedTo[nbr] = weight

    def __str__(self):
        return str(self.id) + ' connectedTo : ' + str([x.id for x in self.connectedTo])

    def get_connection(self):  # get the neighbors
        return self.connectedTo.keys()

    def get_id(self):
        return self.id

    def get_abilities(self):
        return self.abilities

    def get_position(self):
        return self.position

    def get_salary(self):
        return self.salary

    def get_weight(self, nbr):  # get the weight of a neighbor
        return self.connectedTo[nbr]


class Goalkeeper:

    def __init__(self, g_id):
        self.id = g_id
        self.ability = []
        self.rating = 0
        self.salary = 0

    def get_id(self):
        return self.id

    def get_ability(self):
        return self.ability

    def get_rating(self):
        return self.rating

    def get_salary(self):
        return self.salary


class CutPlayer:
    """
    The player to be pruning
    """

    def __init__(self, key):
        self.id = key
        self.cut_pos = None  # Forward/Midfielder or Backward
        self.cut_position = ""  # position
        self.cut_salary = 0  # salary

    def get_id(self):
        return self.id

    def get_cut_pos(self):
        return self.cut_pos

    def get_cut_position(self):
        return self.cut_position

    def get_cut_salary(self):
        return self.cut_salary


class Graph:

    def __init__(self):
        self.vertexList = {}
        self.numVertices = 0

    def add_vertex(self, key):
        self.numVertices = self.numVertices + 1
        newVertex = Player(key)
        self.vertexList[key] = newVertex
        return newVertex

    def get_vertex(self, key):
        if key in self.vertexList:
            return self.vertexList[key]
        else:
            return None

    def __contains__(self, key):
        return key in self.vertexList

    def add_edge(self, f, t, cost=0):
        # if f and t both are not in the graph, add these two nodes
        if f not in self.vertexList:
            nv = self.add_vertex(f)

        if t not in self.vertexList:
            nv = self.add_vertex(t)

        self.vertexList[f].add_neighbor(self.vertexList[t], cost)

    def get_vertices(self):  # get all vertex
        return self.vertexList.keys()

    def __iter__(self):
        return iter(self.vertexList.values())