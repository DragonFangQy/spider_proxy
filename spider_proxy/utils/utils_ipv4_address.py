from copy import deepcopy
from itertools import product
from typing import List

"""
    IPV4 可用地址
    A: 1-126      exclude: 10.0-10.255        10  0-255       # 从源头跳过
                  exclude: 127.0-127.255      127 0-255       # 从源头跳过
    B: 128-192    exclude: 172.16~172.31      172.16~172.31   # 排除
    C: 192-223    exclude: 192.168-192.168    192.168         # 排除
"""

def _get_exclude_ipv4() -> List[str]:
    """
        获取需要排除的ip 地址
        匹配开头
    """

    exclude_ipv4_1_list = ["172"]  # 172
    exclude_ipv4_2_list = []  # 16~31
    exclude_ipv4_str_list = []
    for i in range(16, 31+1):
        exclude_ipv4_2_list.append(str(i))

    # 排除 172.16~172.31
    exclude_ipv4_str_list = [item_ipv4_1__ipv4_2 for item_ipv4_1__ipv4_2 in product(exclude_ipv4_1_list,exclude_ipv4_2_list) ]

    # 排除 192.168
    exclude_ipv4_str_list.append( ("192", "168") )

    return exclude_ipv4_str_list

def _get_ipv4_portion():
    """
        得到ip 地址的 4个部分
    """

    # [1-223].[0-255].[0-255].[1-254]
    ipv4_1_list = []    # ipv4 第一部分 [1-223]
    ipv4_2_list = []    # ipv4 第二部分 [0-255]
    ipv4_3_list = []    # ipv4 第三部分 [0-255]
    ipv4_4_list = []    # ipv4 第四部分 [1-254]
 
    # 第一部分
    for i in range(1,223+1):

        # 从源头跳过 10 和 127 开头的 IP
        if i == 10 or i ==127:
            continue
        ipv4_1_list.append(str(i))

    # 第二部分
    for i in range(0,255+1):
        ipv4_2_list.append(str(i))

    # 第三部分
    ipv4_3_list = ipv4_2_list

    # 第四部分
    ipv4_4_list = deepcopy(ipv4_2_list)
    ipv4_4_list.remove("0")
    ipv4_4_list.remove("255")

    return ipv4_1_list, ipv4_2_list, ipv4_3_list, ipv4_4_list

def get_all_ipv4():
    """
        得到所有可用的ip 地址
    """
    exclude_ipv4_prefix_list = _get_exclude_ipv4()
    for ipv4_portion in product(*_get_ipv4_portion()):
        
        prefix = ipv4_portion[:2]
        # 第一次对 list in list，测试了几次，没发现问题，就先这样写吧 
        if prefix in exclude_ipv4_prefix_list:
            # 排除
            continue
        
        # 用 yield 吧，存到list 中也不清楚要消耗多少内存
        # yield 保险点
        yield ".".join(ipv4_portion)

def get_all_ipv4_port():
    """
        知名端口号：知名端口号是指众所周知的端口号，范围从0到1023。
        动态端口号：一般程序员开发应用程序使用端口号称为动态端口号, 范围是从 1024 到 65535 。
    """
    
    for ipv4_address in get_all_ipv4():
        for port in range(1024, 65535+1):
            yield f"{ipv4_address}:{port}"


if __name__ == "__main__":
    
    for ipv4_address in get_all_ipv4():
        print(ipv4_address)

    
    for ipv4_port in get_all_ipv4_port():
        print(ipv4_port)
    

