import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import  filedialog
import os
from datetime import datetime
from tkinter import messagebox
import csv
import can
import threading
# pyinstaller --onefile --noconsole --icon=E:\python\blf2csv\ic.ico ttk.py


def time_to_seconds(time_str):
    # Split the time string into hours, minutes, seconds, and milliseconds
    time_parts = time_str.split(':')
    hours = int(time_parts[0])
    minutes = int(time_parts[1])
    seconds, milliseconds,_ = map(float, time_parts[2].split('.'))

    # Convert hours, minutes, and seconds to seconds
    total_seconds = hours * 3600 + minutes * 60 + seconds

    # Add milliseconds as fraction of a second
    total_seconds += milliseconds / 1000.0

    return total_seconds


def csv_to_blf(csv_filename, blf_filename):
    # Open the CSV file for reading
    with open(csv_filename, 'r') as csv_file:
        # Create a CSV reader
        csv_reader = csv.reader(csv_file)



        # Create a new BLF file
        with open(blf_filename, 'wb') as blf_file:
            blf_writer = can.BLFWriter(blf_file)
            # Iterate over each row in the CSV file
            count=0
            for row in csv_reader:
                if count==0:
                    count += 1
                    continue
                timeTemp='2024-05-25 '+row[2]
                timestamp =datetime.timestamp(datetime.strptime(timeTemp[:-2], "%Y-%m-%d %H:%M:%S.%f"))
                message_id = int(row[3],16)
                # data = int(row[3],16)
                data =bytes.fromhex(row[7])
                dlc =int(row[6],16)

                # Create a new CAN message
                message = can.Message(arbitration_id=message_id, data=data, timestamp=timestamp,channel=0,dlc=dlc)

                # Write the message to the BLF file
                blf_writer.on_message_received(message)
            # Close the BLF file
            blf_writer.stop()


def text_to_blf(text_filename,blf_filename):
    with open(text_filename) as f:
        text_line=f.readlines()[12:-1]
#     处理文本数据
    for index,tx in enumerate(text_line):
        text_line[index]=tx.replace('\n','').split(' ')
    with open(blf_filename, 'wb') as blf_file:
        blf_writer = can.BLFWriter(blf_file)
        for item in text_line:

            # 12:16:21.548.0
            #Message ID
            # item[0]
            # Cycle time in ms
            # item[6]
            # Data length
            # item[8]
            # Frame type
            # item[10]
            # data
            # item[11:19].join(' ')

            timeTemp = '2024-05-25 12:16:21.548.0'
            timestamp = datetime.timestamp(datetime.strptime(timeTemp[:-2], "%Y-%m-%d %H:%M:%S.%f"))
            message_id = int(item[0].replace('h',""), 16)
            data = bytes.fromhex(' '.join(item[11:19]).replace("h",""))
            dlc = int(item[8])

            # Create a new CAN message
            message = can.Message(arbitration_id=message_id, data=data, timestamp=timestamp, channel=0, dlc=dlc)

            # Write the message to the BLF file
            blf_writer.on_message_received(message)
        blf_writer.stop()

    print("处理后数据",text_line)
def clear_table_files():
    # 删除所有表格项
    for item in tree.get_children():
        tree.delete(item)
def populate_tree(tree, files):
    # 清空表格
    tree.delete(*tree.get_children())
    # 添加文件信息
    for idx, file_info in enumerate(files, 1):
        file_name, file_size, modified_time = file_info
        tree.insert("", "end", text=str(idx), values=(file_name, file_size, modified_time))


def browse_files():
    # 打开文件选择对话框
    files = filedialog.askopenfilenames(title="Select CSV Files",
                                        filetypes=(("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")))
    global files_path_list
    files_path_list=files
    if files:
        file_info_list = []
        for file_path in files:
            # 获取文件名
            file_name = os.path.basename(file_path)
            # 获取文件大小
            file_size = str(round(float(os.path.getsize(file_path))/1024/1024,2))+'M'
            # 获取文件修改日期
            modified_time = os.path.getmtime(file_path)
            modified_time = datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d %H:%M:%S")
            file_info_list.append((file_name, file_size, modified_time))

        # 更新表格数据
        populate_tree(tree, file_info_list)
# 开始任务
def start_worker(use_type):
    # 禁用按钮
    b2.config(state="disabled")
    for file_path in files_path_list:
        file_name = os.path.basename(file_path)
        file_path_full = os.path.split(file_path)
        csv_filename = file_path  # Input CSV file
        # blf_filename = file_path_full[0]+r'/create_csv2blf/'+ file_name.replace('.csv','.blf') # Output BLF file
        if use_type == 1:
            blf_filename = os.getcwd() + r'/create_csv2blf/' + file_name.replace('.csv', '.blf')  # Output BLF file
            csv_to_blf(csv_filename, blf_filename)
        elif use_type==2:
            blf_filename = os.getcwd() + r'/create_csv2blf/' + file_name.replace('.txt', '.blf')  # Output BLF file
            text_to_blf(csv_filename, blf_filename)
    # 启用按钮
    b2.config(state="enabled")
    messagebox.showinfo("完成", "文件已经全部转换为blf格式，请在create_csv2blf文件夹下查看")
def start_csv_to_blf():
    if len(files_path_list)==0:
        messagebox.showinfo("提示", "请先选择文件！")
        return True
    try:
        threading.Thread(target=start_worker,args=(1,)).start()
    except Exception as e:
        # 启用按钮
        b2.config(state="enabled")
        messagebox.showerror("文件转换异常,请联系开发者", str(e))


def start_text_to_blf():
    if len(files_path_list)==0:
        messagebox.showinfo("提示", "请先选择文件！")
        return True
    try:
        threading.Thread(target=start_worker,args=(2,)).start()
    except Exception as e:
        # 启用按钮
        b2.config(state="enabled")
        messagebox.showerror("文件转换异常,请联系开发者", str(e))


STARTSTATUS=True
root = ttk.Window(title="two white 格式转换工具")
# 设置窗口图标
# root.iconbitmap("E:/python/blf2csv/ic.ico")

# 获取屏幕宽度和高度
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# 计算窗口的位置
window_width = 0.38
window_height = 0.4

x = int((screen_width - (screen_width * window_width)) / 2)
y = int((screen_height - (screen_height * window_height)) / 2)
root.geometry(f"{int(screen_width * window_width)}x{int(screen_height * window_height)}+{x}+{y}")
# 禁止用户改变窗口大小
root.resizable(False, False)

files_path_list=[]


# 在 path 这个路径下创建一个新的 file1 文件夹
try:
    os.mkdir(os.getcwd() + './create_csv2blf')
except Exception as e:

    pass




# 创建带有样式的 Treeview
tree = ttk.Treeview(root, style="table.Treeview")
# 添加表头
tree["columns"] = ("Name", "Size", "Modified")
tree.heading("#0", text="序号")
tree.heading("Name", text="文件名")
tree.heading("Size", text="大小")
tree.heading("Modified", text="修改日期")
tree.column("#0", width=80, anchor="w")  # 设置序号列宽度为 50


# 填充表格数据
# populate_tree(tree)

# 调整列宽
for index,column in enumerate(tree["columns"]) :
    tree.column(column, width=200, anchor="w")

# 将表格放置在窗口中
tree.grid(row=0,column=0,rowspan=5,columnspan=10)


b1 = ttk.Button(root, text="选择文件", bootstyle=SUCCESS, command=browse_files, width=20)
b1.grid(row=8,column=0,padx=10,pady=20)

b2 = ttk.Button(root, text="CSV转blf", bootstyle=PRIMARY,command=start_csv_to_blf, width=20)
b2.grid(row=8,column=1,padx=10,pady=20)



b3 = ttk.Button(root, text="重置文件", bootstyle=DARK,command=clear_table_files, width=12)
b3.grid(row=8,column=2,padx=10,pady=20)

b4 = ttk.Button(root, text="TXT转blf", bootstyle=PRIMARY,command=start_text_to_blf, width=20)
b4.grid(row=9,column=1,padx=10,pady=5)
#
# b2 = ttk.Button(root, text="Button 2", bootstyle=(INFO, OUTLINE))
# b2.grid(row=0,column=1)


root.mainloop()