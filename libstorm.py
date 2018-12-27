# coding=utf-8
# filename: libstorm.py

import json
import re
import time

import numpy as np

K = 1024.0
M = K * 1024.0
G = M * 1024.0


def log(message):
  print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' ' + message


def get_retransmission(iperf_json_object):
  return iperf_json_object['end']['streams'][0]['sender']['retransmits']


def get_number_by_percentage_index(array, percentage, sorted=False):
  """按照指定的下标百分比从数组中获取元素

  Args:
    array: 数据源, 可以是已排序数组或者未排序数组.
    percentage: 下标百分比, 接受整数参数, 如 95 % 则输入 95.
    sorted: 指示输入的数组是否已排序, 当此值为 True 时, 认为此数组已排序; 否则认为其尚未得到排序.
  Returns:
    具有下标为已排序数组中指定百分比的元素.
  """
  # 异常情况退出
  if len(array) == 0 or percentage > 100 or percentage < 0:
    return
  # 临时数组
  new_array = []
  # 若数组尚未排序, 则对其进行排序, 否则直接添加到临时数组当中
  if sorted == False:
    new_array.extend(np.sort(array))
  else:
    new_array.extend(array)
  return new_array[int(len(new_array) * (float(percentage) / 100.0))]


def read_text_file(file_path):
  """读取目标的文本文件, 并替换每一行中的 '\n'

  Args:
    (str) file_path: 目标的文本文件的文件名
  Returns:
    (list) lines: 由目标的文本文件中的每一行所组成的数组
  """
  file_object = open(file_path, 'r')
  lines = []
  try:
    for line in file_object:
      lines.append(line.replace('\n', ''))
  finally:
    file_object.close()
  return lines


def read_text_file_into_floats(file_name):
  """读取目标的文本文件并把里面的数组转换成浮点数, 此目标的文本文件每行只能有一个数.

  Args:
    file_name: 目标的文本文件的文件名
  Returns:
    lines: 由每一行的浮点数所组成的数组
  """
  target_file = open(file_name)
  lines = target_file.readlines()
  # 转换为浮点数
  for i in range(len(lines)):
    lines[i] = float(lines[i].replace('\n', ''))
  target_file.close()
  return lines


def convert_Bps_to_Mbps(array):
  """把 Bps 数组转换为 Mbps 数组

  Args:
    array: Bps 数组输入
  Returns:
    array: Mbps 数组输出
  """
  for i in range(len(array)):
    array[i] = float((array[i] * 8.0) / (1000.0 * 1000.0))
  return array


def get_field_previous_n_second_average_array(intervals, field, n, unit):
  """获取间隔中的目标字段的数据, 并按照每 n 秒一个平均值的格式返回由平均值所组成的数组

  Args:
    intervals: 原始数据中的 intervals 部分
    field: 目标字段
    n: 平均值所包含的数据点个数
    unit: 数据的目标单位
  Returns:
    result: 平均值所组成的数组
  """
  # 数据的初始值为零
  result = [0.0]
  # 平均值点的个数
  averages = float(len(intervals)) / float(n)
  # 当前平均值点序号
  index = 0
  for i in range(int(averages)):
    index += n
    s = 0
    for j in range(index - n, index):
      s += intervals[j]['streams'][0][field]
    result.append(float(s) / float(n) / float(unit))
  return result


def get_n_previous_array(array, N):
  """获取数组中每 N 个元素的平均值

  Args:
    array: 需要采样的数组
    N: 采样周期长度
  return:
    result: 按照指定间隔采样的结果
  """
  result = []
  averages = float(len(array)) / float(N)
  index = 0
  for i in range(int(averages)):
    index += N
    s = 0
    for j in range(index - N, index):
      s += array[j]
    result.append(float(s) / float(N))
  return result


def get_n_previous_sum_array(array, N):
  """获取数组中每 N 个元素的平均值

  Args:
    array: 需要采样的数组
    N: 采样周期长度
  return:
    result: 按照指定间隔采样的结果
  """
  result = []
  averages = float(len(array)) / float(N)
  index = 0
  for i in range(int(averages)):
    index += N
    s = 0
    for j in range(index - N, index):
      s += array[j]
    result.append(float(s))
  return result


def get_field_average(intervals, field, unit):
  """从 intervals 当中获取目标的字段的平均值, 并按要求转换数据的单位

  Args:
    intervals: 原始数据的 intervals 部分
    field: 目标字段
    unit: 目标单位
  Returns:
    转换单位后, 目标字段的平均值
  """
  s = 0.0
  for i in range(len(intervals)):
    s += float(intervals[i]['streams'][0][field])
  s /= float(len(intervals))
  return float(s / unit)


def get_field_array(intervals, field, unit):
  """获取 intervals 当中目标字段的数据数组, 并按要求转换单位

  Args:
    intervals: 原始数据的 intervals 部分
    field: 目标字段
    unit: 目标单位
  Returns:
    result: 转换单位后, 目标字段的数据数组
  """
  result = []
  for i in range(len(intervals)):
    result.append(float(intervals[i]['streams'][0][field]) / float(unit))
  return result


def get_csv_result_with_headers(csv, headers):
  """在有表头的 CSV 文件当中读取数据

  Args:
    csv: 由目标 CSV 文件的每一行所组成的数组
    headers: 表头数组
  Returns:
    data: 一个包含表头中所有字段的数据的字典
  """
  data = {}
  # 创建数据集
  for name in headers:
    data[name] = []
  # 装载数据, 并跳过第一行的表头
  for i in range(1, len(csv)):
    numbers = csv[i].split(',')
    for j in range(len(numbers)):
      data[headers[j]].append(float(numbers[j]))
  return data


def write_array_as_row_in_csv(csv_file, values, separator):
  """
  Use this method to write an array as a single row in given csv file with
  designated separator

  :param csv_file: The pre-opened CSV file instance
  :param values: The values to be wrote as a line
  :param separator: Use this to separate the adjacent values
  """
  list_string = ''
  for i in range(0, len(values)):
    list_string += (str(values[i]) + separator)
  list_string += '\n'
  csv_file.write(list_string)


def get_sum_array(a, b):
  """获取两数组对应各项相加所得和的数组

  Args:
    a: 数组 a
    b: 数组 b
  Returns:
    s: 目标数组
  """
  s = []
  for i in range(len(a)):
    s.append(a[i] + b[i])
  return s


def get_fairness_index(a, b):
  """计算两个数的公平性指数
  """
  return ((a + b) * (a + b)) / (2 * ((a * a) + (b * b)))


def fetch_result(file_name):
  """从目标文件中读取测试数据

  Args:
    file_name: 目标数据文件的路径
  Returns:
    result: 包含转换后的 RTT 与带宽数据数组的字典
  """
  json_object = json.load(open(file_name, 'r'))
  result = {
    'array_rtt': get_field_array(json_object['intervals'], 'rtt', 1000.0),
    'array_mbps': get_field_array(json_object['intervals'],
                                  'bits_per_second', (1000.0 * 1000.0))
  }
  return result


def extend_result_set(result_set, materials):
  """追加 materials 中的 RTT 数组与带宽数组

  Args:
    result_set: 需要被追加数据的结果集
    materials: 追加数据的数据源结果集
  """
  result_set['array_rtt'].extend(materials['array_rtt'][:])
  result_set['array_mbps'].extend(materials['array_mbps'][:])


def getMovingAverage(values, window):
  """计算指定数组的移动平均数

  Args:
    values: 原始数组
    window: 移动平均数的窗口大小
  Returns:
    result: 计算出来的移动平均数
  """
  result = []
  for i in range(window, len(values)):
    result.append(np.average(values[i - window: i]))
  return result


def getPercentage(values, upperBound, lowerBound):
  """计算指定数组中在 upperBound 和 lowerBound 之间的点的占所有点的百分比

  Args:
    values: 点的全集
    upperBound: 上限
    lowerBound: 下限
  Returns:
    符合条件的点的百分比
  """
  count = 0
  for v in values:
    if v <= upperBound and v >= lowerBound:
      count += 1
  return float(count) / float(len(values))


def getFirst(values, upperBound, lowerBound):
  """求第一个在 upperBound 和 lowerBound 之间的点的下标

  Args:
    values: 点的全集
    upperBound: 上限
    lowerBound: 下限
  Returns:
    符合要求的第一个点的下标. 如果没有符合要求的点, 就返回 0.
  """
  for j in range(len(values)):
    if values[j] <= upperBound and values[j] >= lowerBound:
      return j
  return 0
