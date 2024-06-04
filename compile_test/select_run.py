# This function is to select files which can be compiled and run.
# text_name is the generated dataset, which is a .txt as input
# output: .C files like files in the example folder
# Note: header.c header.h must be linked when compile

import os
import shutil


def screen():                                    		# 函数功能为：筛选出文件夹下所有后缀名为.txt的文件
    path = './'         	# 文件夹地址
    # txt_list = []										# 创建一个空列表用于存放文件夹下所有后缀为.txt的文件名称
    file_list = os.listdir(path)                   	 	# 获取path文件夹下的所有文件，并生成列表
    for i in file_list:
        file_ext = os.path.splitext(i)              	# 分离文件前后缀，front为前缀名，ext为后缀名
        front, ext = file_ext							# 将前后缀分别赋予front和ext

        if ext == '.txt':                          		# 判断如果后缀名为.txt则将该文件名添加到txt_list的列表当中去
            return i

def select_files(text_name=''):
    f = open(text_name)
    line = f.readline()
    flag=0
    name=0
    num_all=0
    if os.path.exists('test.txt'):
        os.remove('test.txt')
    if os.path.exists('a.out'):
        os.remove('a.out')
    if os.path.exists('test.c'):
        os.remove('test.c')
    while line:
        line = f.readline()
        if line == '#include "header.h"\n':
            f1 = open('./test.txt', 'a')
            f1.write(str(line))
            f1.close()
            flag=1
            continue
        if line !='\n' and flag == 1:
            f1 = open('./test.txt', 'a')
            f1.write(str(line))
            f1.close()
            continue
        if flag==0 or flag==1 and line =='\n':
            flag=2
            continue
        if flag==2 and line =='\n':
            flag=0
            num_all=num_all+1
            # try:
            if os.path.exists('test.txt'):
                os.rename('test.txt','test.c')
                v_return_status = os.system('gcc test.c header.c -I.') # Note: header.c header.h must be linked when compile use -I
                if v_return_status == 0:
                    v_return_status = os.system('./a.out')
                    if v_return_status == 0:
                        name=name+1
                        os.rename('test.c', str(name)+'.c')
                        shutil.move(str(name)+'.c', 'example/'+str(name)+'.c')

            if os.path.exists('a.out'):
                os.remove('a.out')
            if os.path.exists('test.c'):
                os.remove('test.c')
    if os.path.exists('a.out'):
        os.remove('a.out')
    if os.path.exists('test.c'):
        os.remove('test.c')
    print("success rate:", name/num_all)
    f.close()

if __name__ == '__main__':
    txt_name=screen()
    select_files(txt_name)