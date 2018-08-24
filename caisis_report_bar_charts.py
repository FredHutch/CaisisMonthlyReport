# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 15:33:28 2017

@author: esilgard
"""

def add(workbook, worksheet, bar_chart_space, table_format_bold, formatted_disease_group):
    for chart_specs in bar_chart_space: 
        '''
        create bar charts for age at dx and current age buckets
        '''
        worksheet.write_row(chart_specs[1]+'30', ['Ages', 'Counts'], table_format_bold)
        worksheet.write_column(chart_specs[1]+'31',chart_specs[3])
        worksheet.write_column(chr(ord(chart_specs[1]) + 1) + '31', \
            [chart_specs[2].get(x) for x in chart_specs[3]])

        chart1 = workbook.add_chart({'type': 'bar'})
        # Configure the series.
        chart1.add_series({
            'name': chart_specs[0],
            'categories': '=' + formatted_disease_group + '!$'+ chart_specs[1]+'$31:$'+ \
                chart_specs[1] +'$'+str(31+len(chart_specs[3])),
            'values':     '=' + formatted_disease_group + '!$'+ chr(ord(chart_specs[1])+1) \
                + '$31:$' + chr(ord(chart_specs[1])+1) + '$' + \
                str(31+len(chart_specs[3])),
            'fill': {'color': '#207c7e'},
            'overlap': 10,
            'border': {'color': 'black'},
        
        })

        # Add a chart title and some axis labels.
        chart1.set_title ({'name':chart_specs[0]})
        chart1.set_x_axis({'name': 'Counts'})
        chart1.set_y_axis({'name': 'Age', 'interval_unit': 1})
        
        # Set an Excel chart style.
        chart1.set_style(11)
        chart1.set_legend({'position': 'none'})
        # Insert the chart into the worksheet (with an offset)
        worksheet.insert_chart(chart_specs[1]+'15', chart1, )
    return worksheet