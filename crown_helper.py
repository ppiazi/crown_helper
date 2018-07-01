# -*- coding: utf-8 -*-
import subprocess
import os
import sys
import time
import datetime
import shutil

essential_file_list = ["branches", "cfg", "cfg_branches", "cfg_func_map", "funcount", "idcount", "input", "stmtcount"]

class CrownExeHelper:
    def __init__(self):
        self.proc_list = {}
        self.workspace_list = {}
        self.file_list = {}
        #self.strategy_list = ['-dfs', '-cfg', '-hybrid', '-random']
        self.strategy_list = ['-dfs', '-cfg', '-hybrid', '-random']

    def init_workspace(self, dir, cmd, iteration):
        print("Copying directories...")
        for st in self.strategy_list:
            ts = time.time()
            new_folder = dir + st + datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M:%S')
            print("\tCopying %s" % new_folder)
            shutil.copytree(target, new_folder)
            self.workspace_list[st] = new_folder

    def run_crown(self, cmd, iteration, strategy):
        cwd_str = self.workspace_list[strategy]
        cmd_str = "Starting %s %d %s at %s" % (cmd, iteration, strategy, cwd_str)
        print(cmd_str)
        output_file = open(cmd + strategy + ".result.txt", "wb")
        proc = subprocess.Popen(['run_crown', cmd, str(iteration), strategy], stdout=output_file, stderr=output_file, cwd=cwd_str)
        self.proc_list[strategy] = (proc, cmd_str)
        self.file_list[strategy] = output_file

    def start(self, cmd, iteration):
        for st in self.strategy_list:
            self.run_crown(cmd, iter, st)
        
        run_flag = {}
        for k in self.strategy_list:
            run_flag[k] = True

        while True:
            for proc_st in self.proc_list.keys():
                proc_handle = self.proc_list[proc_st][0]
                proc_cmd_str = self.proc_list[proc_st][1]
                if run_flag[proc_st] == True and proc_handle.poll() != None:
                    print("Finished %s" % (proc_cmd_str))
                    self.file_list[proc_st].flush()
                    self.file_list[proc_st].close()
                    run_flag[proc_st] = False

            exit_flag = True
            for k in run_flag.keys():
                if run_flag[k] == True:
                    exit_flag = False
            if exit_flag == True:
                break

            time.sleep(1)

if __name__ == "__main__":
    target = sys.argv[1]
    cmd = sys.argv[2]
    iter = int(sys.argv[3])

    ceh = CrownExeHelper()

    ceh.init_workspace(target, cmd, iter)
    ceh.start(cmd, iter)
