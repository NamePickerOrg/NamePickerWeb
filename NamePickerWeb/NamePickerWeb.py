"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
import random
import os
from typing import List

from rxconfig import config

class Choose:
    def __init__(self,sexFavor:str,numFavor:str,allowRepeat:bool,path:str):
        self.names = {}
        self.sexlen = [0,0,0]
        self.sexl = [[],[],[]]
        self.numlen = [0,0,0]
        self.numl = [[],[],[]]
        self.chosen = []
        self.sexFavor = sexFavor
        self.numFavor = numFavor
        self.allowRepeat = allowRepeat
        self.loadname(path)

    def pick(self):
        if self.sexFavor != "都抽":
            if self.sexFavor == "只抽男":
                le = self.sexlen[0]
                tar = self.sexl[0]
            elif self.sexFavor == "只抽女":
                le = self.sexlen[1]
                tar = self.sexl[1]
            else:
                le = self.sexlen[2]
                tar = self.sexl[2]
        else:
            le = self.length
            tar = self.names["name"]

        if self.numFavor != "都抽":
            if self.numFavor == "只抽双数":
                tar = list(set(tar) & set(self.numl[0]))
                le = len(tar)
            else:
                tar = list(set(tar) & set(self.numl[1]))
                le = len(tar)
        # if plugin_filters:
        #     for i in range(len(tar)):
        #         for j in range(len(plugin_filters_name)):
        #             if self.filswitch[j].isChecked() and not plugin_filters[j](tar[i]):
        #                 tar.remove(tar[i])
        le = len(tar)
        if le != 0:
            chs = random.randint(0, le - 1)
            if not self.allowRepeat:
                if len(self.chosen) >= le:
                    self.chosen = []
                    chs = random.randint(0, le - 1)
                else:
                    while chs in self.chosen:
                        chs = random.randint(0, le - 1)
                self.chosen.append(chs)
            tmp = {"name":tar[chs],"no":str(self.names["no"][self.names["name"].index(tar[chs])])}
            for i in self.names.keys():
                if i == "name" or i == "no":
                    continue
                tmp[i] = str(self.names[i][self.names["name"].index(tar[chs])])
            return tmp
        else:
            return "尚未抽选"

    def pickcb(self,nb:int):
        # for i in plugin.keys():
        #     plugin[i].beforePick()
        namet = []
        namel = []
        for i in range(nb):
            n = self.pick()
            if n != "尚未抽选":
                namet.append(n)
            else:
                return ["没有符合条件的学生"]

        for i in namet:
            namel.append("%s（%s）" % (i["name"], i["no"]))
        return namel
        # for i in plugin.keys():
        #     plugin[i].afterPick(namet)

    def loadname(self,path:str):
        try:
            # name = pd.read_csv("names.csv", sep=",", header=0)
            # name = name.to_dict()
            with open(path,"r",encoding="utf-8") as f:
                nl = f.readlines()
                ns = []
                head = nl[0].strip("\n").split(",")
                del nl[0]
                for i in nl:
                    ns.append(i.strip("\n").split(","))
            name = {}
            for j in head:
                name[j] = {}
                for i in range(len(ns)):
                    name[j][i] = ns[i][head.index(j)]
            self.names["name"] = list(name["name"].values())
            self.names["sex"] = list(name["sex"].values())
            self.names["no"] = list(name["no"].values())
            # for i in plugin_customkey:
            #     self.names[i] = list(name[i].values())
            for k in self.names.keys():
                for i in range(len(self.names[k])):
                    self.names[k][i] = str(self.names[k][i])
            self.length =len(name["name"])
            self.sexlen[0] = self.names["sex"].count("0")
            self.sexlen[1] = self.names["sex"].count("1")
            self.sexlen[2] = self.names["sex"].count("2")
            for i in self.names["name"]:
                if int(self.names["sex"][self.names["name"].index(i)]) == 0:
                    self.sexl[0].append(i)
                elif int(self.names["sex"][self.names["name"].index(i)]) == 1:
                    self.sexl[1].append(i)
                else:
                    self.sexl[2].append(i)

            for i in self.names["name"]:
                if int(self.names["no"][self.names["name"].index(i)])%2==0:
                    self.numl[0].append(i)
                else:
                    self.numl[1].append(i)
            self.numlen[0] = len(self.numl[0])
            self.numlen[1] = len(self.numl[1])
        except FileNotFoundError:
            with open(path,"w",encoding="utf-8") as f:
                st  = ["name,sex,no\n","example,0,1"]
                f.writelines(st)
            self.loadname()

core = Choose("都抽","都抽",False,"names/%s"%os.listdir("names")[0])
class State(rx.State):
    names: List[str] = [
        "example(0)"
    ]

    svl: List[str] = ["都抽","只抽男","只抽女","只抽特殊性别"]
    nvl: List[str] = ["都抽","只抽单数","只抽双数"]
    pl : List[str] = os.listdir("names")
    sv : str = "都抽"
    nv : str = "都抽"
    count: int = 1
    arp : bool = False
    path : str = "测试1班.csv"

    @rx.event
    def choose(self):
        global core
        core.allowRepeat = self.arp
        core.sexFavor = self.sv
        core.numFavor = self.nv
        self.names = core.pickcb(self.count)

    @rx.event
    def setsv(self,value:str):
        self.sv = value

    @rx.event
    def setnv(self,value:str):
        self.nv = value

    @rx.event
    def numinc(self):
        global core
        if len(core.names["name"]) > self.count:
            self.count += 1

    @rx.event
    def numdec(self):
        if self.count > 1:
            self.count -= 1

    @rx.event
    def arpc(self, checked: bool):
        self.arp = checked

    @rx.event
    def setp(self,value:str):
        self.path = value
        core.loadname("names/%s"%self.path)


def namebox(name:str):
    return rx.box(
        name,
        border_radius="5px",
        width="40%",
        margin="8px",
        padding="8px",
    ),

def index() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("NamePicker Web", size="9"),
            rx.text("「希望在我的灵魂中筑巢栖息，唱着没有词的歌曲，似乎永远不会停息。」"),
            spacing="5",
            justify="center",
            min_height="20vh",
        ),
        rx.grid(
            rx.foreach(State.names, namebox),
            columns="1",
        ),
        rx.flex(
            rx.button(
                "点击抽选",
                on_click=State.choose,
                radius="large"
            ),
            rx.flex(
                rx.text("选择名单文件"),
                rx.select(
                    State.pl,
                    value=State.path,
                    on_change=State.setp,
                    radius="large"
                ),
                spacing="9",
                width="100%"
            ),
            rx.flex(
                rx.text("输入抽选数量"),
                rx.flex(
                    rx.button(
                        "-",
                        color_scheme="red",
                        on_click=State.numdec,
                        radius="large"
                    ),
                    rx.heading(State.count),
                    rx.button(
                        "+",
                        color_scheme="grass",
                        on_click=State.numinc,
                        radius="large"
                    ),
                    spacing="3",
                ),
                spacing="9",
                width="100%"
            ),
            rx.flex(
                rx.text("选择性别偏好"),
                rx.select(
                    State.svl,
                    value=State.sv,
                    on_change=State.setsv,
                    radius="large"
                ),
                spacing="9",
                width="100%"
            ),
            rx.flex(
                rx.text("选择学号偏好"),
                rx.select(
                    State.nvl,
                    value=State.nv,
                    on_change=State.setnv,
                    radius="large"
                ),
                spacing="9",
                width="100%"
            ),
            rx.flex(
                rx.text("允许抽到重复名字"),
                rx.switch(
                    checked=State.arp,
                    on_change=State.arpc,
                ),
                spacing="9",
                width="100%"
            ),
            spacing="5",
            direction="column",
        ),
        rx.logo(),
    )

def mgmt() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("NamePicker Web - 管理面板", size="9"),
            rx.text("在此处管理NamePicker Web的行为"),
            spacing="5",
            justify="center",
            min_height="20vh",
        ),
        rx.flex(
            rx.flex(
                rx.text("当前用户信息"),
                rx.card(
                    rx.data_list.root(
                        rx.data_list.item(
                            rx.data_list.label("昵称"),
                            rx.data_list.value("灵魂歌手er"),
                        ),
                        rx.data_list.item(
                            rx.data_list.label("用户名"),
                            rx.data_list.value("lhgser"),
                        ),
                        rx.data_list.item(
                            rx.data_list.label("权限"),
                            rx.data_list.value(
                                rx.badge(
                                    "管理员",
                                    variant="soft",
                                    radius="large",
                                )
                            ),
                            align="center",
                        ),
                        rx.data_list.item(
                            rx.data_list.label("UID"),
                            rx.data_list.value(rx.code("1")),
                        ),
                    ),
                ),
                spacing="9",
                width="100%"
            ),
            spacing="5",
            direction="column",
        ),
        rx.logo()
    )
app = rx.App()
app.add_page(index,title="NamePicker Web")
app.add_page(mgmt,title="NamePicker Web 管理面板")