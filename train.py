#!/usr/bin/python3
# coding: utf-8


import datetime
import getopt
import json
import os
import re
import requests
import sendmail
import sys


LOCAL_LIST_NAME = 'stations'
DISPLAY_IN_TABLE = True

STATION_LIST_UPDATED = False


# 返回当天日期(YYYYMMDD)
def get_today_date():

    this_year = str(datetime.datetime.today().year)
    this_month = str(datetime.datetime.today().month).zfill(2)
    this_day = str(datetime.datetime.today().day).zfill(2)

    return this_year + this_month + this_day


# 返回当前版本的 staion 列表文件名
def get_current_station_list_name():

    def get_list_name(name):
        if name.startswith(LOCAL_LIST_NAME):
            return True

    current_station_list_name = list(filter(get_list_name, list(os.popen('ls'))))[0].rstrip()
    return current_station_list_name


# 检测是否需要更新 station 列表文件，有必要时更新
def update_station_list():

    url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'

    raw_js = requests.get(url, verify=False).text
    # 去除原始文本中开头的一些无关字符
    content = raw_js.split('\'')[1]
    stations = content.split('@')[1:]
    
    current_list_name = get_current_station_list_name()
    local_station_list = list(line.rstrip() for line in open(current_list_name))

    if stations != local_station_list:
        newlist = '\n'.join(stations)
        open(current_list_name, 'w').write(newlist)
        os.rename(current_list_name, LOCAL_LIST_NAME + get_today_date())
        global STATION_LIST_UPDATED
        STATION_LIST_UPDATED = True


# 车站名转为三字车站代码
def station_code_to_name(code):
    
    stations = open(get_current_station_list_name()).readlines()
    for station in stations:
        if code == station.split('|')[2]:
            return station.split('|')[1]
    
    return None


# 三字车站代码转为车站名
def station_name_to_code(name):
    
    stations = open(get_current_station_list_name()).readlines()
    for station in stations:
        if name == station.split('|')[1]:
            return station.split('|')[2]
    
    return None


# 按照日期、起止站查询，返回原始 JSON 
def train_query(train_date, from_station, to_station):
    
    url = 'https://kyfw.12306.cn/otn/leftTicket/query'
    qkeys = ['leftTicketDTO.train_date', 'leftTicketDTO.from_station', 'leftTicketDTO.to_station', 'purpose_codes']
    qvals = [train_date, from_station, to_station, 'ADULT']
    
    # GET 参数的顺序必须固定不能改变……
    url += '?'
    for i in range(len(qkeys)):
        url += qkeys[i] + '=' + qvals[i] + '&'
    url = url[:-1]
    raw_result = requests.get(url, verify=False).text
    
    return raw_result


# 查询结果的原始 JSON 解析为列表
def train_parse(raw_json):
    
    j = json.loads(raw_json)
    if 'data' not in j.keys():
        for m in j['messages']:
            print(m)
        exit()
    else:
        train_data = j['data']['result']
    
    train_lists = []
    for i in train_data:
        datas = i.split('|')
        train = {
            '按键': datas[1], 
            '编号': datas[2],
            '车次': datas[3],
            '始发': datas[4],
            '终到': datas[5],
            '出发': datas[6],
            '到达': datas[7],
            '发时': datas[8],
            '达时': datas[9],
            '历时': datas[10],
            '始日': datas[13],
            '高软': datas[21],
            '软卧': datas[23],
            '硬卧': datas[26],
            '软座': datas[27],
            '硬座': datas[28],
            '无座': datas[29],
            '二等': datas[30],
            '一等': datas[31],
            '商务': datas[32],
        }
        # 对于某些车次不售的票，不建立键值
        to_del = []
        for item in train:
            if train[item] == '':
                to_del.append(item)
        for i in to_del:
            del train[i]
        train_lists.append(train)
        
    return train_lists


# 根据某一字段对结果进行排序
def sort_data(data_list, sort_key, desc=False):

    for item in data_list:
        if sort_key not in item.keys():
            print('Lack of key.')
            exit()
    data_list.sort(key=lambda x:x[sort_key])
    if desc is True:
       data_list.reverse()

    return data_list


# 对结果进行筛选
def filt_data(data_list, filt):

    possible_train_title = ['K', 'T', 'Z', 'C', 'D', 'G', 'Y', 'L', 'S']
    filt_list = list(filt.upper())

    for item in filt_list:
        if item not in possible_train_title:
            print('Filter "{0}" not available'.format(item))
            exit()

    def filt_func(train):
        if train['车次'][:1] in filt_list:
            return True
    
    return list(filter(filt_func, data_list))


# 数据解析后转为易读的结果
def display_data(parsed, is_email):
    
    ticket_types = ['商务', '一等', '二等', '高软', '软卧', '硬卧', '软座', '硬座', '无座']

    if DISPLAY_IN_TABLE and not is_email:
        from prettytable import PrettyTable
        table_head = ['车次', '始发', '出发', '到达', '终到', '发时', '达时', '历时']
        full_table_head = table_head + ticket_types
        for train in parsed:
            for key in train.keys():
                if key in ticket_types:
                    table_head.append(key)
        table_head = list(set(table_head))
        table_head.sort(key=lambda x:full_table_head.index(x))
        pt = PrettyTable(table_head)
        for train in parsed:
            table_row = []
            for field in table_head:
                if field in train.keys():
                    if field in ['始发', '出发', '到达', '终到']:
                        table_row.append(station_code_to_name(train[field]))
                    else:
                        table_row.append(train[field])
                else:
                    table_row.append('')
            pt.add_row(table_row)
        print(pt)
        if STATION_LIST_UPDATED:
            print('Station List has been updated.')
    else:
        train_display = []
        for train in parsed:
            train_string = train['车次'] + ': '
            if train['始发'] == train['出发']:
                train_string += '[{0}]--'.format(station_code_to_name(train['始发']))
            else:
                train_string += '{0}--[{1}]--'.format(station_code_to_name(train['始发']), station_code_to_name(train['出发']))
            if train['终到'] == train['到达']:
                train_string += '[{0}]'.format(station_code_to_name(train['终到']))
            else:
                train_string += '[{0}]--{1}'.format(station_code_to_name(train['到达']), station_code_to_name(train['终到']))
            train_string += '  '
            train_string += '{0}--{1}({2})'.format(train['发时'], train['达时'], train['历时'])
            train_string += '  '
            for ticket in ticket_types:
                if ticket in train.keys():
                    train_string += train[ticket] + ticket
                    train_string += ' '
            train_display.append(train_string)
        outputString = ''
        if is_email:
            for item in train_display:
                outputString += item + '<br>'
            sendmail.sendEmail('余票情况', outputString)
            print('邮件已发送')
        else:
            for item in train_display:
                outputString += item + '\n'
            print(outputString)
            if STATION_LIST_UPDATED:
                print('Station List has been updated.')
            

# 获取命令行参数
def get_options():
    
    options, args = getopt.getopt(sys.argv[1:], 'd:f:t:s:', longopts=['date=', 'from=', 'to=', 'sort=', 'desc', 'filter=', 'email'])
    
    options_dict = {}
    for name, value in options:
        if name in ['-d', '--date']:
            options_dict['date'] = value
        if name in ['-f', '--from']:
            options_dict['from'] = value
        if name in ['-t', '--to']:
            options_dict['to'] = value
        if name in ['-s', '--sort']:
            options_dict['sort'] = value
        if name in ['--desc']:
            options_dict['desc'] = True
        if name in ['--filter']:
            options_dict['filter'] = value
        if name in ['--email']:
            options_dict['email'] = True

    return options_dict


# 处理命令行参数
def dispose_options(options):
    
    for item in ['date', 'from', 'to']:
        if item not in options.keys():
            print('Lack of necessary option(s).')
            exit()

    disposed_options = options
    if len(re.findall('\d{8}', options['date'])) > 0:
        disposed_options['date'] = options['date'][:4] + '-' + options['date'][4:6] + '-' + options['date'][6:]
    if len(re.findall('[A-Z]{3}', options['from'])) == 0:
        disposed_options['from'] = station_name_to_code(options['from'])
    if len(re.findall('[A-Z]{3}', options['to'])) == 0:
        disposed_options['to'] = station_name_to_code(options['to'])

    return disposed_options
    

# 处理查询结果
def dispose_result(raw_result, options):

    parsed_result = train_parse(raw_result)
    if 'filter' in options:
        filted_result = filt_data(parsed_result, options['filter'])
    else:
        filted_result = parsed_result
    if 'sort' in options:
        sorted_result = sort_data(filted_result, options['sort'], desc=True if 'desc' in options.keys() else False)
    else:
        sorted_result = filted_result
    final_result = filted_result

    return final_result    


def run():
    options = get_options()
    update_station_list()
    options = dispose_options(options)
    query_result = train_query(options['date'], options['from'], options['to'])
    disposed_result = dispose_result(query_result, options)
    display_data(disposed_result, is_email=('email' in options.keys()))
    

if __name__ == '__main__':
    run()
