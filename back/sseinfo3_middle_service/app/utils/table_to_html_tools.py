# -*- coding: utf-8 -*-
# @Time : 2021/12/15 11:08
# @Author : yangxiaobo
# @Email : yangxiaobo@datagrand.com
# @File : table_to_html_tools.py
# coding:utf-8
from typing import Dict

from HTMLTable import HTMLTable

# from document_beans.document import Document
# from document_beans.document_element.table import Table


def gen_html_document(table_dic):
    table_html_dict = {}
    text_matrix = table_dic.get('text_matrix')
    mask = table_dic.get('mask')

    text_matrix_length = len(text_matrix[0])
    mask_length = len(mask[0])

    if text_matrix_length>mask_length:
        for i in range(text_matrix_length-mask_length):
            for element  in mask:
                element.append(element[-1])

    elif mask_length>text_matrix_length:

        for i in range(mask_length - text_matrix_length):
            for element in text_matrix:
                element.append("")

    html_table = _gen_html_table_by_text_matrix(text_matrix)
    html_table = _merge_html_cell(mask, html_table)

    try:
        html_content = html_table.to_html()
    except Exception as e:
        print()
    # for label in ['body', 'html']:
    #     html_content = f'<{label}>{html_content}</{label}>'
    table_html_dict.update({'table': html_content})
    return table_html_dict


def _gen_html_table(table):
    html_table = HTMLTable()
    for i, row_cell in enumerate(table.all_cells):
        tmp_list = []
        for cell in row_cell:
            cell_content = ''
            for idx, text_line in enumerate(cell.text_lines):
                if idx > 0:
                    cell_content += '</br>'
                # cell_content += text_line
                cell_content += str(text_line)
            tmp_list.append(cell_content)
        html_table.append_data_rows((tuple(tmp_list),))
    return html_table


def _merge_html_cell(mask, html_table):
    row_num = len(mask)
    col_num = len(mask[0])
    for row in range(row_num):
        for col in range(col_num):
            if mask[row][col] == 0:
                mask[row][col] = -1
            elif mask[row][col] > 0:
                flag_num = mask[row][col]
                mask[row][col] = -1
                row_count = 0
                for idx in range(col_num - col - 1):
                    if mask[row][col + 1 + idx] == flag_num:
                        mask[row][col + 1 + idx] = -1
                        row_count += 1
                    else:
                        break
                if row_count >= 1:
                    html_table[row][col].attr.colspan = row_count + 1
                col_count = 0
                for idx in range(row_num - row - 1):
                    if mask[row + 1 + idx][col] == flag_num:
                        mask[row + 1 + idx][col] = -1
                        col_count += 1
                    else:
                        break
                if col_count >= 1:
                    html_table[row][col].attr.rowspan = col_count + 1
    return html_table


def merge_html_table(table_html_dic):
    table_tr_list = [table.split('<table>', 1)[1].rsplit('</table>', 1)[0] for k, table in table_html_dic.items()]
    return f"<table>{''.join(table_tr_list)}</table>"


def _gen_html_table_by_text_matrix(text_matrix):
    html_table = HTMLTable()
    for i, row_cell in enumerate(text_matrix):
        tmp_list = []
        for cell in row_cell:
            cell_content = ''
            cell = [cell]
            for idx, text_line in enumerate(cell):
                if idx > 0:
                    cell_content += '</br>'
                # cell_content += text_line
                cell_content += str(text_line)
            tmp_list.append(cell_content)
        html_table.append_data_rows((tuple(tmp_list),))
    return html_table