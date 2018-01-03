# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 11:12:08 2017

@author: esilgard

make pie charts for quick snapshots of data element breakdown
"""
import os
import json
from random import choice

dir_path = os.path.dirname(os.path.realpath(__file__))
config = json.load(open(dir_path + os.path.sep + 'resources' + os.path.sep + 'config.json','r'))
pattern_fills = config['pattern_fills']
brand_colors = config['brand_colors']

#variable placement of pie chart depending on size 
#(larger ones to the side of the data, smaller ones below)
size_d = {'s': {'top_left_row':'5','top_left_col_add':0,'width':175, 'height':150},
          'l': {'top_left_row':'2','top_left_col_add':3,'width':300, 'height':250}}


def add(worksheet, chart_space, workbook, formatted_dz,): 
    for chart_specs in chart_space: 
        chart = workbook.add_chart({'type': 'pie'})   
        title = chart_specs[0]
        column = chart_specs[1]        
        cells = chart_specs[2]
        split_cells = cells.split(':')
        size = chart_specs[3]
        points = __format_chart(split_cells)
        # Configure the series and add user defined segment colors.
        chart.add_series({
            'categories': '=' + formatted_dz + '!$'+ column + split_cells[0] + ':$'+ column + split_cells[-1],
            'values': '=' + formatted_dz + '!$'+ chr(ord(column)+1) + split_cells[0] + \
            ':$' + chr(ord(column)+1) + split_cells[-1],
            'points': points
        })
       
        # Add a title.
        chart.set_title({'name': title,'size':5})
        chart.set_size({'width': size_d[size]['width'], 'height': size_d[size]['height']})
        if size == 'l':
            chart.set_legend({'layout':{'x':.7,'y': .1,'width':.25,'height':1}})
        # Insert the chart into the worksheet
        worksheet.insert_chart((chr(ord(column)+size_d[size]['top_left_col_add']) + \
                size_d[size]['top_left_row']), chart)
    return worksheet        



def __format_chart(split_cells):  
    """
    format colors and fill depending on size of data (this pulls colors and 
    patterns at random from config file for charts with many/unknown number of categories)
    specifically for primary of liver mets, which may change at any time
    """
    points = []
    data_size = int(split_cells[-1]) - int(split_cells[0]) + 1

    if data_size > 2:
        for i in xrange(data_size):
            d = {'pattern': {'fg_color': choice(brand_colors),
                            'bg_color': choice(brand_colors),
                            'pattern': choice(pattern_fills)}
             }  
            points.append(d)
        return points
    else:
        return [
                {'fill': {'color': brand_colors[0]}},                
                {'fill': {'color': brand_colors[1]}}
            ]    
    
