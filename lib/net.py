from enum import Enum, IntEnum
from random import random, randint, choice, gauss
from lib.math2 import sigmoid, tanh, relu, leaky_relu, binary, rev_binary, wide_binary, linear,clamp
from copy import deepcopy, copy
import json
import numpy as np
from lib.config import cfg

class TYPE(IntEnum):

    INPUT = 0
    HIDDEN = 1
    OUTPUT = 2
    MEMORY = 3

class NODE_TYPE(IntEnum):
    FWD = 0
    SHORT = 1
    LONG = 2

class ACTIVATION(IntEnum):

    TANH = 0
    SIGMOID = 1
    BINARY = 2
    RELU = 3
    LEAKY_RELU = 4
    REV_BINARY = 5
    WIDE_BINARY = 6
    LINEAR = 7

class Node():

    def __init__(self, node_type, activation=ACTIVATION.TANH, bias = 0, recurrent=False, mem_weight=None):
        
        self.bias = bias
        self.value = 0
        self.to_links = []
        self.from_links = []
        self.type = node_type
        self.recurrent = recurrent
        if self.recurrent:
            self.mem = 0
            if mem_weight:
                self.mem_weight = mem_weight
            else:
                self.mem_weight = self.RandomNormal()
        else:
            self.mem = None
            self.mem_weight = None
        self.activation = ACTIVATION.TANH
        self.recombined = False
        if activation == ACTIVATION.TANH:
            self.activation = ACTIVATION.TANH
            self.func = tanh
        elif activation == ACTIVATION.SIGMOID:
            self.activation = ACTIVATION.SIGMOID
            self.func = sigmoid
        elif activation == ACTIVATION.RELU:
            self.activation = ACTIVATION.RELU
            self.func = relu
        elif activation == ACTIVATION.BINARY:
            self.activation = ACTIVATION.BINARY
            self.func = binary
        elif activation == ACTIVATION.REV_BINARY:
            self.activation = ACTIVATION.REV_BINARY
            self.func = rev_binary
        elif activation == ACTIVATION.WIDE_BINARY:
            self.activation = ACTIVATION.WIDE_BINARY
            self.func = wide_binary
        elif activation == ACTIVATION.LINEAR:
            self.activation = ACTIVATION.LINEAR
            self.func = linear

    def AddToLink(self, link_key):
        self.to_links.append(link_key)

    def AddFromLink(self, link_key):
        self.from_links.append(link_key)

    def RandomBias(self):
        self.bias = self.RandomNormal()

    def RandomMem(self):
        if self.recurrent:
            self.mem_weight = self.RandomNormal()
            
    def RandomNormal(self) -> float:
        n = clamp(gauss(0, 0.5), -1, 1)
        return n 

    def ToJSON(self):
        node = {}
        node['type'] = self.type
        node['recurrent'] = str(int(self.recurrent))
        node['mem_weight'] = self.mem_weight
        node['bias'] = self.bias
        node['from_links'] = json.dumps(self.from_links)
        node['to_links'] = json.dumps(self.to_links)
        node['activation'] = self.activation
        return node
    
class Link():

    def __init__(self, from_node, to_node, weight):
        self.from_node = from_node
        self.to_node = to_node
        self.weight = weight
        self.recombined = False

    def RandomWeight(self):
        self.weight = clamp(gauss(0, 0.5), -1, 1)

    def ToJSON(self):
        link = {}
        link['weight'] = self.weight
        link['from_node'] = self.from_node
        link['to_node'] = self.to_node
        return link

class Layer():

    def __init__(self, layer_type):
        self.type = layer_type
        self.nodes = []

    def AddNode(self, node_key):
        self.nodes.append(node_key)

    def ToJSON(self):
        layer = {}
        layer['type'] = self.type
        layer['nodes'] = json.dumps(self.nodes)
        return layer

class Network():
    """Neural Network created for Genetics Algorithms"""

    MUT_BIAS        =   0.06 * cfg.MUTATIONS
    MUT_WEIGHT      =   0.06 * cfg.MUTATIONS
    MUT_DEL_LINK    =   0.02 * cfg.MUTATIONS
    MUT_ADD_LINK    =   0.02 * cfg.MUTATIONS
    MUT_DEL_NODE    =   0.02 * cfg.MUTATIONS
    MUT_ADD_NODE    =   0.02 * cfg.MUTATIONS
    MUT_NODE_TYPE   =   0.04 * cfg.MUTATIONS
    MUT_MEM         =   0.04 * cfg.MUTATIONS

    ADD_NODE_NUM = 0
    DEL_NODE_NUM = 0

    def __init__(self):
        self.node_num = 0
        self.layer_num = 0
        self.link_num = 0
        self.layers = dict()
        self.nodes = dict()
        self.links = dict()
        self.log = []

    def BuildFromGenome(self, genome):
        self.node_num = genome.node_num
        self.layer_num = genome.layer_num
        self.link_num = genome.link_num
        self.layers = genome.layers
        self.nodes = genome.nodes
        self.links = genome.links

    def BuildRandom(self, node_list=[83, 0, 0, 0, 0, 0, 5], link_rate=0.5):
        """Method for setup new neural network based on node_list and link_rate parameters. This method should be run just after object creation."""
        for lay1 in range(len(node_list)):
            if lay1 == 0:
                layer_type = TYPE.INPUT
                self.input_layer_key = lay1
            elif lay1 == len(node_list)-1:
                layer_type = TYPE.OUTPUT
                self.output_layer_key = lay1
            else:
                layer_type = TYPE.HIDDEN

            layer_key = self.AddNewLayer(layer_type)
            
            for nod1 in range(node_list[lay1]):
                node_key = self.AddNewNode(lay1)
                for lay0 in range(lay1):
                    for nod0 in range(len(self.layers[lay0].nodes)):
                        if random() < link_rate:
                            from_node_key = self.layers[lay0].nodes[nod0]
                            self.AddNewLink(from_node_key, node_key)   

    def RandomWeight(self):
        """Function returns randomly generated float value from -1.0 to 1.0"""
        return clamp(gauss(0, 0.5), -1, 1)

    def NextLayerKey(self):
        """Layers number counter. It returns key for new layer and increases total layers count in network"""
        temp_num = self.layer_num
        self.layer_num += 1
        return temp_num

    def NextNodeKey(self):
        """Nodes number counter. It returns key for new Node and increases total Nodes count in network"""
        temp_num = self.node_num
        self.node_num += 1
        return temp_num

    def NextLinkKey(self):
        """Links number counter. It returns key for new link and increases total links count in network"""
        temp_num = self.link_num
        self.link_num += 1
        return temp_num

    def GetNodeKeyList(self, node_types=[TYPE.HIDDEN, TYPE.OUTPUT]):
        selected = []
        for n in self.nodes:
            if self.nodes[n].type in node_types:
                selected.append(n)
        return selected

    def GetLayerKeyList(self, layer_types=[TYPE.HIDDEN]):
        selected = []
        for l in self.layers:
            if self.layers[l].type in layer_types:
                selected.append(l)
        return selected

    def NewSignature(self, length: int) -> int:
        sign = 0
        for i in range(length):
            r = randint(0, 9)
            if i == length-1 and r == 0:
                r += 1
            sign += r * 10**i
        return sign

    def ConnectionExist(self, node1key, node2key, both_dirs=False):
        for l1 in self.nodes[node1key].from_links:
            if self.links[l1].to_node == node2key:
                return True
        if both_dirs:
            for l2 in self.nodes[node2key].from_links:
                if self.links[l2].to_node == node1key:
                    return True
        return False

    def AddNewLayer(self, layer_type):
        layer = Layer(layer_type)
        layer_key = self.NextLayerKey()
        self.layers[layer_key] = layer
        if layer_type == TYPE.INPUT:
            self.input_layer_key = layer_key
        elif layer_type == TYPE.OUTPUT:
            self.output_layer_key = layer_key
        return layer_key

    def AddNewNode(self, layer_key, recurrent=False):
        # !exception
        node = Node(node_type=self.layers[layer_key].type, activation=ACTIVATION.TANH, bias=self.RandomWeight(), recurrent=recurrent)
        node_key = self.NewSignature(4)
        while node_key in self.nodes:
            node_key = self.NewSignature(4)
        self.nodes[node_key] = node
        self.layers[layer_key].AddNode(node_key)
        return node_key

    def AddNewLink(self, from_node, to_node):
        link = Link(from_node, to_node, self.RandomWeight())
        link_key = self.NewSignature(4)
        while link_key in self.links:
            link_key = self.NewSignature(4)
        self.links[link_key] = link
        self.nodes[to_node].to_links.append(link_key)
        self.nodes[from_node].from_links.append(link_key)
        return link_key

    def AddThisLink(self, link_key, link):
        if link.from_node in self.nodes and link.to_node in self.nodes:
            link = deepcopy(link)
            if link_key in self.links:
                self.DeleteLink(link_key)
            self.links[link_key] = link
            self.log.append(f"ADD LINK: {link_key}")
            if not link_key in self.nodes[link.to_node].to_links:
                self.nodes[link.to_node].to_links.append(link_key)
            if not link_key in self.nodes[link.from_node].from_links:
                self.nodes[link.from_node].from_links.append(link_key)
            return True
        else:
            return False

    def AddThisNode(self, layer_key, node_key, node):
        if not node_key in self.nodes:
            node = deepcopy(node)
            self.nodes[node_key] = node
            self.layers[layer_key].AddNode(node_key)
            self.log.append(f"ADD NODE: {node_key}")
            return True
        else:
            return False

    def DeleteLink(self, link_key):
        if link_key in self.links:
            node_key1 = self.links[link_key].to_node
            node_key0 = self.links[link_key].from_node
            self.nodes[node_key1].to_links.remove(link_key)
            self.nodes[node_key0].from_links.remove(link_key)
            self.links.pop(link_key)
            self.log.append(f"DEL LINK: {link_key}")
            return True
        else:
            return False

    def DeleteNode(self, node_key):
        if node_key in self.nodes:
            links_to_kill = []
            for from_link_key in self.nodes[node_key].from_links:
                links_to_kill.append(from_link_key)
            for to_link_key in self.nodes[node_key].to_links:
                links_to_kill.append(to_link_key)
            for link_key in links_to_kill:
                self.DeleteLink(link_key)
            links_to_kill.clear()
            (layer_key, node_index) = self.FindNode(node_key)
            self.layers[layer_key].nodes.remove(node_key)
            self.nodes.pop(node_key)
            self.log.append(f"DEL NODE: {node_key}")
            return True
        else:
            return False

    def Calc(self, inputs):
        """Main calculation function. It gets input values, provide serial calculations and return output values"""
        inp_count = len(inputs)
        if inp_count == len(self.layers[0].nodes):
            for i in range(inp_count):
                in_node_key = self.layers[0].nodes[i]
                if self.nodes[in_node_key].recurrent:
                    mem = self.nodes[in_node_key].mem
                    mem_weight = self.nodes[in_node_key].mem_weight
                    self.nodes[in_node_key].value = (inputs[i] + mem) / 2
                    self.nodes[in_node_key].mem = self.nodes[in_node_key].value * mem_weight
                else:
                    self.nodes[in_node_key].value = inputs[i]
        for lay1 in range(1, len(self.layers)):
            for nod1 in range(len(self.layers[lay1].nodes)):
                dot = 0
                node_key = self.layers[lay1].nodes[nod1]
                bias = self.nodes[node_key].bias
                if self.nodes[node_key].activation == ACTIVATION.TANH:
                    func = tanh
                elif self.nodes[node_key].activation == ACTIVATION.SIGMOID:
                    func = sigmoid
                elif self.nodes[node_key].activation == ACTIVATION.RELU:
                    func = relu
                elif self.nodes[node_key].activation == ACTIVATION.LEAKY_RELU:
                    func = leaky_relu
                elif self.nodes[node_key].activation == ACTIVATION.BINARY:
                    func = binary
                elif self.nodes[node_key].activation == ACTIVATION.REV_BINARY:
                    func = rev_binary
                elif self.nodes[node_key].activation == ACTIVATION.WIDE_BINARY:
                    func = wide_binary
                elif self.nodes[node_key].activation == ACTIVATION.LINEAR:
                    func = linear

                for lin1 in range(len(self.nodes[node_key].to_links)):
                    
                    link_key = self.nodes[node_key].to_links[lin1]
                    from_node_key = self.links[link_key].from_node
                    v = self.nodes[from_node_key].value
                    w = self.links[link_key].weight
                    dot = dot + (v * w)

                dot = dot + bias

                recurrent = self.nodes[node_key].recurrent
                if recurrent:
                    mem = self.nodes[node_key].mem
                    mem_weight = self.nodes[node_key].mem_weight
                    dot = dot + mem
                    dot = func(dot) #* experimental activation
                    #dot = tanh(dot) #! new activation function test
                    #dot = math.tanh(dot)
                    self.nodes[node_key].mem = dot * mem_weight
                else:
                    dot = func(dot) #* experimental activation
                    #dot = tanh(dot) #! new activation function test
                    #dot = math.tanh(dot) 
                    #dot = sigmoid(dot) #? new alternative activation function
                
                self.nodes[node_key].value = dot


        out_layer = len(self.layers) - 1
        output = []
        for out in range(len(self.layers[out_layer].nodes)):
            
            out_node_key = self.layers[out_layer].nodes[out]
            output.append(self.nodes[out_node_key].value)

        return output

    def MutateBias(self, dt=1):

        for n in self.nodes:
            if (random()) < self.MUT_BIAS+self.node_index*self.mutations_rate:
                self.nodes[n].RandomBias()
            if self.nodes[n].recurrent:
                if (random()) < self.MUT_MEM+self.node_index*self.mutations_rate:
                    self.nodes[n].RandomMem()

    def MutateLinks(self, dt=1):

        links_to_kill = []
        links_to_add = []
        added = 0; deleted = 0

        for l in self.links:
            if (random()) < self.MUT_DEL_LINK+self.link_index*self.mutations_rate:
                links_to_kill.append(l)
                deleted += 1

            if (random()) < self.MUT_ADD_LINK+self.link_index*self.mutations_rate:
                link_added = False
                while not link_added:
                    n1 = choice(list(self.nodes.keys()))
                    n2 = choice(list(self.nodes.keys()))
                    if n1 != n2:
                        (l1, i1) = self.FindNode(n1)
                        (l2, i2) = self.FindNode(n2)
                        if l1 != l2:
                            if l1 < l2:
                                if not self.ConnectionExist(n1, n2, both_dirs=False):
                                    links_to_add.append((n1, n2))
                                    added += 1
                                    link_added = True
                            elif l2 < l1:
                                if not self.ConnectionExist(n2, n1, both_dirs=False):
                                    links_to_add.append((n2, n1))
                                    link_added = True
                                    added += 1
        for l in links_to_kill:
            self.DeleteLink(l)
        links_to_kill.clear()
        for (node0, node1) in links_to_add:
            self.AddNewLink(node0, node1)
        links_to_add.clear()
        return (added, deleted)
    
    def MutateWeights(self, dt=1):
        for l in self.links:
            if (random()) < self.MUT_WEIGHT+self.link_index*self.mutations_rate:
                self.links[l].RandomWeight()

    def MutateNodes(self, dt=1):
        nodes_to_kill = []
        nodes_to_add = []
        links_to_kill = []
        hidden_list = []
        added = 0; deleted = 0

        hidden_list = self.GetLayerKeyList([TYPE.HIDDEN])
        input_nodes = self.GetNodeKeyList([TYPE.INPUT])
        output_nodes = self.GetNodeKeyList([TYPE.OUTPUT])
        hidden_nodes = self.GetNodeKeyList([TYPE.HIDDEN])
        
        for n in self.nodes:
            if (random()) < self.MUT_DEL_NODE+self.node_index*self.mutations_rate:
                if len(hidden_nodes) > 0:
                    del_node = choice(hidden_nodes)
                    if not del_node in nodes_to_kill:
                        for l0 in self.nodes[del_node].from_links:
                            links_to_kill.append(l0)
                        for l1 in self.nodes[del_node].to_links:
                            links_to_kill.append(l1)
                        nodes_to_kill.append(del_node)
                        deleted += 1
            
            if hidden_list != []:
                if (random()) < self.MUT_ADD_NODE+self.node_index*self.mutations_rate:
                    layer_key = choice(hidden_list)
                    n1key = choice(input_nodes)
                    n2key = choice(output_nodes)
                    nodes_to_add.append((layer_key, n1key, n2key))
                    added += 1

        for l in links_to_kill:
            self.DeleteLink(l)
        
        for n in nodes_to_kill:
            self.DeleteNode(n)

        for layer, n_from, n_to in nodes_to_add:
            node_key = self.AddNewNode(layer)
            self.AddNewLink(n_from, node_key)
            self.AddNewLink(node_key, n_to)
        
        return (added, deleted)
    
    def MutateNodeType(self, dt=1):
        for n in self.nodes:
            if (random()) < self.MUT_NODE_TYPE+self.node_index*self.mutations_rate:
                #n_type = choice(['tanh', 'sigmoid', 'binary', 'rev_binary', 'wide_binary', 'relu', 'leaky_relu', 'linear', 'memory'])
                n_type = choice(['tanh', 'sigmoid', 'binary', 'relu', 'leaky_relu', 'memory'])
                if n_type == 'memory':
                    self.nodes[n].recurrent = not self.nodes[n].recurrent
                    if self.nodes[n].recurrent:
                        self.nodes[n].mem = 0
                        self.nodes[n].mem_weight = self.nodes[n].RandomNormal()
                    else:
                        self.nodes[n].mem = None
                        self.nodes[n].mem_weight = None
                elif n_type == 'tanh':
                    self.nodes[n].activation = ACTIVATION.TANH
                elif n_type == 'sigmoid':
                    self.nodes[n].activation = ACTIVATION.SIGMOID
                elif n_type == 'relu':
                    self.nodes[n].activation = ACTIVATION.RELU
                elif n_type == 'leaky_relu':
                    self.nodes[n].activation = ACTIVATION.LEAKY_RELU
                elif n_type == 'binary':
                    self.nodes[n].activation = ACTIVATION.BINARY
                elif n_type == 'rev_binary':
                    self.nodes[n].activation = ACTIVATION.REV_BINARY
                elif n_type == 'wide_binary':
                    self.nodes[n].activation = ACTIVATION.WIDE_BINARY
                elif n_type == 'linear':
                    self.nodes[n].activation = ACTIVATION.LINEAR

    def Mutate(self, mutations_rate: int=5, dt=1):
        node_num = len(self.nodes)-(len(self.GetNodeKeyList([TYPE.INPUT]))+len(self.GetNodeKeyList([TYPE.OUTPUT])))
        link_num = len(self.links)
        if node_num != 0:
            self.node_index = 0.05/node_num
        else:
            self.node_index = 0.05
        if link_num != 0:
            self.link_index = 0.05/link_num
        else:
            self.link_index = 0.05
        self.mutations_rate = mutations_rate/10
        self.MutateBias(dt)
        added_l, deleted_l = self.MutateLinks(dt)
        self.MutateWeights(dt)
        added_n, deleted_n = self.MutateNodes(dt)
        self.MutateNodeType(dt)

    def Replicate(self):

        clone = Network()
        clone.node_num = self.node_num
        clone.layer_num = self.layer_num
        clone.link_num = self.link_num
        clone.layers = deepcopy(self.layers)
        clone.nodes = deepcopy(self.nodes)
        clone.links = deepcopy(self.links)
        for node_key in clone.nodes:
            clone.nodes[node_key].recombined = False
        for link_key in clone.links:
            clone.links[link_key].recombined = False
        clone.log = deepcopy(self.log)
        clone.log.append("___CLONE___")
        return clone
       
    def FindNode(self, node_key):

        for layer_key in self.layers:
            n = 0
            for node_key2 in self.layers[layer_key].nodes:
                if node_key == node_key2:
                    return (layer_key, n)
                n += 1

    def GetNodesNum(self):
        nodes_num = 0
        for l in self.layers:
            if self.layers[l].type == TYPE.HIDDEN:
                nodes_num += len(self.layers[l].nodes)
        return nodes_num

    def GetLinksNum(self):
    
        return len(self.links)

    def CleanRecombinated(self):

        for node_key in self.nodes:
            self.nodes[node_key].recombined = False
        for link_key in self.links:
            self.links[link_key].recombined = False

    def ToJSON(self):

        net = {}
        net['layer_num'] = self.layer_num
        net['node_num'] = self.node_num
        net['link_num'] = self.link_num
        net['layers'] = {}
        net['nodes'] = {}
        net['links'] = {}

        for layer_key in self.layers:
            net['layers'][layer_key] = self.layers[layer_key].ToJSON()

        for node_key in self.nodes:
            net['nodes'][node_key] = self.nodes[node_key].ToJSON()

        for link_key in self.links:
            net['links'][link_key] = self.links[link_key].ToJSON()
        
        return net

    def FromJSON(self, neuro):

        self.layer_num = neuro['layer_num']
        self.node_num = neuro['node_num']
        self.link_num = neuro['link_num']

        layers0 = neuro['layers']
        self.layers.clear()
        for l in layers0:
            layer_key = int(l)
            layer = Layer(layers0[l]['type'])
            self.layers[layer_key] = layer
            self.layers[layer_key].nodes = json.loads(layers0[l]['nodes'])

        nodes0 = neuro['nodes']
        self.nodes.clear()
        for n in nodes0:
            node_key = int(n)
            node = Node(nodes0[n]['type'], nodes0[n]['activation'], nodes0[n]['bias'], bool(int(nodes0[n]['recurrent'])), nodes0[n]['mem_weight'])
            self.nodes[node_key] = node
            self.nodes[node_key].from_links = json.loads(nodes0[n]['from_links'])
            self.nodes[node_key].to_links = json.loads(nodes0[n]['to_links'])
            #self.nodes[node_key].activation = json.loads(nodes0[n]['activation'])
                
        links0 = neuro['links']
        self.links.clear()
        for li in links0:
            link_key = int(li)
            link = Link(links0[li]['from_node'], links0[li]['to_node'], links0[li]['weight'])
            self.links[link_key] = link
