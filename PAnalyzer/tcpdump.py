# -*- coding: utf-8 -*-
# filename: tcpdump_retransmission.py

import gc
import json
import logging

from multiprocessing import Process
from multiprocessing import Lock

from python import libstorm as storm

DATA_PACKET_SIZE_ON_WIRE_IN_BYTE = 1514
PACKET_OVERHEAD_ON_WIRE = 66

DEFAULT_SERVER_PORT = '5201'

TASK_STATUS_LOG_TEMPLATE = 'Task "%s, rtt=%s, loss=%s", status=%s'
RUNTIME_LOG_NAME_TEMPLATE = 'runtime-%s-rtt%s-loss%s.log'

IPERF_FILE_NAME_TEMPLATE = './%s/iperf3-%s-rtt%s-loss%s-1g-%s.json'
TCPDUMP_FILE_NAME_TEMPLATE = './%s/tcpdump-%s-rtt%s-loss%s-1g-%s.log'

# 当数据包发送次数大于等于 2 时, 认为发生了一次丢包
DATA_PACKET_LOSS_THRESHOLD = 2
# 当 ack 数目大于等于 3 时, 认为发生了一次丢包
ACK_LOSS_THRESHOLD = 3


def get_global_dataset():
    """获取全局数据集

    Returns:
        (dict): 包含所有指定字段的数据集
    """
    return {
        'payload_sent': 0,
        'payload_retransmitted': 0,

        'packet_sent': 0,
        'packet_retransmitted': 0,

        'on_wire_sent_sender': 0,
        'on_wire_retransmitted_sender': 0,
        'on_wire_sent_receiver': 0,
        'on_wire_retransmitted_receiver': 0,
        'on_wire_total': 0,

        # 分别由收发双方识别出来的丢包数
        'packet_loss_sender': 0,
        'packet_loss_receiver': 0,

        'r/l': 0,

        # 来自 iperf 的数据
        'iperf_throughput': 0,
        'iperf_duration': 0,
        'iperf_retransmission': 0
    }


def get_round_dataset():
    """为每一轮的数据创建空白数据集

    Returns:
        (dict): 收发双方共用的空白数据集. 发送方使用 packet_retransmitted 字段.
        接收方识别出来的丢包使用 packet_loss_sender 字段, 接收方识别出来的丢包
        使用 packet_loss_receiver 字段.
    """
    return {
        # 所有发送的数据包的数据集
        'packets': {},

        # 在添加数据包的时候可以直接计算的字段
        'payload_sent': 0,
        'payload_retransmitted': 0,

        'packet_sent': 0,
        'packet_retransmitted': 0,

        'on_wire_sent': 0,
        'on_wire_retransmitted': 0,

        # 分别由收发双方识别出来的丢包数
        'packet_loss_sender': 0,
        'packet_loss_receiver': 0,

        # 来自 iperf 的数据
        'iperf_throughput': 0,
        'iperf_duration': 0,
        'iperf_retransmission': 0
    }


def extract(line):
    """获取 tcpdump 记录当中所包含的各种有用信息

    例如, 在与以下记录相类似的 tcpdump 记录中获取数据包的序列号, 收发双方的 ip
    地址, 包长度.
    16:41:31.869665 IP 10.0.0.7.42984 > 10.0.0.8.5208: Flags [.],
    seq 1059268509:1059280093, ack 1, win 58, options [nop,nop,
    TS val 1833200120 ecr 46901062], length 11584

    Args:
        (str) line: 一行 tcpdump 记录
    Returns:
        (str, int, str, str, str, str):
        序列号, 数据包长度, 发送方 ip, 发送方端口号, 接收方 ip, 接收方端口号
    """
    # 把这一行记录分成数组, 然后通过直接取数的方式来避免使用正则表达式.
    line_split = line.split(' ')

    # 使用 -1 来避免取到末尾的逗号
    seq = line_split[8][:-1]
    # 获取数据包长度
    size = int(line_split[-1])
    # 获取发送方的 ip 地址与端口号
    last_index = line_split[2].rindex('.')
    sip = line_split[2][0:last_index]
    sport = line_split[2][last_index + 1:]
    # 获取接收方的 ip 地址与端口号
    last_index = line_split[4].rindex('.')
    rip = line_split[4][0:last_index]
    # 使用 -1 来避免取到末尾的分号
    rport = line_split[4][last_index + 1:-1]

    return seq, size, sip, sport, rip, rport


def is_new_test(port, cskp, dskp, default_server_port):
    """检查新的一行的发送方端口号是否与现有的控制 socket 端口号 (cskp) 或者数据
    socket 端口号 (dskp) 相同. 若输入的端口号与 cskp 和 dskp 均不相等, 则表明这
    是一次新的测试.

    Args:
        (str) port: 新的一行的端口号
        (str) cskp: 控制 socket 端口号 (control socket port)
        (str) dskp: 数据 socket 端口号 (data socket port)
        (str) default_server_port: 服务器的监听端口号. 默认值是 5201.
    Returns:
        (bool) 给定的端口号是否属于一次新的测试
    """
    return port != cskp and port != dskp and port != default_server_port


def get_dskp(i, length, lines, iperf_sender_ip, cskp):
    """获取当前测试的数据 socket 端口号 (dskp).

    从第 i 行开始寻找 dskp. 由于 dskp 会在之后的行中出现, 并且所在行的 IP 地址
    与 sip 相等, 但是端口号不等于 sport. 则可以利用这一特性查找 dskp.

    Args:
        (int)   i: 开始位置
        (int)   length: 文件最大行数
        (list)  lines: 文件每一行
        (str)   sip: 源地址
        (sport) sport: 源端口
    Returns:
        (str, int) 端口号, 以及 cskp 所在的行号
    """
    for j in range(i, length):
        seq, size, sip, sport, rip, rport = extract(lines[j])
        if sip == iperf_sender_ip and sport != cskp:
            # 返回 dskp 以及所在的行
            return sport, j


def add_new_packet(seq, length, data_set):
    """处理该数据包的记录

    Args:
        (str)  seq:       数据包序列号
        (int)  length:    数据包长度
        (dict) data_set:  数据包数据集
    """
    if not (seq in data_set['packets']):
        # 若给定的 seq 第一次出现, 则证明此数据包是第一次发送的, 需要为其创建 entry.
        data_set['packets'][seq] = 0
        data_set['payload_sent'] += length
        data_set['packet_sent'] += 1
        data_set['on_wire_sent'] += (length + PACKET_OVERHEAD_ON_WIRE)
    else:
        # 若给定的 seq 已经在数据集当中, 则证明此数据包是被重传的的数据包.
        data_set['payload_retransmitted'] += length
        data_set['packet_retransmitted'] += 1
        data_set['on_wire_retransmitted'] += (length + PACKET_OVERHEAD_ON_WIRE)

    # 发送次数加一
    data_set['packets'][seq] += 1


def get_loss(packets, threshold):
    """基于数据包日志计算丢包数目

    Args:
        (dict) packets:     数据包数据集
        (int) threshold:    单个包的发送次数丢包门限, 超过此值即为丢包
    Returns
        (int) loss: 丢包数目
    """
    loss = 0
    for value in packets.values():
        if value >= threshold:
            loss += 1
    return loss


def is_data_socket(ip, port, iperf_sender_ip, dskp):
    """判断给定的 IP 地址与端口号是否属于数据 socket.

    把给定的 IP 地址与端口号和 iperf 测试当中的发送方的 IP 地址与以及数据 socket
    的端口号向匹配. 当给定的 IP 地址与端口号属于记录中的发送方时, 如果匹配成功,
    则证明这一行记录是 iperf 测试的发送方在向接收方发送数据. 当给定的 IP 地址与
    端口号属于记录中的接收方时, 匹配成功则证明这是向 iperf 测试的发送方返回 ACK.

    这两种情况均需要统计相关数据.

    Args:
        (str) ip:               当前行中发送方的 IP 地址
        (str) port:             当前行中发送方的端口号
        (str) iperf_sender_ip:  这个网络拓扑中的 iperf 发送方的 IP 地址
        (str) dskp:             当前测试的数据 socket 端口号
    Returns:
        (bool): 若给定的 IP 地址与端口号属于数据 socket, 则返回 True; 否则返回 False.
    """
    return (ip == iperf_sender_ip) and (port == dskp)


def get_iperf_result(data_set, algorithm, rtt, loss, nth_run):
    """获取与本次测试对应的 iperf3 测试结果

    Args:
        (dict) data_set:       结果集
        (str) algorithm:    本次测试的算法
        (str) rtt:          本次测试的 RTT
        (str) loss:         本次测试的丢包率
        (str) nth_run:      第几次测试
    """
    iperf_file_name = IPERF_FILE_NAME_TEMPLATE % \
        (algorithm, algorithm, rtt, loss, nth_run)
    json_object = json.load(open(iperf_file_name, 'r'))
    data_set['iperf_duration'] = json_object['end']['sum_sent']['seconds']
    data_set['iperf_retransmission'] = \
        json_object['end']['sum_sent']['retransmits']
    data_set['iperf_throughput'] = \
        json_object['end']['sum_sent']['bits_per_second'] / storm.M


def get_packets(lines, stats, role, description, local_logger):
    """从 tcpdump 抓包记录中获取所有发送方或者接收方从数据 socket 中发出去的包的
    集合.

    Args:
        (str)     lines:            tcpdump 行合集
        (dict)    stats:            记录数据集
        (str)     role:             目标角色
        (dict)    description:      任务描述
        (logger)  local_logger:     当前任务所使用的 logger
    """

    algorithm = description['algorithm']
    rtt = description['rtt']
    loss = description['loss']

    # -------- 初始化各种变量 --------
    # 数据文件的最大行数
    length = len(lines)
    # 当前循环包含的是本文件包含的第几次实验
    nth_run = 1

    # -------- 这几行充当循环的初始条件 --------
    # 由于在同一个文件当中, iperf 测试的发送方与接收方的 IP 地址都是固定的, 所以
    # 可以保存起来, 用在判断发送方角色的语句当中.
    # sip 和 dip 分别当前行中收发双方的 IP 地址. sport 和 rport 分别是当前行中
    # 收发双方的端口号.
    seq, size, sip, sport, rip, rport = extract(lines[0])
    iperf_sender_ip = sip
    # control_socket_port, 控制 socket 的端口号
    # data_socket_port, 数据 socket 的端口号
    # 在每一次测试的第一行就能拿到 cskp, 但是 dskp 需要遍历后面的行才能找到
    cskp = sport
    # 获取 dskp 并跳过 cskp 建立连接的行
    dskp, i = get_dskp(0, length, lines, iperf_sender_ip, cskp)

    # 为第一次实验的数据创建 entry
    key = cskp + dskp
    stats[key] = get_round_dataset()

    local_logger.info(
        str(nth_run) + '. Found new test at line: ' + str(i) + ', cskp=' +
        cskp + ', dskp=' + dskp + '.')

    # 加载位于 iperf 的记录当中的带宽, 测试时间, 以及重传
    if role == 'sender':
        local_logger.info(
            'Loading iperf file: "' + IPERF_FILE_NAME_TEMPLATE %
            (algorithm, algorithm, rtt, loss, nth_run) + '"')
        get_iperf_result(stats[key], algorithm, rtt, loss, nth_run)

    # -------- 开始遍历数据文件 --------
    while i < length:
        # 跳过空行与最后一行
        if lines[i] == '' or i == length - 1:
            i += 1
            continue

        # 获取当前行中保存的收发双方的 IP 地址和端口号
        seq, size, sip, sport, rip, rport = extract(lines[i])

        if is_new_test(sport, cskp, dskp, DEFAULT_SERVER_PORT):
            # 设置新测试的 cskp 和 dskp
            cskp = sport
            dskp, i = get_dskp(i, length, lines, iperf_sender_ip, cskp)

            nth_run += 1
            local_logger.info(
                str(nth_run) + '. Found new test at line: ' + str(i) +
                ', cskp=' + cskp + ', dskp=' + dskp + '.')

            # 为本次实验数据创建 entry
            key = cskp + dskp
            stats[key] = get_round_dataset()

            # 加载新一次测试的 iperf 数据
            if role == 'sender':
                local_logger.info(
                    'Loading iperf file: "' + IPERF_FILE_NAME_TEMPLATE %
                    (algorithm, algorithm, rtt, loss, nth_run) + '"')
                get_iperf_result(stats[key], algorithm, rtt, loss, nth_run)

        # 只统计收发双方在数据 socket 上发送的数据
        if is_data_socket(sip, sport, iperf_sender_ip, dskp) and \
                role == 'sender':
            # 发送方发出的数据, 主要是待发送的 TCP Payload 以及部分控制信息
            add_new_packet(seq, size, stats[key])
        elif is_data_socket(rip, rport, iperf_sender_ip, dskp) and \
                role == 'receiver':
            # 接收方发送的数据, 主要是 ACK 以及部分控制信息
            add_new_packet(seq, size, stats[key])

        i += 1

    # 分别计算收发双方的数据中识别出来的 packet loss
    if role == 'sender':
        for value in stats.values():
            value['packet_loss_sender'] = get_loss(
                value['packets'], DATA_PACKET_LOSS_THRESHOLD)
    if role == 'receiver':
        for value in stats.values():
            value['packet_loss_receiver'] = get_loss(
                value['packets'], ACK_LOSS_THRESHOLD)


def get_global_stats(sender_stats, receiver_stats, local_logger):
    """从收发双方的数据当中计算结果, 继续以 cskp + dakp 为每一次的实验的 entry.
    'average' 字段中包含所有实验的平均统计结果.

    Args:
        (dict) sender_stats:    发送方的数据集
        (dict) receive_stats:   接收方的数据集
        (logger) local_logger:  当前任务使用的 logger
    Returns:
        (dict) global_stats: 所有实验的统计结果
    """
    global_stats = {}

    # 用于计算总体平均值的临时变量
    payload_sent = 0.0
    payload_retransmitted = 0.0

    packet_sent = 0.0
    packet_retransmitted = 0.0

    packet_loss_sender = 0.0
    packet_loss_receiver = 0.0

    on_wire_sent_sender = 0.0
    on_wire_retransmitted_sender = 0.0
    on_wire_sent_receiver = 0.0
    on_wire_retransmitted_receiver = 0.0
    on_wire_total = 0.0

    iperf_throughput = 0.0
    iperf_duration = 0.0
    iperf_retransmission = 0.0

    keys = sender_stats.keys()
    # 文件中包含的测试次数
    test_count = float(len(keys))

    for key in keys:
        global_stats[key] = get_global_dataset()

        # -------- 计算单次测试的数据 --------
        # payload
        global_stats[key]['payload_sent'] = \
            float(sender_stats[key]['payload_sent']) / storm.G
        global_stats[key]['payload_retransmitted'] = \
            float(sender_stats[key]['payload_retransmitted']) / storm.G
        # packet
        global_stats[key]['packet_sent'] = sender_stats[key]['packet_sent']
        global_stats[key]['packet_loss_sender'] = \
            sender_stats[key]['packet_loss_sender']
        global_stats[key]['packet_loss_receiver'] = \
            receiver_stats[key]['packet_loss_receiver']
        global_stats[key]['packet_retransmitted'] = \
            sender_stats[key]['packet_retransmitted']
        # on_wire
        global_stats[key]['on_wire_sent_sender'] = \
            float(sender_stats[key]['on_wire_sent']) / storm.G
        global_stats[key]['on_wire_retransmitted_sender'] = \
            float(sender_stats[key]['on_wire_retransmitted']) / storm.G
        global_stats[key]['on_wire_sent_receiver'] = \
            float(receiver_stats[key]['on_wire_sent']) / storm.G
        global_stats[key]['on_wire_retransmitted_receiver'] = \
            float(receiver_stats[key]['on_wire_retransmitted']) / storm.G
        global_stats[key]['on_wire_total'] = \
            float(sender_stats[key]['on_wire_sent'] +
                  receiver_stats[key]['on_wire_sent']) / storm.G
        # ratio
        if receiver_stats[key]['packet_loss_receiver'] != 0:
            global_stats[key]['r/l'] = \
                float(sender_stats[key]['packet_retransmitted']) / \
                float(receiver_stats[key]['packet_loss_receiver'])
        else:
            global_stats[key]['r/l'] = 0

        global_stats[key]['iperf_throughput'] = \
            sender_stats[key]['iperf_throughput']
        global_stats[key]['iperf_duration'] = \
            sender_stats[key]['iperf_duration']
        global_stats[key]['iperf_retransmission'] = \
            sender_stats[key]['iperf_retransmission']

        # 打印单次测试数据
        local_logger.info('-------- ' + key + ' --------')
        local_logger.info('payload_sent (GB):                   %-3.3f' %
                          global_stats[key]['payload_sent'])
        local_logger.info('payload_retransmitted (GB):          %-3.3f' %
                          global_stats[key]['payload_retransmitted'])
        local_logger.info('packet_sent:                         %-d' %
                          global_stats[key]['packet_sent'])
        local_logger.info('packet_loss_sender:                  %-d' %
                          global_stats[key]['packet_loss_sender'])
        local_logger.info('packet_loss_receiver:                %-d' %
                          global_stats[key]['packet_loss_receiver'])
        local_logger.info('packet_retransmitted:                %-d' %
                          global_stats[key]['packet_retransmitted'])
        local_logger.info('on_wire_sent_sender (GB):            %-3.3f' %
                          global_stats[key]['on_wire_sent_sender'])
        local_logger.info(
            'on_wire_retransmitted_sender (GB):   %-3.3f' %
            global_stats[key]['on_wire_retransmitted_sender'])
        local_logger.info('on_wire_sent_receiver (GB):          %-3.3f' %
                          global_stats[key]['on_wire_sent_receiver'])
        local_logger.info(
            'on_wire_retransmitted_receiver (GB): %-3.3f' %
            global_stats[key]['on_wire_retransmitted_receiver'])
        local_logger.info(
            'on_wire_total (GB):                  %-3.3f' %
            float(global_stats[key]['on_wire_sent_sender'] +
                  global_stats[key]['on_wire_retransmitted_sender'] +
                  global_stats[key]['on_wire_sent_receiver'] +
                  global_stats[key]['on_wire_retransmitted_receiver']))
        local_logger.info('r/l                                  %-3.3f' %
                          global_stats[key]['r/l'])
        local_logger.info('iperf3 throughput (Mbps):            %-3.3f' %
                          global_stats[key]['iperf_throughput'])
        local_logger.info('iperf3 duration (s):                 %-3.3f' %
                          global_stats[key]['iperf_duration'])
        local_logger.info('iperf3 retransmission:               %-3.3f' %
                          global_stats[key]['iperf_retransmission'])

        # -------- 积累总体平局值 --------
        # payload
        payload_sent += float(sender_stats[key]['payload_sent']) / storm.G
        payload_retransmitted += \
            float(sender_stats[key]['payload_retransmitted']) / storm.G

        # packet
        packet_sent += sender_stats[key]['packet_sent']
        packet_retransmitted += sender_stats[key]['packet_retransmitted']

        packet_loss_sender += sender_stats[key]['packet_loss_sender']
        packet_loss_receiver += receiver_stats[key]['packet_loss_receiver']

        # on_wire
        on_wire_sent_sender += \
            float(sender_stats[key]['on_wire_sent']) / storm.G
        on_wire_retransmitted_sender += \
            float(sender_stats[key]['on_wire_retransmitted']) / storm.G
        on_wire_sent_receiver += \
            float(receiver_stats[key]['on_wire_sent']) / storm.G
        on_wire_retransmitted_receiver += \
            float(receiver_stats[key]['on_wire_retransmitted']) / storm.G
        on_wire_total += float(
            global_stats[key]['on_wire_sent_sender'] +
            global_stats[key]['on_wire_retransmitted_sender'] +
            global_stats[key]['on_wire_sent_receiver'] +
            global_stats[key]['on_wire_retransmitted_receiver']
        )

        iperf_throughput += sender_stats[key]['iperf_throughput']
        iperf_duration += sender_stats[key]['iperf_duration']
        iperf_retransmission += sender_stats[key]['iperf_retransmission']

    # -------- 根据积累的数据计算总体平均值 --------
    global_stats['average'] = get_global_dataset()

    # payload
    global_stats['average']['payload_sent'] = float(payload_sent) / test_count
    global_stats['average']['payload_retransmitted'] = \
        float(payload_retransmitted) / test_count

    # packet
    global_stats['average']['packet_sent'] = float(packet_sent) / test_count
    global_stats['average']['packet_retransmitted'] = \
        float(packet_retransmitted) / test_count

    global_stats['average']['packet_loss_sender'] = \
        float(packet_loss_sender) / test_count
    global_stats['average']['packet_loss_receiver'] = \
        float(packet_loss_receiver) / test_count

    # on_wire
    global_stats['average']['on_wire_sent_sender'] = \
        float(on_wire_sent_sender) / test_count
    global_stats['average']['on_wire_retransmitted_sender'] = \
        float(on_wire_retransmitted_sender) / test_count
    global_stats['average']['on_wire_sent_receiver'] = \
        float(on_wire_sent_receiver) / test_count
    global_stats['average']['on_wire_retransmitted_receiver'] = \
        float(on_wire_retransmitted_receiver) / test_count
    global_stats['average']['on_wire_total'] = \
        float(on_wire_total) / test_count
    # ratio
    if global_stats['average']['packet_loss_receiver'] != 0:
        global_stats['average']['r/l'] = \
            float(global_stats['average']['packet_retransmitted']) / \
            float(global_stats['average']['packet_loss_receiver'])
    else:
        global_stats['average']['r/l'] = 0

    global_stats['average']['iperf_throughput'] = \
        float(iperf_throughput) / test_count
    global_stats['average']['iperf_duration'] = \
        float(iperf_duration) / test_count
    global_stats['average']['iperf_retransmission'] = \
        float(iperf_retransmission) / test_count

    return global_stats


def print_global_stats(global_stats, local_logger):
    """打印 global_stats 当中包含的结果

    Args:
        (dict) global_stats:    全局数据集
        (logger) local_logger:  本次任务所采用的 logger
    """
    average = global_stats['average']
    local_logger.info('-------- average --------')
    local_logger.info('Payload sent (GB):                    %-3.3f' %
                      average['payload_sent'])
    local_logger.info('Payload retransmitted (GB):           %-3.3f' %
                      average['payload_retransmitted'])
    local_logger.info('Packet sent:                          %-3.3f' %
                      average['packet_sent'])
    local_logger.info('Packet retransmitted:                 %-3.3f' %
                      average['packet_retransmitted'])
    local_logger.info('Packet loss, Sender:                  %-3.3f' %
                      average['packet_loss_sender'])
    local_logger.info('Packet loss, Receiver:                %-3.3f' %
                      average['packet_loss_receiver'])
    local_logger.info('On-wire Sender, Sent (GB):            %-3.3f' %
                      average['on_wire_sent_sender'])
    local_logger.info('On-wire Sender, Retransmitted (GB):   %-3.3f' %
                      average['on_wire_retransmitted_sender'])
    local_logger.info('On-wire Receiver, Sent (GB):          %-3.3f' %
                      average['on_wire_sent_receiver'])
    local_logger.info('On-wire Receiver, Retransmitted (GB): %-3.3f' %
                      average['on_wire_retransmitted_receiver'])
    local_logger.info('On-wire Total (GB):                   %-3.3f' %
                      average['on_wire_total'])
    local_logger.info('R/L:                                  %-3.3f' %
                      average['r/l'])
    local_logger.info('iperf3 throughput (Mbps):             %-3.3f' %
                      average['iperf_throughput'])
    local_logger.info('iperf3 duration (s):                  %-3.3f' %
                      average['iperf_duration'])
    local_logger.info('iperf3 retransmission:                %-3.3f' %
                      average['iperf_retransmission'])


def run(algorithm, rtts, loss, read_lock, name):

    fmt = '%(asctime)s - %(levelname)s: %(message)s'
    local_logger = logging.getLogger(name)
    local_logger.setLevel(logging.INFO)
    log_file = name + '.log'
    local_file_handler = logging.FileHandler(log_file)
    local_file_handler.setLevel(logging.INFO)
    local_file_handler.setFormatter(logging.Formatter(fmt))
    local_logger.addHandler(local_file_handler)

    # 获取本次任务的相关信息
    for a in algorithm:
        for r in rtts:
            for l in loss:

                local_logger.info(
                    TASK_STATUS_LOG_TEMPLATE % (a, r, l, 'STARTED'))

                sender_file_name = \
                    TCPDUMP_FILE_NAME_TEMPLATE % (a, a, r, l, 'sender')
                receiver_file_name = \
                    TCPDUMP_FILE_NAME_TEMPLATE % (a, a, r, l, 'receiver')

                # 初始化数据集
                sender_stats = {}
                receiver_stats = {}

                read_lock.acquire()
                local_logger.info('Lock Acquired, loading tcpdump files.')
                local_logger.info('Loading: ' +
                                  TCPDUMP_FILE_NAME_TEMPLATE %
                                  (a, a, r, l, 'sender'))
                sender_lines = storm.read_text_file(sender_file_name)
                local_logger.info('Loading: ' +
                                  TCPDUMP_FILE_NAME_TEMPLATE %
                                  (a, a, r, l, 'receiver'))
                receiver_lines = storm.read_text_file(receiver_file_name)
                local_logger.info('Finished loading, lock released.')
                read_lock.release()

                # 获取收发双方的 tcpdump 记录当中发送的数据包, 为每一次测试计算当次的统计数据
                description = {
                    'algorithm': a,
                    'rtt': r,
                    'loss': l
                }
                get_packets(sender_lines, sender_stats, 'sender',
                            description, local_logger)
                get_packets(receiver_lines, receiver_stats, 'receiver',
                            description, local_logger)

                # 强制系统进行 gc, 回收多余的 packets 数组
                for value in sender_stats.values():
                    del value['packets']
                for value in receiver_stats.values():
                    del value['packets']
                gc.collect()

                # 计算各种全局数据
                global_stats = get_global_stats(
                    sender_stats, receiver_stats, local_logger)

                # 所有测试的平均数据
                print_global_stats(global_stats, local_logger)

                local_logger.info(
                    TASK_STATUS_LOG_TEMPLATE % (a, r, l, 'FINISHED'))


def main():

    # 测试设置
    algorithm = ['illinois']

    rtt_1 = ['12', '30']
    rtt_2 = ['60', '100']
    rtt_3 = ['200', '300']

    loss = ['0.01', '0.05', '0.1', '0.2', '0.4',
            '0.6', '0.8', '1.0', '3.0', '5.0']

    read_lock = Lock()

    task_1 = Process(target=run, args=(
        algorithm, rtt_1, loss, read_lock, algorithm[0] + '-process-1', ))
    task_2 = Process(target=run, args=(
        algorithm, rtt_2, loss, read_lock, algorithm[0] + '-process-2', ))
    task_3 = Process(target=run, args=(
        algorithm, rtt_3, loss, read_lock, algorithm[0] + '-process-3', ))

    task_1.start()
    task_2.start()
    task_3.start()

    task_1.join()
    task_2.join()
    task_3.join()


if __name__ == '__main__':
    main()