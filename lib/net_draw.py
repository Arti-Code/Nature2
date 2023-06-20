import json
import os
from copy import copy, deepcopy
from shutil import rmtree

import pygame
import pygame.gfxdraw as gfxdraw
from pygame import Color, Rect, Surface

from lib.config import cfg
from lib.creature import Creature
from lib.gui import GUI
from lib.math2 import clamp
from lib.net import ACTIVATION, Link, Network, Node, MUTATIONS



def draw_net(screen: Surface, owner: object, network: Network):
    if network:
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

        inp_desc = [
            'AGT', 'PLA', 'MEA',
            'ENG', 'HIT',
            'AGR', 'AGD', 
            'FAM', 'DNG',
            'PLR', 'PLD',
            'MER', 'MED',
            'ROR', 'ROD',
            '???'
        ]
        out_desc = [
            "MOV", "ROT",
            "EAT", "ATK",
            "HID", "SPK"
        ]

        for layer in network.layers:
            node_num = len(network.layers[layer].nodes)
            if node_num > 0:
                dist_nn = round(max_layer_size/(node_num))
            else:
                dist_nn = max_layer_size
            dists[layer] = dist_nn
            n = 0
            base_line.append(round((cfg.NET_BASE + max_nodes_num * v_space)/2))
            back_box = Rect(1, cfg.SCREEN[1] - (max(base_line))-4, max_net_length+110, max_layer_size+4)
            gfxdraw.aapolygon(screen, [back_box.topleft, back_box.topright, back_box.bottomright, back_box.bottomleft], Color(0, 255, 255, 75))
            #pygame.draw.polygon(screen, Color(0, 255, 255, 50), [(back_box.left+1, back_box.top+1), (back_box.right-2, back_box.top+1), (back_box.right-2, back_box.bottom-2), (back_box.left+1, back_box.bottom-2)], 1)
            gfxdraw.filled_polygon(screen, [back_box.topleft, back_box.topright, back_box.bottomright, back_box.bottomleft], Color(0,0,0, 75))
            for node_key in network.layers[layer].nodes:
                node: Node = network.nodes[node_key]
                added: bool=False; changed: bool=False
                if MUTATIONS.ADDED in node.mutations:
                    added = True
                elif MUTATIONS.CHANGED in node.mutations:
                    changed = True
                v = node.value
                mean = round(node.mean, 1)
                mem_size = node.memory_size
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
                    a = abs(round(200*link.signal))+55
                    link_color: Color
                    if MUTATIONS.ADDED in link.mutations:
                        link_color = Color(0, 255, 0, 255)
                    elif MUTATIONS.CHANGED in link.mutations:
                        link_color = Color(255, 255, 255, 255)
                    else:    
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
                    p0 = (55 + l0 * h_space, cfg.SCREEN[1] - base_line[l0] + (dists[l0] * n0) + round(dists[l0]/2))
                    p1 = (55 + l * h_space, cfg.SCREEN[1] - base_line[l] + (dist_nn * n) + round(dist_nn/2))
                    pygame.draw.line(screen, link_color, p0, p1, w)
                desc = ''
                nodes_to_draw.append((node_color, l, n, node.recurrent, dist_nn, desc, v, mean, mem_size, added, changed))
                n += 1
            l += 1
        
        out = 0
        
        for c, l, n, r, d, desc, v, mean, mem_size, added, changed in nodes_to_draw:
            v_color: Color
            v_color_alfa: Color

            if MUTATIONS.ADDED in link.mutations:
                v_color = Color(255, 255, 0, 255)
                v_color_alfa = Color(0, 255, 0, 50)
            elif MUTATIONS.CHANGED in link.mutations:
                v_color = Color(255, 255, 255, 255)
                v_color_alfa = Color(255, 255, 255, 50)
            else:
                v = clamp(v, -1.0, 1.0)
                rv=0; gv = 0; bv=0
                if v >= 0:
                    gv = 255
                else:
                    rv = 255
                    gv = 150
                    bv = 25
                v_color = Color(rv, gv, bv)
                v_color_alfa = Color(rv, gv, bv, 50)
            cv = int(6*abs(v))+2
            black_color = Color(255, 255, 255, 255)
            gfxdraw.aacircle(screen, 55 + l * h_space, cfg.SCREEN[1] - base_line[l] + d*n + round(d/2), cv, v_color)
            gfxdraw.filled_circle(screen, 55 + l * h_space, cfg.SCREEN[1] - base_line[l] + d*n + round(d/2), cv, v_color_alfa)
            mem_text = ""
            text = ""
            if r:
                mem_text = f" [{mean}|{mem_size}]"
                mc = int(6*abs(mean))+2
                #gfxdraw.aacircle(screen, 55 + l * h_space, cfg.SCREEN[1] - base_line[l] + d*n + round(d/2), int(mc-1), black_color)
                gfxdraw.aacircle(screen, 55 + l * h_space, cfg.SCREEN[1] - base_line[l] + d*n + round(d/2), int(mc), black_color)
                #gfxdraw.circle(screen, 55 + l * h_space, cfg.SCREEN[1] - base_line[l] + d*n + round(d/2), int(mc-1), black_color)
            if l == 0:
                val = network.nodes[network.layers[l].nodes[n]].value
                if r:
                    text = "{:<2}:{:2> .1f}     {:>}".format(inp_desc[n], val, mem_text)
                else:
                    text = "{:<2}:{:2> .1f}".format(inp_desc[n], val)
                owner.add_text(text, 4, cfg.SCREEN[1] - base_line[l] + d*n + round(d/2) - 5, True, Color('white'))
            elif l == last_layer_idx:
                val = owner.enviro.selected.output[out]
                if r:
                    text = " {:<}:{:< .1f}{}".format(out_desc[out], val, mem_text)
                else:
                    text = " {:<}:{:< .1f}".format(out_desc[out], val)
                owner.add_text2(text, 65 + l * (h_space), cfg.SCREEN[1] - base_line[l] + d*n + round(d/2) - 2, Color('white'), False, False, False, True)
                out += 1
            else:
                val = network.nodes[network.layers[l].nodes[n]].value
                if r:
                    text = "{:^1.1f}{}".format(val, mem_text)
                else:
                    text = "{:^1.1f}".format(val)
                owner.add_text(text, 48 + l * (h_space), cfg.SCREEN[1] - base_line[l] + d*n + round(d/2) - 16, True, Color('white'))


def draw_net2(network: Network) -> Surface:
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
        net_surf = Surface.convert_alpha(net_surf)
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
                p0 = (80 + l0 * h_space, back_box.height - base_line[l0] + (dists[l0] * n0) + round(dists[l0]/2))
                p1 = (80 + l * h_space, back_box.height - base_line[l] + (dist_nn * n) + round(dist_nn/2))
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
        gfxdraw.aacircle(net_surf, 80 + l * h_space, back_box.height - base_line[l] + d*n + round(d/2), cv, v_color)
        gfxdraw.filled_circle(net_surf, 80 + l * h_space, back_box.height - base_line[l] + d*n + round(d/2), cv, v_color_alfa)
        if r:
            gfxdraw.filled_circle(net_surf, 80 + l * h_space, back_box.height - base_line[l] + d*n + round(d/2), int(cv/2), black_color)
            gfxdraw.aacircle(net_surf, 80 + l * h_space, back_box.height - base_line[l] + d*n + round(d/2), int(cv/2), c)
        #if l == 0:
            #val = network.nodes[network.layers[l].nodes[n]].value
            #text = "{:<2}:{:2> .1f}".format(inp_desc[n], val)
            #self.add_text(text, 6 + l * (h_space+10), cfg.SCREEN[1] - base_line[l] + d*n + round(d/2) - 5, True, Color('white'))
        #elif l == last_layer_idx:
            #val = self.enviro.selected.output[out]
            #text = "{:<}:{:< .1f}".format(out_desc[out], val)
            #self.add_text2(text, 90 + l * (h_space), cfg.SCREEN[1] - base_line[l] + d*n + round(d/2) - 2, Color('white'), False, False, False, True)
            #out += 1
        #else:
            #val = network.nodes[network.layers[l].nodes[n]].value
            #text = "{:^1.1f}".format(val)
            #self.add_text(text, 85 + l * (h_space), cfg.SCREEN[1] - base_line[l] + d*n + round(d/2) - 5, True, Color('white'))
        #net_surf.set_colorkey(Color(0,0,0))
        #net_surf.fill(Color(0, 0, 0))
    return net_surf

def add_text(surface: Surface, text: str, x: int, y: int, color: Color):
    txt_render = cfg.small_font.render(text, True, Color(color))
    txt_rect = txt_render.get_rect()
    txt_rect.left = x
    txt_rect.top = y
    surface.blit(txt_render, txt_rect)
