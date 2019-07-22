"""
Clare
2019/07/17
"""

from wxpy import *
import datetime
from threading import Timer
import re
import schedule
import time
import os
import csv

# Set robot
# Change the path before using
bot=Bot()
bot.cache_path=True
bot.enable_puid('wxpy_puid.pkl')
file_path = "/Users/qianxinxuan/Desktop/wxrobot/file/"

# Functions!

# send "add 群聊名称" to the robot to add that group chat to the list.
# if the group chat can be found in the account of robot, call add_new_group()
# else, call add_group()
def add_new_group(msg_chat, group):
    """
    go through all csv files in the folder, if the group chat is already in the folder,
    send "已含有". Else, create a new csv for that group chat and write 5 columns, return "已添加".
    """
    is_already_in = False
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if os.path.splitext(file)[1] == '.csv' and os.path.splitext(file)[0] == group.name:
                is_already_in = True
                msg_chat.send('提醒列表中已含有此群聊')
    if(is_already_in == False):
        print(group.name)
        file_name = file_path + group.name + '.csv'
        to_do_list_head = ['群聊', '序号', '消息内容', '消息状态', '延误天数']
        print("do not have csv")
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            csv_write = csv.writer(f)
            csv_write.writerow(to_do_list_head)
        msg_chat.send('已向提醒列表中添加此群聊')
        # f.close()

def add_group(msg_chat, group_name):
    """
    if the group chat cannot be found in the robot account, call this function
    and return "找不到", else call add_new_group()
    """
    company_groups = bot.groups().search(group_name)
    for company_group in company_groups:
        print("find name: " + company_group.name)
        add_new_group(msg_chat, company_group)
        time.sleep(3)
    if(len(company_groups) == 0):
        msg_chat.send('查找不到此群聊（可能刚建群未更新，可能名字输入错误）')

# send "delete 群聊名称" to the robot, the group chat will be removed from the notification list
def delete_group(msg_chat, group_name):
    """
    go through all csv files in the foler, if the group chat can be found, delete
    the file to remove it and return "成功移除", else return “找不到”.
    """
    have_group = False
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if(group_name in file and 'csv' in file):
                os.remove(file_path + file)
                have_group = True
                msg_chat.send('已从提醒列表中移除此群聊')
    if(have_group == False):
        msg_chat.send('查找不到此群聊（可能刚建群未更新，可能名字输入错误）')

# send notifications at 09:30 every day to inform unaddressed msgs.
def send_daily_news():
    """
    go through all csv files in the folder (if there are any). For each file, send
    each line as a wechat msg to that group chat. If there is no unaddressed msg, send
    "无待办事项".
    """
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if('csv' in file):
                group_name = file.split(".", 1)[0]
                file_name = file_path + file
                print(group_name)
                group_chats = bot.groups().search(group_name)
                if(len(group_chats) == 0):
                    continue
                group_chat = ensure_one(bot.groups().search(group_name))
                content = []
                print(file_name)
                csv_file=csv.reader(open(file_name,'r'))
                print(csv_file)
                to_do_list_head = ['群聊', '序号', '消息内容', '消息状态', '延误天数']
                index = 1;
                for line in csv_file:
                    print(line)
                    # chat_from.send('群聊: {}, 待办序号: {},  消息内容: {} '.format(line[0], line[1], line[2]))
                    if(line[3] == '0'):
                        line[1] = index
                        line[4] = int(line[4]) + 1
                        content.append(line)
                        index = index + 1
                for to_do in content:
                    group_chat.send('序号: {},  消息内容: {}, 延误天数: {} '.format(to_do[1], to_do[2], to_do[4]))
                if(index == 1):
                    group_chat.send('无待办事项')
                write_file = csv.writer(open(file_name,'w',encoding='utf-8-sig'))
                write_file.writerow(to_do_list_head)
                write_file.writerows(content)

# send delay unaddressed msgs at 13：30 every day.
def send_delay_news():
    """
    go through each csv in the folder, if "延误天数" >1, regard it as delayed and
    send notifications in the corresponding group chat.
    """
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if('csv' in file):
                group_name = file.split(".", 1)[0]
                file_name = file_path + file
                print(group_name)
                group_chats = bot.groups().search(group_name)
                if(len(group_chats) == 0):
                    continue
                group_chat = ensure_one(bot.groups().search(group_name))
                content = []
                print(file_name)
                csv_file=csv.reader(open(file_name,'r'))
                print(csv_file)
                to_do_list_head = ['群聊', '序号', '消息内容', '消息状态', '延误天数']
                index = 1;
                for line in csv_file:
                    print(line)
                    # chat_from.send('群聊: {}, 待办序号: {},  消息内容: {} '.format(line[0], line[1], line[2]))
                    if(line[3] == '0' and int(line[4]) > 1):
                        content.append(line)
                for to_do in content:
                    group_chat.send('延误！ 序号: {},  消息内容: {}, 延误天数: {} '.format(to_do[1], to_do[2], to_do[4]))

# send "request" to the robot to get all current unaddressed msgs
def send_all_list(chat_from):
    """
    go through each csv file and each line in the file, return all unaddressed msgs
    """
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if('csv' in file):
                file_name = file_path + file
                group_name = file.split(".", 1)[0]
                print(file_name)
                csv_file=csv.reader(open(file_name,'r'))
                print(csv_file)
                msg_num = 0
                for line in csv_file:
                    # content.append(line)
                    print(line)
                    if(line[3] == '0'):
                        chat_from.send('群聊: {}, 序号: {},  消息内容: {} '.format(line[0], line[1], line[2]))
                        msg_num = msg_num + 1
                if(msg_num == 0):
                    chat_from.send('群聊: {}, 无待办事项 '.format(group_name))
            # csv_file.close()

# send "request" to the group chat to get all current unaddressed msgs in that group chat
def send_group_list(chat_from):
    """
    go through all csv files to find the correct file. go through all lines and send them
    as unaddressed msgs to that group chat
    """
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if('csv' in file and chat_from.name in file):
                file_name = file_path + file
                print(file_name)
                csv_file=csv.reader(open(file_name,'r'))
                print(csv_file)
                msg_num = 0
                for line in csv_file:
                    if(line[3] == '0'):
                        chat_from.send('群聊: {}, 序号: {},  消息内容: {} '.format(line[0], line[1], line[2]))
                        msg_num = msg_num + 1
                if(msg_num == 0):
                    chat_from.send('无待办事项 ')
                    # content.append(line)
                    # print(line[3])
                    # chat_from.send('待办序号: {},  消息内容: {} '.format(line[1], line[2]))
            # csv_file.close()

# add a new @ msg to the to_do_list by writing in the corresponding csv file
def add_group_to_do(chat_group, msg_text):
    """
    go through all the csv files in the folder to find the group chat where the msg
    is received. write the msg in that csv file.
    """
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if(file == chat_group.name + '.csv'):
                print("find group name")
                file_name = file_path + file
                print(file_name)
                print(msg_text)
                csv_file=csv.reader(open(file_name,'r'))
                print(csv_file)
                list_index = 0
                for row in csv_file:
                    list_index = list_index + 1
                print(list_index)
                # read_file.close()
                #['群聊', '序号', '消息内容', '消息状态', '延误天数']
                msg_info = [chat_group.name, list_index, msg_text, 0, 0]
                print(msg_info)
                write_file = csv.writer(open(file_name,'a',encoding='utf-8-sig'))
                write_file.writerow(msg_info)
                # write_file.close()

# send "ad #" and @ the robot to mark the msg as "addressed" and remove it from to_do_list
def delete_group_to_do(chat_group, msg_text):
    """
    go through all the csv files to find the correct group chat, find the # after "ad",
    modify the status of the corresponding msg to 1, in order to delete it when send_daily_news()
    is called.
    """
    num_list = re.findall("\d+", msg_text)
    to_do_index = 0
    if(len(num_list) >= 1):
        to_do_index = int(num_list[0])
    content = []
    print(to_do_index)
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if('csv' in file and chat_group.name in file):
                file_name = file_path + file
                print(file_name)
                print("find group name")
                read_file = csv.reader(open(file_name,'r'))
                for line in read_file:
                    content.append(line)
                print(to_do_index)
                if(to_do_index > 0 and to_do_index < len(content)):
                    content[to_do_index][3] = 1
                write_file = csv.writer(open(file_name,'w',encoding='utf-8-sig'))
                write_file.writerows(content)
                # #['群聊', '序号', '消息内容', '消息状态', '延误天数']
                # msg_info = [chat_group, list_index, msg_text, 0, 0]
                # write_file = csv.writer(open(file_name,'a'))
                # write_file.writerow(msg_info)
                # write_file.close()

# 线程
@bot.register()
def process_message(msg):
    # global to_do_lists
    # # group chat
    # # indivitual request
    # # add groups
    # if('request' in msg.text):
    #     send_all_list(msg.chat)
    # and ('add' in msg.text or 'Add' in msg.text)
    if not isinstance(msg.chat, Group) and msg.receiver == bot.self and ('Add' in msg.text or 'add' in msg.text):
        group_msg_list_ = msg.text.split(" ", 1)
        if(len(group_msg_list_) > 1):
            group_name = group_msg_list_[1]
            print(group_name)
            add_group(msg.chat, group_name)

    if isinstance(msg.chat, Group) and '@' in msg.text and msg.sender != bot.self and not msg.is_at:
        print("add todo")
        add_group_to_do(msg.chat, msg.text)

    if not isinstance(msg.chat, Group) and ('request' in msg.text or 'Request' in msg.text):
        print("request all todo")
        send_all_list(msg.chat)

    if isinstance(msg.chat, Group) and ('request' in msg.text or 'Request' in msg.text):
        print("request group todo")
        send_group_list(msg.chat)

    if isinstance(msg.chat, Group) and ('Address' in msg.text or 'address' in msg.text) and msg.is_at:
        print("delete group todo")
        delete_group_to_do(msg.chat, msg.text)

    if not isinstance(msg.chat, Group) and msg.receiver == bot.self and ('Delete' in msg.text or 'delete' in msg.text):
        group_msg_list_ = msg.text.split(" ", 1)
        if(len(group_msg_list_) > 1):
            group_name = group_msg_list_[1]
            print(group_name)
            delete_group(msg.chat, group_name)

# schedule a time when the bot should do send_daily_news() or send_delay_news()
def on_time_send_news():
    # when using the bot, uncomment the following two lines
    schedule.every().day.at("09:30").do(send_daily_news)
    schedule.every().day.at("13:30").do(send_delay_news)
    # the following two lines are for testing
    # schedule.every(2).minutes.do(send_daily_news)
    # schedule.every(2).minutes.do(send_delay_news)
    while True:
        schedule.run_pending()
        time.sleep(2)

if __name__ == "__main__":
    on_time_send_news()
