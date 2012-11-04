# -*- coding: utf-8 -*-

"""
Author: David Wong <davidwong.xc@gmail.com>
License: 3 clause BSD license

This module contains classes for parsing profiler output. Output is formatted into a json graph
representation.

"""

from decimal import Decimal
import re
import subprocess

from django.utils import simplejson


class PstatsWriter(object):
    """
    Takes an output file from cProfile
    Writes a JSON graph representation to send to the browser
    Creates and returns self.graph
    """
    
    def __init__(self, gprof_file_path):
        gprof = self.format_profile(gprof_file_path)
        self.profile = gprof
        #self.nodes_edges_list is a list of the graph's nodes and edges
        #self.nodes_edges_list is created by calling self.profile.split(';\n\t')
        self.nodes_edges_list = None
        
        #Order nodes and edges are added in doesn't matter. The client side JS just has to add nodes first.
        #table_nodes is formatted for the html table
        
        self.graph = {"nodes":[], "edges":[], "table_nodes": []}
        
    
    def format_profile(self, gprof_file_path):
        #Formats Python cProfile output using gprof2dot, making it easier to parse.
        
        #To do: add arguments to check_output() to prune nodes and edges below a % time
        #Use gprof2dot for Python because it already does some formatting
        
        return_string = subprocess.check_output(["gprof2dot", "-f", "pstats", gprof_file_path])
        start = return_string.find('graph [')
        end = return_string.rfind(';')

        profile_string = return_string[start:(end + 1)]
        return profile_string
    
    def create_nodes_edges_list(self):
        self.nodes_edges_list = self.profile.split(';\n\t')
        self.nodes_edges_list = self.nodes_edges_list[3:len(self.nodes_edges_list)]
        
    def create_graph(self):
        #Creates self.graph, which is the json representation sent to the browser.
        
        nodes_list = [i for i in self.nodes_edges_list if i.find('->') == -1]
        edges_list = [i for i in self.nodes_edges_list if i.find('->') != -1]
        
        #Create nodes first because create_edges looks up node labels in self.graph["nodes"]
        for node in nodes_list:
            self.create_node(node)
            
        for edge in edges_list:
            self.create_edge(edge)
        
        self.graph["nodes"].sort(key=lambda node: Decimal(node['total_time'])) 
    
    def create_edge(self, edge_string):
        edge = {'start': None, 'end': None, 'label': None}
        reg_exp = re.compile(r"\d+")
        
        #Just using this reg exp to get the edge's start and end, which are the first two numbers.
        numbers = reg_exp.findall(edge_string)
        start_number = int(numbers[0])
        end_number = int(numbers[1])
        
        start = None
        end = None
        
        """For edges, we need edge['start'] and edge['end'] to be the string labels of the nodes. We're looking
        up the string labels below."""
        
        for node in self.graph["nodes"]:
            if start_number == node['number']:
                start = node['label']
            if end_number == node['number']:
                end = node['label']
        
        edge['start'] = start
        edge['end'] = end
        
        #Look through the edge string to find the edge label
        label_index = edge_string.find("label=")
        label_start = edge_string.find('"', label_index)
        label_end = edge_string.find('"', (label_start + 1))
        label = edge_string[(label_start + 1): label_end]
        label_clean = label.replace('\\n', ' ')
        
        edge['label'] = label_clean
        self.graph["edges"].append(edge)
                
    
    def format_table_node(self, label):
        #Replace < and > characters for HTML
        table_node_label = label.replace('<', '')
        table_node_label = table_node_label.replace('>', '')
        
        #Look through the node string to find the running times
        reg_exp = re.compile(r"\d+\.\d+")
        time_index = table_node_label.find('\\n')
        s = table_node_label[time_index:]
        running_times = reg_exp.findall(s)
        total_time = running_times[0]
        self_time = running_times[1]
        
        last_sep_index = table_node_label.rfind('\\n')
        table_node_label = table_node_label[:time_index] + '\\n' + total_time + '\\n' + self_time\
                           + '\\n' + table_node_label[(last_sep_index + 2):]  
        
        return table_node_label, total_time
            
    def create_node(self, node_string):
        #'number' in node is used in create_edge, to look up the node's label.
        node = {'number': None, 'label': None, 'total_time': None}
        reg_exp = re.compile(r"\d+")
        
        numbers = reg_exp.findall(node_string)
        num = int(numbers[0])
        node['number'] = num
        
        label_index = node_string.find("label=")
        label_start = node_string.find('"', label_index)
        label_end = node_string.find('"', (label_start + 1))
        label = node_string[(label_start + 1): label_end]
       
        #table_node is formatted for the html table, while node is formatted for the graph
        table_node_label, total_time = self.format_table_node(label) 
        table_node = {'label': None}
        table_node['label'] = table_node_label
        self.graph['table_nodes'].append(table_node)
        
        label_clean = label.replace('\\n', ' ')
        node['label'] = label_clean
        node['total_time'] = total_time
        self.graph["nodes"].append(node)
    
    def return_graph(self):
        return self.graph   
    


