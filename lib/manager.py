from random import random, randint
from math import sin, cos, radians, degrees, pi as PI
import pygame
import pygame.gfxdraw as gfxdraw
from pygame import Surface, Color, Rect
from lib.math2 import flipy, clamp
from lib.net import Network, TYPE, ACTIVATION
from lib.config import *
from lib.gui import GUI

class Manager:

    def __init__(self, screen: Surface):
        pygame.font.init()
        self.fira_code = pygame.font.Font("res/fonts/fira.ttf", 12)
        self.creature_font = pygame.font.Font("res/fonts/fira.ttf", 10)
        self.norm_font = pygame.font.Font("res/fonts/fira.ttf", 12)
        self.titl_font = pygame.font.Font("res/fonts/fira.ttf", 18)
        self.subtitl_font = pygame.font.Font("res/fonts/fira.ttf", 16)
        self.small_font = pygame.font.Font("res/fonts/fira.ttf", 8)
        self.titl_font.set_bold(True)
        self.subtitl_font.set_bold(True)
        self.screen = screen
        self.gui = GUI(owner=self, view=(1200, 700))

    def user_event(self, event):
        self.gui.process_event(event)

    def update_gui(self, dt: float):
        self.gui.update(dt)

    def draw_gui(self, screen: Surface):
        self.gui.draw_ui(screen)

    def new_sim(self, project_name: str):
       pass 
    
    def draw_net(self, network: Network):
        if network:
            h_space = 40
            v_space = 10
            nodes_to_draw = []
            dists = {}
            max_nodes_num = 0
            max_layer_size = 0
            for layer in network.layers:
                node_num = len(network.layers[layer].nodes)
                if max_nodes_num < node_num:
                    max_nodes_num = node_num
            max_layer_size = max_nodes_num * v_space
            l = 0
            base_line = []

            inp_desc = ["sid", 
                        "lpd", "lps", "lcd", "lcs", "lca", "lmd", "lms", "lob",
                        "fpd", "fps", "fcd", "fcs", "fca", "fmd", "fms", "fob",
                        "rpd", "rps", "rcd", "rcs", "rca", "rmd", "rms", "rob",
                        "eng", "atk", "hrt", "hid", "enmy", "good", "run", "stam",
                         "collid", "x", "y"]
            out_desc = ["mov", "turn", "run", "hid", "atk", "eat"]

            input_keys = network.GetNodeKeyList([TYPE.INPUT])
            output_keys = network.GetNodeKeyList([TYPE.OUTPUT])
            for layer in network.layers:
                last_layer = False
                if network.layers[layer].type == TYPE.OUTPUT:
                    last_layer = True
                node_num = len(network.layers[layer].nodes)
                if node_num > 0:
                    dist_nn = round(max_layer_size/(node_num))
                else:
                    dist_nn = max_layer_size
                dists[layer] = dist_nn
                n = 0
                desc_idx = 0
                base_line.append(round((575 + max_nodes_num * v_space)/2))
                for node_key in network.layers[layer].nodes:
                    node = network.nodes[node_key]
                    if node.recombined:
                        node_color = Color("#8f8f8f")
                    else:
                        if node.activation == ACTIVATION.TANH:
                            node_color = Color("#7CFC00")
                        elif node.activation == ACTIVATION.SIGMOID:
                            node_color = Color("#00f5ed")
                        elif node.activation == ACTIVATION.RELU:
                            node_color = Color("#f50000")
                        elif node.activation == ACTIVATION.LEAKY_RELU:
                            node_color = Color("#ab02e3")
                        elif node.activation == ACTIVATION.BINARY:
                            node_color = Color("#f0f000")
                        elif node.activation == ACTIVATION.REV_BINARY:
                            node_color = Color("#ffaa00")
                        elif node.activation == ACTIVATION.WIDE_BINARY:
                            node_color = Color("#1a8cff")
                        elif node.activation == ACTIVATION.LINEAR:
                            node_color = Color("#f05800")
                    for link_key in node.to_links:
                        link = network.links[link_key]
                        from_node_key = link.from_node
                        (l0, n0) = network.FindNode(from_node_key)
                        g = 0
                        if link.weight >= 0:
                            g = 0
                            r = round(255*link.weight)
                            b = 255 - r
                            if link.recombined:
                                g = 255
                        else:
                            b = abs(round(255*link.weight))
                            r = 255 - b
                            if link.recombined:
                                g = 255
                        link_color = Color(r, g, b)
                        node_num0 = len(network.layers[l0].nodes)
                        pygame.draw.aaline(self.screen, link_color, (40 + l0 * h_space, SCREEN[1] - base_line[l0] + (dists[l0] * n0) + round(dists[l0]/2)), (40 + l * h_space, SCREEN[1] - base_line[l] + (dist_nn * n) + round(dist_nn/2)-1))
                        pygame.draw.aaline(self.screen, link_color, (40 + l0 * h_space, SCREEN[1] - base_line[l0] + (dists[l0] * n0) + round(dists[l0]/2)), (40 + l * h_space, SCREEN[1] - base_line[l] + (dist_nn * n) + round(dist_nn/2)))
                        pygame.draw.aaline(self.screen, link_color, (40 + l0 * h_space, SCREEN[1] - base_line[l0] + (dists[l0] * n0) + round(dists[l0]/2)), (40 + l * h_space, SCREEN[1] - base_line[l] + (dist_nn * n) + round(dist_nn/2)+1))
                    #if last_layer:  #TODO
                    #    desc = out_desc[desc_idx]
                    #    desc_idx += 1
                    desc = ''
                    nodes_to_draw.append((node_color, l, n, node.recurrent, dist_nn, desc))
                    n += 1
                l += 1

            for c, l, n, r, d, desc in nodes_to_draw:
                gfxdraw.filled_circle(self.screen, 40 + l * h_space, SCREEN[1] - base_line[l] + d*n + round(d/2), 3, c)
                gfxdraw.aacircle(self.screen, 40 + l * h_space, SCREEN[1] - base_line[l] + d + round(d/2), 3, c)
                if r:
                    gfxdraw.aacircle(self.screen, 40 + l * h_space, SCREEN[1] - base_line[l] + d*n + round(d/2), 5, c)
                #if l == 0:
                #    self.AddText(f'{n}', 20 + l * (h_space+10), SCREEN[1] - base_line[l] + d*n + round(d/2) - 5, Color('white'), small=True)
                #if desc:
                #    self.AddText(desc, 40 + l * (h_space+10), SCREEN[1] - base_line[l] + d*n + round(d/2), Color('#069ab8'), small=True)