#! /usr/bin/env python3
import argparse
import os
import pathlib
import re
import typing
from datetime import datetime, timedelta
from signal import SIGHUP, SIGINT, SIGTERM, signal
from time import sleep

from pyecharts import options as opts
from pyecharts.charts import Line, Page


class SpendingChart(object):

    def __init__(self, title:str) -> None:
        self.lineChart = Line()
        titleOpts = opts.TitleOpts(title=title)
        xaxisOpts = opts.AxisOpts(type_="time")
        yaxisOpts = opts.AxisOpts(type_="value")
        tooltipOpts = opts.TooltipOpts(trigger="axis")
        self.lineChart.set_global_opts(
            title_opts=titleOpts,
            xaxis_opts=xaxisOpts,
            yaxis_opts=yaxisOpts,
            tooltip_opts=tooltipOpts,
        )

        self.colors:typing.List[str] = [
            "#2a5caa",
            "#1d953f",
            "#f58220",
            "#ef5b9c",
            "#585eaa",
            "#45b97c",
            "#e0861a",
            "#ed1941",
            "#7bbfea",
            "#00a6ac",
            "#f15a22",
            "#f05b72"
        ]

        self.colorIndex = 0

    def setTime(self, start:datetime, seconds:int):
        time = [(start + timedelta(seconds=t)).strftime("%Y-%m-%d %H:%M:%S") for t in range(seconds)]
        self.lineChart.add_xaxis(xaxis_data=time)

    def addLine(self, name:str, data:typing.List[int], stack:str = None):
        self.lineChart.add_yaxis(
            series_name=name,
            stack=stack,
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
            yaxis_index=0,
            y_axis=data,
            is_smooth=True,
            is_symbol_show=False,
            markpoint_opts=opts.MarkPointOpts([opts.MarkPointItem(type_="max")]),
            color=self.colors[self.colorIndex]
        )

        self.colorIndex = (self.colorIndex + 1) % len(self.colors)

    def render(self) -> str:
        return self.lineChart.render()


class Proc(object):

    def __init__(self, pid:str):
        self.pid:str = pid
        self.lastCpuSpending = self.cpuSpending()
        self.path:str = os.readlink(f"/proc/{pid}/exe")
        self.name:str = pathlib.Path(self.path).name

    # 根据pid获取一个进程
    def getByPid(pid:str):
        try:
            return Proc(pid)
        except:
            return None

    # 根据名称查找一个进程
    def findByName(regexp:str):
        pids:typing.List[int] = os.listdir("/proc")
        for pid in pids:
            try:
                binPath:str = os.readlink(f"/proc/{pid}/exe")
                if re.search(regexp, binPath) is not None:
                    return Proc(pid)
            except:
                continue

        return None

    # 获取进程当前的内存占用
    def memory(self) -> int:
        with open(f"/proc/{self.pid}/status") as fp:
            data:str = fp.read()
            rss:str = re.search(r"VmRSS:\s*([0-9]*)\s*kB", data)
        return int(rss.group(1))

    # 获取从上次调用到现在进程的CPU总占用时间
    def cpu(self) -> int:
        now:int = self.cpuSpending()
        delta:int = now - self.lastCpuSpending
        self.lastCpuSpending = now
        return delta

    # 获取进程的CPU总占用时间
    def cpuSpending(self) -> int:
        with open(f"/proc/{self.pid}/stat") as fp:
            data:str = fp.read()
            values:typing.List[str] = data.split()
        n:int = 0
        for v in values[13:17]:
            n += int(v)
        return n


class CpuStat(object):

    def __init__(self):
        self.lastJiffies:int = self.totalJiffies()

    # 获取从上次调用到现在CPU的运行时间
    def passJiffies(self):
        now:int = self.totalJiffies()
        delta:int = now - self.lastJiffies
        self.lastJiffies = now
        return delta

    # 获取CPU的总运行时间
    def totalJiffies(self) -> int:
        with open(f"/proc/stat") as fp:
            data:str = fp.readline()
            values:typing.List[str] = data.split()
        n:int = 0
        for v in values[1:]:
            n += int(v)
        return n


def main():
    parser:argparse.ArgumentParser = argparse.ArgumentParser(description="Process spending", add_help=True)
    parser.add_argument("-p", "--pid", help="Process ID", default=[], required=False, nargs="+")
    parser.add_argument("-n", "--name", help="Process name", default=[], required=False, nargs="+")
    args:argparse.Namespace = parser.parse_args()
    
    processes:typing.List[Proc] = []
    memoryData:typing.Dict[Proc, typing.List[int]] = {}
    cpuData:typing.Dict[Proc, typing.List[float]] = {}
    
    for pid in args.pid :
        proc:Proc = Proc.getByPid(pid)
        if proc is None:
            print("cannot find process by pid<%d>" % pid)
            continue
        processes.append(proc)
        memoryData[proc] = []
        cpuData[proc] = []

    for name in args.name:
        proc:Proc = Proc.findByName(name)
        if proc is None:
            print("cannot find process by name<%s>" % name)
        processes.append(proc)
        memoryData[proc] = []
        cpuData[proc] = []

    memoryChart:SpendingChart = SpendingChart("内存占用(kB)")
    cpuChart:SpendingChart = SpendingChart("CPU占用(%)")
    cpu:CpuStat = CpuStat()

    run:bool = True
    def handleSignal(signum, stackFrame):
        nonlocal run
        run = False

    signal(SIGTERM, handleSignal)
    signal(SIGINT, handleSignal)
    signal(SIGHUP, handleSignal)

    # 循环抓取数据
    start:datetime = datetime.now()
    seconds:int = 0
    while run:
        sleep(1)
        seconds += 1
        cpuTime:int = cpu.passJiffies()
        for proc in processes:
            if not run: # 退出事件导致时间拉长，产生错误数据
                break
            memoryData[proc].append(proc.memory())
            cpuData[proc].append(round(proc.cpu()/ cpuTime * 100, 2))

    # 图表生成
    memoryChart.setTime(start, seconds)
    cpuChart.setTime(start, seconds)
    for proc in processes:
        memoryChart.addLine(proc.name, memoryData[proc])
        cpuChart.addLine(proc.name, cpuData[proc])

    # 渲染
    page = Page()
    page.add(memoryChart.lineChart)
    page.add(cpuChart.lineChart)
    page.render()


if __name__ == "__main__":
    main()
