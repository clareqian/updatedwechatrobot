"""
Clare
2019/07/08
"""


# Set robot
from wxpy import *
import datetime
from threading import Timer
import re
import schedule
import time
import os
import csv

bot=Bot()
bot.cache_path=True
bot.enable_puid('wxpy_puid.pkl')

file_path = "/Users/caixiongfeng/Desktop/wxrobot/file/"




# 在 Web 微信中把自己加为好友
#bot.self.add()
#bot.self.accept()

# 发送消息给自己
#bot.self.send('能收到吗？')



# find target groups, create empty new list to collect @ msgs
# find specific groups and add them to a list company_groups
to_do_lists = []


def add_new_group(msg_chat, group):
    is_already_in = False
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if os.path.splitext(file)[1] == '.csv' and os.path.splitext(file)[0] == group.name:
                is_already_in = True
                msg_chat.send('已含有此群聊')
    if(is_already_in == False):
        print(group.name)
        file_name = file_path + group.name + '.csv'
        to_do_list_head = ['群聊', '序号', '消息内容', '消息状态', '延误天数']
        print("do not have csv")
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            csv_write = csv.writer(f)
            csv_write.writerow(to_do_list_head)
        msg_chat.send('已添加此群聊')
        # f.close()

def add_group(msg_chat, group_name):
    company_groups = bot.groups().search(group_name)
    for company_group in company_groups:
        print("find name: " + company_group.name)
        add_new_group(msg_chat, company_group)
        time.sleep(3)
    if(len(company_groups) == 0):
        msg_chat.send('无此群聊')

# company_groups.append(company_group), add each target group to target groups
# create a new list for each target group and add it to the msg group - to_do_lists.
# for company_group in company_groups:
#     # to_do_lists.append([])
#     print('test add group')
#     add_new_group(company_group)


# a loop for each target group
# if the msg is unaddressed, status=0; else status =1
# for each group, do a loop for each single to_do_list
# if msg_status=1, remove it from to_do_list
def send_daily_news():
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
                    group_chat.send('待办序号: {},  消息内容: {}, 延迟天数: {} '.format(to_do[1], to_do[2], to_do[4]))
                if(index == 1):
                    group_chat.send('无待办事项')
                write_file = csv.writer(open(file_name,'w',encoding='utf-8-sig'))
                write_file.writerow(to_do_list_head)
                write_file.writerows(content)

    # # print(to_do_list)
    # i = 0
    # for company_group in company_groups:
    #     msg_index = 0
    #     for to_do_msg in to_do_lists[i]:
    #         if(to_do_msg['status'] == 1):
    #             to_do_lists[i].remove(to_do_msg)
    #     for to_do_msg in to_do_lists[i]:
    #         msg_index = msg_index + 1
    #         if(to_do_msg['status'] == 0):
    #             company_group.send('待办序号: {},  消息内容: {} '.format(msg_index, to_do_msg['txt']))
    #             to_do_lists[i][msg_index - 1]['num'] = to_do_lists[i][msg_index - 1]['num'] + 1
    #     i = i + 1
    #     time.sleep(2)


def send_delay_news():
    global to_do_lists
    # print(to_do_list)
#     i = 0
#     for company_group in company_groups:
#         msg_index = 0
#         for to_do_msg in to_do_lists[i]:
#             if(to_do_msg['status'] == 1):
#                 to_do_lists[i].remove(to_do_msg)
#         for to_do_msg in to_do_lists[i]:
#             msg_index = msg_index + 1
#             if(to_do_msg['status'] == 0 and to_do_msg['num'] > 1):
#                 company_group.send('延误！ 待办序号: {},  延误天数: {}, 消息内容: {} '.format(msg_index, to_do_msg['num']-1, to_do_msg['txt']))
# #            if(to_do_msg['status'] == 0 and to_do_msg['num'] == 1):
# #                company_group.send('待办序号: {},  消息内容: {} '.format(msg_index, to_do_msg['txt']))
#         i = i + 1
#         time.sleep(2)
    # t = Timer(10, send_news)
    # t.start()

def send_all_list(chat_from):
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
                    msg_num = msg_num + 1
                    # chat_from.send('群聊: {}, 待办序号: {},  消息内容: {} '.format(line[0], line[1], line[2]))
                    if(line[3] == '0'):
                        chat_from.send('群聊: {}, 待办序号: {},  消息内容: {} '.format(line[0], line[1], line[2]))
                if(msg_num == 0):
                    chat_from.send('群聊: {}, 无待办消息 '.format(group_name))

            # csv_file.close()


def send_group_list(chat_from):
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
                        chat_from.send('群聊: {}, 待办序号: {},  消息内容: {} '.format(line[0], line[1], line[2]))
                        msg_num = msg_num + 1
                chat_from.send('无待办消息 ')
                    # content.append(line)
                    # print(line[3])
                    # chat_from.send('待办序号: {},  消息内容: {} '.format(line[1], line[2]))
                    
            # csv_file.close()

def add_group_to_do(chat_group, msg_text):
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


def delete_group_to_do(chat_group, msg_text):
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
        print("add to do")
        add_group_to_do(msg.chat, msg.text)
    
    if not isinstance(msg.chat, Group) and ('request' in msg.text or 'Request' in msg.text):
        print("request all todo")
        send_all_list(msg.chat)
    
    if isinstance(msg.chat, Group) and ('request' in msg.text or 'Request' in msg.text):
        print("request group todo")
        send_group_list(msg.chat)

    if isinstance(msg.chat, Group) and ('Ad' in msg.text or 'ad' in msg.text) and msg.is_at:
        print("delete group todo")
        delete_group_to_do(msg.chat, msg.text)


    # list_index = company_groups.index(msg.chat)
    # if('@' in msg.text and msg.sender != bot.self and not msg.is_at):
    #     to_do_msg = {'txt':msg.text, 'status':0, 'num':1}
    #     to_do_lists[list_index].append(to_do_msg)
    # if(('Ad' in msg.text or 'ad' in msg.text) and msg.is_at):
    #     num_list = re.findall("\d+", msg.text)
    #     num = 0
    #     if(len(num_list) >= 1):
    #         num = int(num_list[0])
    #     if((num <= len(to_do_lists[list_index])) and (num >= 1)):
    #         to_do_lists[list_index][num - 1]['status'] = 1

# check each msg received
# if it is an @ msg and it does not @ the bot, make it a to_do_msg and add it to to_do_list
# if it is an @ msg and it @ the bot and it is in the format "ad #", the corresponding to_do_msg's status is changed to 1
# @bot.register(company_groups, TEXT)
# def process_message(msg):
#     global to_do_lists
#     list_index = company_groups.index(msg.chat)
#     if('@' in msg.text and msg.sender != bot.self and not msg.is_at):
#         to_do_msg = {'txt':msg.text, 'status':0, 'num':1}
#         to_do_lists[list_index].append(to_do_msg)
#     if(('Ad' in msg.text or 'ad' in msg.text) and msg.is_at):
#         num_list = re.findall("\d+", msg.text)
#         num = 0
#         if(len(num_list) >= 1):
#             num = int(num_list[0])
#         if((num <= len(to_do_lists[list_index])) and (num >= 1)):
#             to_do_lists[list_index][num - 1]['status'] = 1
#                 # to_do_list.remove(to_do_list[num - 1])


# schedule a time when the bot should do send_news() or send_delay_news()
def on_time_send_news():
    # when using the bot, uncomment the following two lines
    # schedule.every().day.at("09:30").do(send_news)
    # schedule.every().day.at("13:30").do(send_delay_news)

    # the following two lines are for testing
    schedule.every(1).minutes.do(send_daily_news)
    schedule.every(1).minutes.do(send_delay_news)
    while True:
        schedule.run_pending()
        time.sleep(2)



if __name__ == "__main__":
    on_time_send_news()
