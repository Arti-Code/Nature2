import json
import os
from copy import copy, deepcopy
from shutil import rmtree

import pygame
import pygame.gfxdraw as gfxdraw
from pygame import Color, Rect, Surface
from pygame.font import Font

from lib.config import cfg
from lib.creature import Creature
from lib.gui import GUI
from lib.math2 import clamp
from lib.net import ACTIVATION, Link, Network, Node, MUTATIONS


def draw_net(network: Network, small_font: Font, norm_font: Font) -> Surface:
    text_list: list=[]
    back_box: Rect
    if not network:
        return None
    else:
        last_layer_idx: int=len(network.layers)-1
        h_space = cfg.GRAPH_H
        v_space = cfg.GRAPH_V
        nodes_to_draw = []
        dists = {}
        max_nodes_num = 0
        max_layer_size = 0
        for layer in network.layers:
            node_num = len(network.layers[layer].nodes)
            if max_nodes_num < node_num:
                max_nodes_num = node_num
        max_layer_size = max_nodes_num * v_space
        max_net_length = len(network.layers)*h_space
        l = 0
        base_line = []
        #black_box: Rect=None
        inp_desc = [
            'ENE', 'PLA', 'MEA',
            'ENG', 'HIT',
            'E-R', 'E-D', 
            'FAM', 'DNG',
            'P-R', 'P-D',
            'M-R', 'M-D',
            'R-R', 'R-D',
            'BOR'
        ]
        out_desc = [
            "MOV", "TUR",
            "EAT", "ATK",
            "HID", "HIT"
        ]

    for layer in network.layers:
        node_num = len(network.layers[layer].nodes)
        dist_nn: int
        if node_num > 0:
            dist_nn = round(max_layer_size/(node_num))
        else:
            dist_nn = max_layer_size
        dists[layer] = dist_nn
        n = 0
        base_line.append(round((cfg.NET_BASE + max_nodes_num * v_space)/2))
        back_box = Rect(4, cfg.SCREEN[1] - (max(base_line))-4, max_net_length+105, max_layer_size+6)

        net_surf: Surface = Surface((back_box.w, back_box.h))
        #net_surf = Surface.convert_alpha(net_surf)
        net_surf.fill(Color(0, 0, 0, 200))
        #gfxdraw.circle(net_surf, 100, 100, 50, Color(0,255,0))
        gfxdraw.aapolygon(net_surf, [back_box.topleft, back_box.topright, back_box.bottomright, back_box.bottomleft], Color(25, 100, 255, 150))
        pygame.draw.polygon(net_surf, Color(25, 100, 255, 150), [(back_box.left+1, back_box.top+1), (back_box.right-2, back_box.top+1), (back_box.right-2, back_box.bottom-2), (back_box.left+1, back_box.bottom-2)], 1)
        gfxdraw.filled_polygon(net_surf, [back_box.topleft, back_box.topright, back_box.bottomright, back_box.bottomleft], Color(0,0,255, 25))
        
        for node_key in network.layers[layer].nodes:
            node: Node = network.nodes[node_key]
            v = node.value
            if node.recurrent:
                node_color = Color("black")
            else:
                if node.activation == ACTIVATION.TANH:
                    node_color = Color("#55ff2f")
            for link_key in node.to_links:
                link: Link=network.links[link_key]
                from_node_key = link.from_node
                (l0, n0) = network.FindNode(from_node_key)
                g = 0
                a = abs(round(100*link.signal))+155
                if link.signal >= 0:
                    g = 0
                    r = 100+155*link.signal
                    b = 0
                    if link.recombined:
                        g = 255
                else:
                    b = 100+abs(155*link.signal)
                    r = 0
                    if link.recombined:
                        g = 255
                link_color = Color((r, g, b, a))
                w = a//50
                p0 = (70 + l0 * h_space, back_box.height - base_line[l0] + (dists[l0] * n0) + round(dists[l0]/2))
                p1 = (70 + l * h_space, back_box.height - base_line[l] + (dist_nn * n) + round(dist_nn/2))
                pygame.draw.line(net_surf, link_color, p0, p1, w)
            desc = ''
            nodes_to_draw.append((node_color, l, n, node.recurrent, dist_nn, desc, v))
            n += 1
        l += 1
        out = 0

    for c, l, n, r, d, desc, v in nodes_to_draw:
        v = clamp(v, -1.0, 1.0)
        rv=0; gv = 0; bv=0
        cv = int(6*abs(v))+2
        if v >= 0:
            gv = 255
        else:
            rv = 255
            gv = 150
            bv = 25
        v_color = Color(rv, gv, bv)
        v_color_alfa = Color(rv, gv, bv, 255)
        black_color = Color(255, 255, 255, 255)
        gfxdraw.aacircle(net_surf, 70 + l * h_space, back_box.height - base_line[l] + d*n + round(d/2), cv, v_color)
        gfxdraw.filled_circle(net_surf, 70 + l * h_space, back_box.height - base_line[l] + d*n + round(d/2), cv, v_color_alfa)
        if r:
            gfxdraw.filled_circle(net_surf, 70 + l * h_space, back_box.height - base_line[l] + d*n + round(d/2), int(cv/2), black_color)
            gfxdraw.aacircle(net_surf, 70 + l * h_space, back_box.height - base_line[l] + d*n + round(d/2), int(cv/2), c)
        if l == 0:
            val = network.nodes[network.layers[l].nodes[n]].value
            text = "{:<2}:{:2> .1f}".format(inp_desc[n], val)
            text_list.append(add_text(text, 12 + l * (h_space+10), back_box.height - base_line[l] + d*n + round(d/2) - 5, Color('white'), small_font))
        elif l == last_layer_idx:
            val = network.nodes[network.layers[l].nodes[n]].value
            text = "{:<}:{:< .1f}".format(out_desc[n], val)
            text_list.append(add_text(text, 80 + l * (h_space), back_box.height - base_line[l] + d*n + round(d/2) - 5, Color('white'), small_font))
        #else:
            #val = network.nodes[network.layers[l].nodes[n]].value
            #text = "{:^1.1f}".format(val)
            #self.add_text(text, 85 + l * (h_space), cfg.SCREEN[1] - base_line[l] + d*n + round(d/2) - 5, True, Color('white'))
        #net_surf.set_colorkey(Color(0,0,0))
        #net_surf.fill(Color(0, 0, 0))
    draw_texts(net_surf, text_list)
    text_list.clear()
    return net_surf

def add_text(text: str, x: int, y: int, color: Color, font: Font) -> tuple:
    txt_render = font.render(text, True, Color(color))
    txt_rect = txt_render.get_rect()
    txt_rect.left = x
    txt_rect.top = y
    return (txt_render, txt_rect)
    #surface.blit(txt_render, txt_rect)

def draw_texts(surface: Surface, text_list: list):
    for txt, rect in text_list:
        surface.blit(txt, rect)
