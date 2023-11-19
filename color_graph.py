import copy
import sys

def read_file():
    if len(sys.argv) != 2:
        print("Error in the number of arguments. Usage: python colorGraph3.py fileName.txt")
        sys.exit()
    inputFile = open(sys.argv[1], "r")
    content = inputFile.readlines()
    inputFile.close()

    withoutNewlines = list(filter(lambda x: x != '\n', content))
    withoutNewlines = list(map(lambda x: x.rstrip('\n'), withoutNewlines))

    for i in range(0, len(withoutNewlines)):
        withoutNewlines[i] = withoutNewlines[i].lower()

    clausesStringList = []
    for line in withoutNewlines:
        if line.find("variaveis:") != -1:
            index = line.find(":")
            stringVariables = line[index + 1:]
            # Remove leading spaces if any
            while stringVariables[0] == ' ':
                stringVariables = stringVariables[1:]
        elif line.find("clausulas") == -1:
            clausesStringList.append(line)

    variable = ""
    variablesList = []
    for char in stringVariables:
        if char == " " and variable != "":
            variablesList.append(variable)
            variable = ""
        else:
            variable += char

    variablesList.append(variable)

    for i in range(0, len(clausesStringList)):
        while clausesStringList[i].find("or") != -1:
            clausesStringList[i] = clausesStringList[i].replace("or", "")

    literalsList = []
    clausesList = []
    for string in clausesStringList:
        literal = ""
        for c in string:
            if c == " " and literal != "":
                literalsList.append(literal)
                literal = ""
            elif c != " ":
                literal += c
        literalsList.append(literal)
        clausesList.append(Clausula(literalsList[0], literalsList[1], literalsList[2]))
        literalsList = []

    # Display results
    print("Variables:")
    print(variablesList)
    print("\nClauses:")
    for clause in clausesList:
        print(clause.l1 + " " + clause.l2 + " " + clause.l3)
    print()
    return [variablesList, clausesList]

# Representa um nó do grafo
class Node:
    def __init__(self, name, connected_nodes, color):
        self.name = name
        self.connected_nodes = list(connected_nodes)
        self.connect_node(self.connected_nodes)
        self.color = color

    def __str__(self):
        msg = "Node: " + self.name + ", color: " + self.color + ", connected nodes: ["
        for node in self.connected_nodes:
            msg = msg + node.name + ", "
        if len(self.connected_nodes) > 0:
            msg = msg[:-1]
            msg = msg[:-1]
        msg = msg + "]"
        return msg

    def __repr__(self):
        return str(self)

    def connect_node(self, nodes):
        for node in nodes:
            if node not in self.connected_nodes:
                self.connected_nodes.append(node)
            if self not in node.connected_nodes:
                node.connected_nodes.append(self)


# Clausula 3 sat
class Clausula:
    def __init__(self, l1, l2, l3):
        self.l1 = l1
        self.l2 = l2
        self.l3 = l3

    def __str__(self):
        return self.l1 + " OR " + self.l2 + " OR " + self.l3

    def __repr__(self):
        return str(self)


class Graph:
    def __init__(self, variables, clauses):
        self.base_nodes = []
        self.variable_nodes = []
        self.gate_nodes = []
        self.variables = list(variables)
        self.clauses = list(clauses)

    def __str__(self):
        return "Graph: \n" + str(self.base_nodes + self.variable_nodes + self.gate_nodes)

    def find_node(self, name):
        return next(x for x in self.variable_nodes if x.name == name)

    def initialize_graph(self):
        base = Node("Base", [], "B")
        true_node = Node("True", [base], "V")
        false_node = Node("False", [true_node, base], "F")
        self.base_nodes = [base, true_node, false_node]

    def create_variable_nodes(self):
        for variable in self.variables:
            var_node = Node(variable, [self.base_nodes[0]], "")
            neg_var_node = Node("¬" + variable, [self.base_nodes[0], var_node], "")
            self.variable_nodes = self.variable_nodes + [var_node, neg_var_node]

    def create_or_gate(self, n1, n2, i, j):
        n11 = Node("C" + str(i) + str(j), [n1], "")
        n21 = Node("C" + str(i) + str(j + 1), [n11, n2], "")
        n3 = Node("C" + str(i) + str(j + 2), [n11, n21], "")
        self.gate_nodes = self.gate_nodes + [n11, n21, n3]
        return n3

    def create_gate_nodes(self):

        for i in range(0, len(self.clauses)):
            clause = self.clauses[i]
            n1 = self.find_node(clause.l1)
            n2 = self.find_node(clause.l2)
            n3 = self.find_node(clause.l3)
            res1 = self.create_or_gate(n1, n2, i + 1, 1)
            res2 = self.create_or_gate(res1, n3, i + 1, 4)
            res2.connect_node([self.base_nodes[0], self.base_nodes[2]])

    ###################### Etapa 1 ###############################
    # Aqui é feito o mapeamento da entrada. É inicializada a estrutura base do grafo, com T, F e B
    # Após isso, a partir das clausulas, são criadas as variáveis e os gadgets OR que são utilizados na coloração do grafo com as variaveis os vértices auxiliares e a base do grafo
    def create_graph(self):
        self.initialize_graph()
        self.create_variable_nodes()
        self.create_gate_nodes()

    def available_colors(self, node):
        colors = ["B", "V", "F"]
        for neighbor in node.connected_nodes:
            try:
                colors.remove(neighbor.color)
            except ValueError:
                pass
        return colors

    def color_3_colors_algorithm(self):
        nodes = []
        for node in (self.gate_nodes + self.variable_nodes):
            if node.color == "":
                nodes.append(node)
        return self.color_graph(nodes)
    
    ###################### Etapa 2 ###############################
    # Aqui é feita a resolução do problema de coloração do grafo juntamente com a verificação do problema, se existe solução. 
    # É recursivamente testado cada uma das possibilidades de cores para as variaveis e auxiliares do gadget
    def color_graph(self, nodes):
        if not nodes:
            return True
        node = nodes[0]
        colors = self.available_colors(node)
        if not colors:
            return False
        new_nodes = copy.copy(nodes)
        new_nodes.remove(node)
        for color in colors:
            node.color = color
            result = self.color_graph(new_nodes)
            if result:
                return True
        node.color = ""
        return False

    ##################### Etapa 3 ####################################
    # Mapeamento da coloração de grafos para 3 sat. Basta observar a cor das variáveis
    def to_sat3(self):
        is_solvable = self.color_3_colors_algorithm()
        msg = ""
        if is_solvable:
            msg = "SAT3 Resolution, truth values:"
            for i in range(0, len(self.variable_nodes), 2):
                msg = msg + "\n" + self.variable_nodes[i].name + " = " + self.variable_nodes[i].color
        else:
            msg = "Cannot solve SAT3/Color the graph with 3 colors."
        return msg

# Example usage
if __name__ == "__main__":
    variables, clauses = read_file()
    graph = Graph(variables, clauses)
    graph.create_graph()
    print(graph)
    print()
    result = graph.to_sat3()
    print(result)
