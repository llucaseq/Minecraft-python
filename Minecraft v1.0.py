import turtle
import time
import random
import math
import threading
from tkinter import Tk, Label, Button, Frame, messagebox

# 游戏基础设置
screen = turtle.Screen()
screen.title("Minecraft Ultimate")
screen.setup(1000, 700)
screen.setworldcoordinates(-500, -350, 500, 350)
screen.tracer(0)
screen.colormode(255)

# 全局变量
is_playing = False
player_x, player_y = 0, 0
player_health = 20
player_hunger = 20
player_effects = []
BLOCK_SIZE = 20
render_distance = 15
time_of_day = 0
weather = "clear"
light_level = 1.0
dimension = "主世界"
redstone_ticks = 0
redstone_power = {}

# 数据结构
blocks = {}  # {z: {(x,y): block_type}}
inventory = {}
hotbar = [None] * 9
players = {}
animals = []
monsters = []
items_on_ground = []
plants = {}  # {(x,y,z): {"type": "wheat", "growth": 0, "watered": True}}
fish = []
recipes = {}
buttons = {}

# 方块类型定义 - 添加了新方块
BLOCK_TYPES = {
    "grass": {"breakable": True, "hardness": 0.6, "drop": "dirt", "tool": None, "transparent": False},
    "dirt": {"breakable": True, "hardness": 0.5, "drop": "dirt", "tool": None, "transparent": False},
    "stone": {"breakable": True, "hardness": 1.5, "drop": "cobblestone", "tool": "pickaxe", "transparent": False},
    "cobblestone": {"breakable": True, "hardness": 2.0, "drop": "cobblestone", "tool": "pickaxe", "transparent": False},
    "wood": {"breakable": True, "hardness": 2.0, "drop": "wood", "tool": "axe", "transparent": False},
    "leaves": {"breakable": True, "hardness": 0.2, "drop": "stick", "tool": "shears", "transparent": True},
    "water": {"breakable": False, "hardness": 100, "drop": None, "tool": None, "transparent": True, "liquid": True},
    "glass": {"breakable": True, "hardness": 0.3, "drop": "glass", "tool": None, "transparent": True},
    "bedrock": {"breakable": False, "hardness": -1, "drop": None, "tool": None, "transparent": False},
    "sand": {"breakable": True, "hardness": 0.5, "drop": "sand", "tool": None, "transparent": False},
    "gravel": {"breakable": True, "hardness": 0.6, "drop": "gravel", "tool": None, "transparent": False},
    "coal_ore": {"breakable": True, "hardness": 3.0, "drop": "coal", "tool": "pickaxe", "transparent": False},
    "iron_ore": {"breakable": True, "hardness": 3.0, "drop": "iron_ore", "tool": "pickaxe", "transparent": False},
    "gold_ore": {"breakable": True, "hardness": 3.0, "drop": "gold_ore", "tool": "pickaxe", "transparent": False},
    "diamond_ore": {"breakable": True, "hardness": 3.0, "drop": "diamond", "tool": "pickaxe", "transparent": False},
    "redstone_ore": {"breakable": True, "hardness": 3.0, "drop": "redstone", "tool": "pickaxe", "transparent": False},
    "crafting_table": {"breakable": True, "hardness": 2.5, "drop": "crafting_table", "tool": "axe", "transparent": False, "interactive": True},
    "torch": {"breakable": True, "hardness": 0.1, "drop": "torch", "tool": None, "transparent": True, "light": 15},
    "redstone_torch": {"breakable": True, "hardness": 0.1, "drop": "redstone_torch", "tool": None, "transparent": True, "redstone": True},
    "redstone_wire": {"breakable": True, "hardness": 0.1, "drop": "redstone", "tool": None, "transparent": True, "redstone": True},
    "button": {"breakable": True, "hardness": 0.5, "drop": "button", "tool": None, "transparent": True, "redstone": True},
    "lever": {"breakable": True, "hardness": 0.5, "drop": "lever", "tool": None, "transparent": True, "redstone": True},
    "piston": {"breakable": True, "hardness": 0.5, "drop": "piston", "tool": None, "transparent": False, "redstone": True},
    "redstone_lamp": {"breakable": True, "hardness": 0.3, "drop": "redstone_lamp", "tool": None, "transparent": False, "redstone": True},
    "farmland": {"breakable": True, "hardness": 0.6, "drop": "dirt", "tool": None, "transparent": False, "farmable": True},
    "water_bucket": {"breakable": False, "hardness": 0, "drop": "water_bucket", "tool": None, "transparent": False, "liquid": True},
    "furnace": {"breakable": True, "hardness": 3.5, "drop": "furnace", "tool": "pickaxe", "transparent": False, "interactive": True},
    "composter": {"breakable": True, "hardness": 0.6, "drop": "composter", "tool": None, "transparent": False, "interactive": True},
    "cloud": {"breakable": True, "hardness": 0.1, "drop": "cloud", "tool": None, "transparent": True},
    "holy_stone": {"breakable": True, "hardness": 2.0, "drop": "holy_stone", "tool": "pickaxe", "transparent": False},
    "abyssal_stone": {"breakable": True, "hardness": 3.0, "drop": "abyssal_stone", "tool": "iron_pickaxe", "transparent": False},
    "abyssal_ore": {"breakable": True, "hardness": 4.0, "drop": "abyssal_crystal", "tool": "diamond_pickaxe", "transparent": False},
    "chest": {"breakable": True, "hardness": 2.5, "drop": "chest", "tool": "axe", "transparent": False, "inventory": True},
    "bed": {"breakable": True, "hardness": 0.2, "drop": "bed", "tool": None, "transparent": False, "interactive": True},
    
    # 新增方块类型
    "obsidian": {"breakable": True, "hardness": 50, "drop": "obsidian", "tool": "diamond_pickaxe", "transparent": False},
    "quartz_ore": {"breakable": True, "hardness": 3.0, "drop": "quartz", "tool": "pickaxe", "transparent": False},
    "lapis_ore": {"breakable": True, "hardness": 3.0, "drop": "lapis", "tool": "pickaxe", "transparent": False},
    "emerald_ore": {"breakable": True, "hardness": 3.0, "drop": "emerald", "tool": "iron_pickaxe", "transparent": False},
    "glowstone": {"breakable": True, "hardness": 0.3, "drop": "glowstone_dust", "tool": "pickaxe", "transparent": True, "light": 15},
    "ice": {"breakable": True, "hardness": 0.5, "drop": "water", "tool": "pickaxe", "transparent": True, "slippery": True},
    "snow": {"breakable": True, "hardness": 0.1, "drop": "snowball", "tool": None, "transparent": False},
    "clay": {"breakable": True, "hardness": 0.6, "drop": "clay_ball", "tool": None, "transparent": False},
    "hay_bale": {"breakable": True, "hardness": 0.5, "drop": "hay", "tool": "axe", "transparent": False},
    "wool": {"breakable": True, "hardness": 0.8, "drop": "wool", "tool": "shears", "transparent": False, "colorful": True},
    "netherrack": {"breakable": True, "hardness": 0.4, "drop": "netherrack", "tool": None, "transparent": False},
    "nether_brick": {"breakable": True, "hardness": 2.0, "drop": "nether_brick", "tool": "pickaxe", "transparent": False},
    "end_stone": {"breakable": True, "hardness": 3.0, "drop": "end_stone", "tool": "pickaxe", "transparent": False},
    "sponge": {"breakable": True, "hardness": 0.6, "drop": "sponge", "tool": "axe", "transparent": False, "absorbs_water": True},
    "cactus": {"breakable": True, "hardness": 0.4, "drop": "cactus", "tool": None, "transparent": False, "damaging": True}
}

# 方块颜色定义 - 为新方块添加颜色
COLORS = {
    "grass": [(34, 139, 34), (139, 69, 19), (101, 67, 33)],
    "dirt": [(139, 69, 19), (130, 64, 18), (121, 59, 17)],
    "stone": [(169, 169, 169), (130, 130, 130), (100, 100, 100)],
    "cobblestone": [(101, 67, 33), (82, 53, 27), (64, 41, 20)],
    "wood": [(139, 69, 19), (160, 82, 45), (184, 134, 11)],
    "leaves": [(34, 139, 34), (50, 205, 50), (0, 255, 0)],
    "water": [(0, 0, 255, 100), (0, 0, 200, 100), (0, 0, 150, 100)],
    "glass": [(200, 200, 255, 150), (220, 220, 255, 150), (240, 240, 255, 150)],
    "bedrock": [(80, 80, 80), (70, 70, 70), (60, 60, 60)],
    "sand": [(244, 164, 96), (210, 180, 140), (255, 218, 185)],
    "gravel": [(169, 169, 169), (192, 192, 192), (211, 211, 211)],
    "coal_ore": [(50, 50, 50), (40, 40, 40), (30, 30, 30)],
    "iron_ore": [(192, 192, 192), (211, 211, 211), (220, 220, 220)],
    "gold_ore": [(255, 215, 0), (255, 223, 89), (255, 236, 139)],
    "diamond_ore": [(0, 255, 255), (175, 238, 238), (224, 255, 255)],
    "redstone_ore": [(178, 34, 34), (220, 20, 60), (255, 0, 0)],
    "crafting_table": [(139, 69, 19), (101, 67, 33), (184, 134, 11)],
    "torch": [(255, 165, 0), (255, 140, 0), (255, 69, 0)],
    "redstone_torch": [(178, 34, 34), (220, 20, 60), (255, 0, 0)],
    "redstone_wire": [(178, 34, 34), (220, 20, 60), (255, 0, 0)],
    "button": [(139, 69, 19), (101, 67, 33), (184, 134, 11)],
    "lever": [(139, 69, 19), (255, 165, 0), (101, 67, 33)],
    "piston": [(139, 69, 19), (101, 67, 33), (184, 134, 11)],
    "redstone_lamp": [(255, 255, 255), (240, 240, 240), (220, 220, 220)],
    "farmland": [(139, 69, 19), (130, 64, 18), (121, 59, 17)],
    "furnace": [(101, 67, 33), (82, 53, 27), (64, 41, 20)],
    "composter": [(139, 69, 19), (110, 52, 11), (82, 39, 0)],
    "cloud": [(255, 255, 255, 100), (240, 240, 240, 100), (220, 220, 220, 100)],
    "holy_stone": [(245, 245, 245), (220, 220, 220), (200, 200, 200)],
    "abyssal_stone": [(30, 30, 60), (25, 25, 50), (20, 20, 40)],
    "abyssal_ore": [(138, 43, 226), (128, 0, 128), (106, 90, 205)],
    "chest": [(139, 69, 19), (130, 64, 18), (121, 59, 17)],
    "bed": [(220, 20, 60), (205, 92, 92), (178, 34, 34)],
    
    # 新方块的颜色定义
    "obsidian": [(49, 46, 129), (41, 37, 107), (33, 31, 86)],
    "quartz_ore": [(245, 245, 245), (220, 220, 220), (200, 200, 200)],
    "lapis_ore": [(59, 130, 246), (51, 115, 224), (44, 100, 202)],
    "emerald_ore": [(16, 185, 129), (12, 161, 113), (8, 137, 98)],
    "glowstone": [(251, 191, 36, 200), (245, 158, 11, 200), (234, 179, 8, 200)],
    "ice": [(200, 230, 255, 180), (180, 210, 235, 180), (160, 190, 215, 180)],
    "snow": [(255, 255, 255), (240, 240, 240), (220, 220, 220)],
    "clay": [(135, 206, 235), (116, 185, 230), (96, 164, 225)],
    "hay_bale": [(187, 183, 36), (172, 168, 33), (157, 153, 30)],
    "wool": [(255, 255, 255), (240, 240, 240), (220, 220, 220)],
    "netherrack": [(115, 41, 41), (102, 36, 36), (89, 31, 31)],
    "nether_brick": [(101, 28, 28), (89, 24, 24), (77, 20, 20)],
    "end_stone": [(229, 228, 226), (215, 214, 212), (201, 200, 198)],
    "sponge": [(249, 166, 2), (234, 154, 2), (219, 142, 2)],
    "cactus": [(34, 139, 34), (29, 119, 30), (24, 99, 26)]
}

# 物品定义 - 为新方块添加对应的物品
ITEMS = {
    "wood": {"type": "material"},
    "stick": {"type": "material"},
    "cobblestone": {"type": "material"},
    "coal": {"type": "material", "fuel": 8},
    "iron_ore": {"type": "material"},
    "iron_ingot": {"type": "material"},
    "gold_ore": {"type": "material"},
    "gold_ingot": {"type": "material"},
    "diamond": {"type": "material"},
    "redstone": {"type": "material"},
    "abyssal_crystal": {"type": "material"},
    "axe": {"type": "tool", "durability": 100},
    "pickaxe": {"type": "tool", "durability": 100},
    "shovel": {"type": "tool", "durability": 100},
    "sword": {"type": "weapon", "damage": 3, "durability": 100},
    "wheat_seeds": {"type": "seed", "plant": "wheat"},
    "carrot_seeds": {"type": "seed", "plant": "carrot"},
    "potato_seeds": {"type": "seed", "plant": "potato"},
    "wheat": {"type": "food", "hunger": 2},
    "carrot": {"type": "food", "hunger": 3},
    "potato": {"type": "food", "hunger": 3},
    "bread": {"type": "food", "hunger": 5},
    "fishing_rod": {"type": "tool", "durability": 65, "use": "fishing"},
    "fish": {"type": "food", "hunger": 2},
    "salmon": {"type": "food", "hunger": 3},
    "pufferfish": {"type": "food", "hunger": 1, "poisonous": True},
    
    # 新物品
    "obsidian": {"type": "material"},
    "quartz": {"type": "material"},
    "lapis": {"type": "material", "use": "dye"},
    "emerald": {"type": "material", "use": "trade"},
    "glowstone_dust": {"type": "material", "light": True},
    "snowball": {"type": "material", "use": "throw"},
    "clay_ball": {"type": "material"},
    "hay": {"type": "material", "use": "feed"},
    "wool": {"type": "material", "use": "craft"},
    "netherrack": {"type": "material", "fuel": 1},
    "nether_brick": {"type": "material"},
    "end_stone": {"type": "material"},
    "sponge": {"type": "material", "use": "absorb_water"},
    "cactus": {"type": "material", "use": "brew"}
}

# 维度定义
dimensions = {
    "主世界": {"sky_color": (135, 206, 235), "ground_color": (34, 139, 34)},
    "下界": {"sky_color": (139, 0, 0), "ground_color": (101, 67, 33)},
    "末地": {"sky_color": (0, 0, 51), "ground_color": (255, 228, 181)},
    "天堂": {"sky_color": (135, 240, 255), "ground_color": (124, 252, 0)},
    "深渊": {"sky_color": (0, 0, 0), "ground_color": (30, 30, 60)}
}

# Boss定义
bosses = {
    "末影龙": {"health": 200, "damage": 10, "size": 3, "color": (75, 0, 130)},
    "凋灵": {"health": 300, "damage": 15, "size": 2.5, "color": (47, 79, 79)},
    "天堂守护者": {"health": 250, "damage": 8, "size": 2, "color": (255, 255, 204)},
    "深渊领主": {"health": 350, "damage": 12, "size": 3, "color": (75, 0, 130)}
}

# 画笔设置
pen = turtle.Turtle()
pen.speed(0)
pen.hideturtle()
pen.penup()

player_pen = turtle.Turtle()
player_pen.speed(0)
player_pen.shape("turtle")
player_pen.color(255, 215, 0)
player_pen.penup()

remote_players_pen = [turtle.Turtle() for _ in range(5)]
for p in remote_players_pen:
    p.speed(0)
    p.shape("turtle")
    p.hideturtle()
    p.penup()

animal_pens = [turtle.Turtle() for _ in range(10)]
for p in animal_pens:
    p.speed(0)
    p.shape("circle")
    p.hideturtle()
    p.penup()

monster_pens = [turtle.Turtle() for _ in range(10)]
for p in monster_pens:
    p.speed(0)
    p.shape("circle")
    p.hideturtle()
    p.penup()

boss_pen = turtle.Turtle()
boss_pen.speed(0)
boss_pen.shape("square")
boss_pen.hideturtle()
boss_pen.penup()

# 末影龙
ender_dragon = turtle.Turtle()
ender_dragon.speed(0)
ender_dragon.shape("square")
ender_dragon.color(75, 0, 130)
ender_dragon.shapesize(3, 3)
ender_dragon.hideturtle()
ender_dragon.penup()

# 选择框画笔
selection_box_pen = turtle.Turtle()
selection_box_pen.speed(0)
selection_box_pen.color(255, 255, 0)
selection_box_pen.hideturtle()
selection_box_pen.penup()

# 辅助函数
def play_sound(sound):
    """播放音效（实际实现需添加音频库支持）"""
    pass

def draw_block(x, y, z, block_type, force=False):
    """绘制方块"""
    if z not in blocks:
        blocks[z] = {}
    
    if not force and (x, y) in blocks[z] and blocks[z][(x, y)] == block_type:
        return
        
    blocks[z][(x, y)] = block_type
    
    pen.goto(x, y)
    # 处理特殊方块的透明度
    if len(COLORS[block_type][0]) == 4:  # 有透明度
        pen.color(COLORS[block_type][0][0], COLORS[block_type][0][1], COLORS[block_type][0][2])
        pen.pencolor(COLORS[block_type][0][0], COLORS[block_type][0][1], COLORS[block_type][0][2])
        pen.fillcolor(COLORS[block_type][0][0], COLORS[block_type][0][1], COLORS[block_type][0][2], COLORS[block_type][0][3])
    else:
        pen.color(COLORS[block_type][0])
    pen.pendown()
    pen.begin_fill()
    
    for _ in range(4):
        pen.forward(BLOCK_SIZE)
        pen.left(90)
    
    pen.end_fill()
    
    # 绘制侧面阴影
    if len(COLORS[block_type][1]) == 4:  # 有透明度
        pen.fillcolor(COLORS[block_type][1][0], COLORS[block_type][1][1], COLORS[block_type][1][2], COLORS[block_type][1][3])
    else:
        pen.color(COLORS[block_type][1])
    pen.begin_fill()
    pen.forward(BLOCK_SIZE)
    pen.left(45)
    pen.forward(BLOCK_SIZE * 0.4)
    pen.left(135)
    pen.forward(BLOCK_SIZE)
    pen.end_fill()
    
    # 绘制顶部阴影
    if len(COLORS[block_type][2]) == 4:  # 有透明度
        pen.fillcolor(COLORS[block_type][2][0], COLORS[block_type][2][1], COLORS[block_type][2][2], COLORS[block_type][2][3])
    else:
        pen.color(COLORS[block_type][2])
    pen.begin_fill()
    pen.left(45)
    pen.forward(BLOCK_SIZE * 0.4)
    pen.left(45)
    pen.forward(BLOCK_SIZE)
    pen.left(135)
    pen.forward(BLOCK_SIZE * 0.4)
    pen.end_fill()
    
    pen.penup()

def remove_block(x, y, z):
    """移除方块"""
    if z in blocks and (x, y) in blocks[z]:
        del blocks[z][(x, y)]
        if not blocks[z]:
            del blocks[z]
        
        # 清除方块显示
        pen.goto(x, y)
        pen.color(screen.bgcolor())
        pen.pendown()
        pen.begin_fill()
        
        for _ in range(4):
            pen.forward(BLOCK_SIZE)
            pen.left(90)
        
        pen.end_fill()
        
        # 清除阴影
        pen.begin_fill()
        pen.forward(BLOCK_SIZE)
        pen.left(45)
        pen.forward(BLOCK_SIZE * 0.4)
        pen.left(135)
        pen.forward(BLOCK_SIZE)
        pen.end_fill()
        
        pen.left(45)
        pen.forward(BLOCK_SIZE * 0.4)
        pen.left(45)
        pen.forward(BLOCK_SIZE)
        pen.left(135)
        pen.forward(BLOCK_SIZE * 0.4)
        pen.end_fill()
        
        pen.penup()

def is_colliding(x, y, z):
    """检查碰撞"""
    block_x = round(x / BLOCK_SIZE) * BLOCK_SIZE
    block_y = round(y / BLOCK_SIZE) * BLOCK_SIZE
    return z in blocks and (block_x, block_y) in blocks[z]

def spawn_item(x, y, item_type, count=1):
    """生成物品"""
    item_pen = turtle.Turtle()
    item_pen.speed(0)
    item_pen.shape("circle")
    item_pen.shapesize(0.5, 0.5)
    # 为新物品设置颜色
    item_colors = {
        "obsidian": (49, 46, 129),
        "quartz": (245, 245, 245),
        "lapis": (59, 130, 246),
        "emerald": (16, 185, 129),
        "glowstone_dust": (251, 191, 36),
        "snowball": (255, 255, 255),
        "clay_ball": (135, 206, 235),
        "hay": (187, 183, 36),
        "wool": (255, 255, 255),
        "netherrack": (115, 41, 41),
        "nether_brick": (101, 28, 28),
        "end_stone": (229, 228, 226),
        "sponge": (249, 166, 2),
        "cactus": (34, 139, 34)
    }
    # 默认使用金色
    color = item_colors.get(item_type, (255, 215, 0))
    item_pen.color(color)
    item_pen.penup()
    item_pen.goto(x, y)
    item_pen.showturtle()
    
    items_on_ground.append({
        "x": x, "y": y, "type": item_type, "count": count, "pen": item_pen
    })

def draw_button(button_id):
    """绘制按钮"""
    btn = buttons[button_id]
    pen.goto(btn["x"], btn["y"])
    pen.color(100, 100, 100)
    pen.pendown()
    pen.begin_fill()
    
    for _ in range(2):
        pen.forward(btn["width"])
        pen.left(90)
        pen.forward(btn["height"])
        pen.left(90)
    
    pen.end_fill()
    
    pen.color(255, 255, 255)
    pen.penup()
    pen.goto(btn["x"] + btn["width"]/2, btn["y"] + btn["height"]/2 - 10)
    pen.write(btn["text"], align="center", font=("Arial", 10, "normal"))
    pen.penup()

def draw_control_bar():
    """绘制控制栏"""
    # 绘制生命值
    pen.goto(-450, 300)
    pen.color(255, 0, 0)
    pen.write(f"生命值: {player_health}/20", font=("Arial", 12, "normal"))
    
    # 绘制饥饿值
    pen.goto(-300, 300)
    pen.color(255, 165, 0)
    pen.write(f"饥饿值: {player_hunger}/20", font=("Arial", 12, "normal"))
    
    # 绘制时间
    time_str = "白天" if 1000 <= time_of_day < 12000 else "夜晚"
    pen.goto(-150, 300)
    pen.color(255, 255, 255)
    pen.write(f"时间: {time_str}", font=("Arial", 12, "normal"))
    
    # 绘制维度
    pen.goto(0, 300)
    pen.color(255, 255, 255)
    pen.write(f"维度: {dimension}", font=("Arial", 12, "normal"))
    
    # 绘制快捷栏
    for i in range(9):
        x = -200 + i * 50
        y = -320
        
        pen.goto(x, y)
        pen.color(100, 100, 100)
        pen.pendown()
        pen.begin_fill()
        
        for _ in range(2):
            pen.forward(40)
            pen.left(90)
            pen.forward(40)
            pen.left(90)
        
        pen.end_fill()
        pen.penup()
        
        if hotbar[i]:
            pen.goto(x + 20, y + 20)
            pen.color(255, 255, 255)
            pen.write(hotbar[i][:4], align="center", font=("Arial", 8, "normal"))
            pen.write(f" ({inventory.get(hotbar[i], 0)})", align="center", font=("Arial", 8, "normal"))
    
    # 绘制功能按钮
    draw_button("redstone_guide")
    draw_button("brew_guide")
    draw_button("heaven")
    draw_button("abyss")
    draw_button("fishing")
    draw_button("multiplayer")

def draw_selection_box():
    """绘制选择框"""
    block_x = round(player_x / BLOCK_SIZE) * BLOCK_SIZE
    block_y = round(player_y / BLOCK_SIZE) * BLOCK_SIZE
    
    selection_box_pen.clear()
    selection_box_pen.goto(block_x, block_y)
    selection_box_pen.pendown()
    
    for _ in range(4):
        selection_box_pen.forward(BLOCK_SIZE)
        selection_box_pen.left(90)
    
    selection_box_pen.penup()

def draw_main_menu():
    """绘制主菜单"""
    global is_playing
    
    is_playing = False
    screen.clear()
    screen.bgcolor(30, 30, 30)
    
    pen.goto(0, 100)
    pen.color(255, 215, 0)
    pen.write("Minecraft Ultimate", align="center", font=("Arial", 36, "bold"))
    
    buttons["start"] = {"x": -100, "y": 0, "width": 200, "height": 50, "text": "开始游戏"}
    buttons["quit"] = {"x": -100, "y": -70, "width": 200, "height": 50, "text": "退出"}
    
    draw_button("start")
    draw_button("quit")
    
    screen.update()

# 游戏功能函数
def add_player(player_id, x, y, z, is_local=False):
    """添加玩家"""
    if player_id in players:
        return
        
    # 分配画笔
    if is_local:
        # 本地玩家使用已有的画笔
        pen = player_pen
    else:
        # 远程玩家使用专用画笔
        for p in remote_players_pen:
            if not p.isvisible():
                pen = p
                break
        else:
            pen = remote_players_pen[0]  # 如果所有画笔都在使用，复用第一个
    
    # 随机颜色（非本地玩家）
    color = (255, 215, 0) if is_local else (
        random.randint(50, 255),
        random.randint(50, 255),
        random.randint(50, 255)
    )
    
    pen.color(color)
    pen.goto(x, y)
    pen.showturtle()
    
    players[player_id] = {
        "x": x, "y": y, "z": z,
        "health": 20,
        "pen": pen,
        "is_local": is_local
    }

def update_player(player_id, x, y, z, health):
    """更新玩家位置和状态"""
    if player_id not in players:
        return
        
    players[player_id]["x"] = x
    players[player_id]["y"] = y
    players[player_id]["z"] = z
    players[player_id]["health"] = health
    players[player_id]["pen"].goto(x, y)

def push_block(x, y, z):
    """活塞推动方块"""
    if z in blocks and (x, y) in blocks[z]:
        block_type = blocks[z][(x, y)]
        # 检查方块是否可被推动
        if BLOCK_TYPES[block_type].get("movable", True):
            # 移除原位置方块
            remove_block(x, y, z)
            # 在新位置放置方块
            draw_block(x, y+BLOCK_SIZE, z, block_type)

def redstone_updater(update_func):
    """红石系统更新循环"""
    while True:
        if is_playing:
            update_func()
        time.sleep(0.05)  # 每50ms更新一次

def update_redstone():
    """更新红石电路状态"""
    global redstone_ticks
    redstone_ticks = (redstone_ticks + 1) % 20  # 每20游戏刻更新一次
    
    # 处理按钮状态（按下后一段时间自动弹起）
    for (x, y, z), block_type in get_all_redstone_blocks():
        if block_type == "button" and redstone_power[(x, y, z)] > 0:
            if redstone_ticks % 40 == 0:  # 按钮按下后2秒弹起
                redstone_power[(x, y, z)] = 0
                update_redstone_propagation(x, y, z)
    
    # 处理红石火把状态（每段时间反转一次）
    if redstone_ticks % 10 == 0:
        for (x, y, z), block_type in get_all_redstone_blocks():
            if block_type == "redstone_torch":
                current_power = redstone_power[(x, y, z)]
                new_power = 15 if current_power == 0 else 0
                redstone_power[(x, y, z)] = new_power
                update_redstone_propagation(x, y, z)
    
    # 更新红石灯状态
    for (x, y, z), block_type in get_all_redstone_blocks():
        if block_type == "redstone_lamp":
            if redstone_power[(x, y, z)] > 0:
                # 点亮红石灯
                draw_block(x, y, z, block_type, force=True)
            else:
                # 关闭红石灯（使用暗色调）
                pen.goto(x, y)
                pen.color((100, 100, 100))
                pen.begin_fill()
                pen.pendown()
                for _ in range(4):
                    pen.forward(BLOCK_SIZE)
                    pen.left(90)
                pen.end_fill()
                pen.penup()
    
    # 处理活塞动作
    for (x, y, z), block_type in get_all_redstone_blocks():
        if block_type == "piston" and redstone_power[(x, y, z)] > 0:
            # 活塞伸出
            push_block(x, y+1, z)  # 假设活塞向上推
        elif block_type == "piston" and redstone_power[(x, y, z)] == 0:
            # 活塞收回
            pass  # 这里可以添加活塞收回逻辑

def get_all_redstone_blocks():
    """获取所有红石相关方块"""
    redstone_blocks = []
    for z in blocks:
        for (x, y), block_type in blocks[z].items():
            if BLOCK_TYPES.get(block_type, {}).get("redstone", False):
                redstone_blocks.append(((x, y, z), block_type))
    return redstone_blocks

def update_redstone_propagation(x, y, z):
    """更新红石信号传播（简化版）"""
    pass  # 实际实现需要复杂的信号传播逻辑

def plant_updater(update_func):
    """植物生长更新循环"""
    while True:
        if is_playing:
            update_func()
        time.sleep(1)  # 每1秒更新一次

def update_plants():
    """更新植物生长"""
    current_time = time.time()
    
    for (x, y, z), plant in list(plants.items()):
        # 检查植物是否还存活（下方是否有耕地）
        if not (z-1 in blocks and (x, y) in blocks[z-1] and blocks[z-1][(x, y)] == "farmland"):
            del plants[(x, y, z)]
            # 清除植物显示
            pen.goto(x, y)
            pen.color(screen.bgcolor())
            pen.begin_fill()
            pen.pendown()
            pen.circle(BLOCK_SIZE / 2)
            pen.end_fill()
            pen.penup()
            continue
        
        # 检查是否需要生长
        if current_time - plant["last_growth"] > 5:  # 每5秒生长一次
            # 检查是否浇水和有光
            growth_chance = 0.3 if plant["watered"] else 0.1
            if random.random() < growth_chance and light_level > 0.5:
                plant["growth"] = min(100, plant["growth"] + 5)
                draw_plant(x, y, z, plant["type"], plant["growth"])
                
                # 成熟后可以收获
                if plant["growth"] >= 100:
                    # 掉落作物
                    crop_item = plant["type"]
                    spawn_item(x, y, crop_item, random.randint(1, 3))
                    # 有几率掉落种子
                    if random.random() < 0.3:
                        spawn_item(x, y, f"{crop_item}_seeds", 1)

                    # 移除植物
                    del plants[(x, y, z)]
                    # 清除植物显示
                    pen.goto(x, y)
                    pen.color(screen.bgcolor())
                    pen.begin_fill()
                    pen.pendown()
                    pen.circle(BLOCK_SIZE / 2)
                    pen.end_fill()
                    pen.penup()
        
        plant["last_growth"] = current_time

def draw_plant(x, y, z, plant_type, growth):
    """绘制植物"""
    # 根据生长阶段绘制不同形态
    growth_stage = min(4, int(growth / 25))  # 0-4个生长阶段
    
    pen.goto(x, y)
    if plant_type == "wheat":
        colors = [(34, 139, 34), (50, 205, 50), (124, 252, 0), (255, 215, 0)]
        pen.color(colors[growth_stage])
    elif plant_type == "carrot":
        colors = [(34, 139, 34), (50, 205, 50), (255, 69, 0), (255, 99, 71)]
        pen.color(colors[growth_stage])
    elif plant_type == "potato":
        colors = [(34, 139, 34), (50, 205, 50), (139, 69, 19), (160, 82, 45)]
        pen.color(colors[growth_stage])
    
    # 绘制植物（随生长阶段变大）
    size = BLOCK_SIZE * (0.2 + growth_stage * 0.2)
    pen.begin_fill()
    pen.pendown()
    pen.circle(size / 2)
    pen.end_fill()
    pen.penup()

def selection_box_updater():
    """持续更新选择框位置"""
    while is_playing:
        draw_selection_box()
        time.sleep(0.1)

def entity_behavior():
    """实体AI与行为系统（包含动物和怪物）"""
    global player_health, player_hunger
    while is_playing:
        # 动物行为（被动生物）
        for animal in animals:
            if animal["health"] <= 0:
                animal["pen"].hideturtle()
                continue
                
            # 随机移动
            if random.random() < 0.05:  # 5%概率移动
                dir_x = random.choice([-1, 0, 1]) * BLOCK_SIZE//2
                dir_y = random.choice([-1, 0, 1]) * BLOCK_SIZE//2
                new_x = animal["x"] + dir_x
                new_y = animal["y"] + dir_y
                
                # 远离玩家
                distance_to_player = math.sqrt(
                    (animal["x"] - player_x)**2 + 
                    (animal["y"] - player_y)** 2
                )
                if distance_to_player < 100:
                    # 远离玩家移动
                    if animal["x"] < player_x:
                        new_x -= BLOCK_SIZE//2
                    else:
                        new_x += BLOCK_SIZE//2
                        
                    if animal["y"] < player_y:
                        new_y -= BLOCK_SIZE//2
                    else:
                        new_y += BLOCK_SIZE//2
                
                if not is_colliding(new_x, new_y, 0):
                    animal["x"] = new_x
                    animal["y"] = new_y
                    animal["pen"].goto(new_x, new_y)

        
        # 怪物行为增强
        for monster in monsters:
            if monster["health"] <= 0:
                monster["pen"].hideturtle()
                continue
                
            # 白天燃烧（骷髅和僵尸）
            if (dimension == "主世界" and 1000 <= time_of_day < 12000 and 
                monster["type"] in ["zombie", "skeleton"] and 
                monster["y"] > -50):  # 在地面上
                monster["health"] -= 1
                if monster["health"] <= 0:
                    monster["pen"].hideturtle()
                    continue
            
            # 检测玩家距离，进入攻击状态
            distance_to_player = math.sqrt(
                (monster["x"] - player_x)**2 + 
                (monster["y"] - player_y)** 2
            )
            
            # Creeper在近距离会爆炸
            if monster["type"] == "creeper" and distance_to_player < 80:
                # 爆炸效果
                monster["health"] = 0
                monster["pen"].hideturtle()
                player_health -= 10
                play_sound("attack")
                play_sound("hurt")
                continue
                
            # 进入攻击状态
            if distance_to_player < 200:
                monster["aggro"] = True
                monster["target_x"], monster["target_y"] = player_x, player_y

            elif monster["aggro"] and distance_to_player > 300:
                monster["aggro"] = False
                # 随机移动目标
                monster["target_x"] = random.randint(-530, 530)
                monster["target_y"] = random.randint(-100, 200)
            
            # 计算移动方向
            move_x, move_y = 0, 0
            if abs(monster["x"] - monster["target_x"]) > BLOCK_SIZE//2:
                move_x = BLOCK_SIZE//2 if monster["x"] < monster["target_x"] else -BLOCK_SIZE//2
            if abs(monster["y"] - monster["target_y"]) > BLOCK_SIZE//2:
                move_y = BLOCK_SIZE//2 if monster["y"] < monster["target_y"] else -BLOCK_SIZE//2
            
            # 检查移动是否会导致碰撞
            new_x = monster["x"] + move_x
            new_y = monster["y"] + move_y
            
            # 如果不碰撞则移动
            if not is_colliding(new_x, new_y, 0):
                monster["x"] = new_x
                monster["y"] = new_y
                monster["pen"].goto(new_x, new_y)
            
            # 攻击玩家
            if (abs(monster["x"] - player_x) < BLOCK_SIZE and 
                abs(monster["y"] - player_y) < BLOCK_SIZE):
                damage = 2 if monster["type"] == "zombie" else 1
                player_health -= damage
                player_hunger -= 1
                if player_health <= 0:
                    messagebox.showinfo("游戏结束", "你被怪物击败了!")
                    draw_main_menu()

                play_sound("attack")
                play_sound("hurt")
                draw_control_bar()
        
        # 末影龙移动（仅在末地）
        if dimension == "末地" and is_playing:
            ender_dragon_x, ender_dragon_y = ender_dragon.xcor(), ender_dragon.ycor()
            
            # 末影龙会追踪玩家
            distance_to_player = math.sqrt(
                (ender_dragon_x - player_x)**2 + 
                (ender_dragon_y - player_y)** 2
            )
            
            if distance_to_player < 400:
                target_x, target_y = player_x, player_y
            else:
                target_x, target_y = 0, 100
                
            move_x = BLOCK_SIZE//2 if ender_dragon_x < target_x else -BLOCK_SIZE//2
            move_y = BLOCK_SIZE//4 if ender_dragon_y < target_y else -BLOCK_SIZE//4
            
            new_x = ender_dragon_x + move_x
            new_y = ender_dragon_y + move_y
            new_x = max(-500, min(500, new_x))
            new_y = max(-50, min(200, new_y))
            ender_dragon.goto(new_x, new_y)
        
        # 物品拾取检测
        for i in range(len(items_on_ground)-1, -1, 1):
            item = items_on_ground[i]
            distance = math.sqrt(
                (item["x"] - player_x)**2 + 
                (item["y"] - player_y)** 2
            )
            
            if distance < 30:  # 拾取范围
                # 添加到物品栏
                inventory[item["type"]] = inventory.get(item["type"], 0) + item["count"]
                # 自动添加到快捷栏
                if item["type"] not in hotbar:
                    for j in range(9):
                        if hotbar[j] is None:
                            hotbar[j] = item["type"]
                            break
                # 移除地面物品
                item["pen"].hideturtle()
                items_on_ground.pop(i)
                play_sound("pickup")
                draw_control_bar()
        
        screen.update()
        time.sleep(0.3 if dimension != "末地" else 0.2)  # 末地实体更快

def update_light_level():
    """根据时间更新光照强度"""
    global light_level
    if dimension == "主世界":
        if 0 <= time_of_day < 1000:  # 日出
            light_level = time_of_day / 1000
        elif 1000 <= time_of_day < 12000:  # 白天
            light_level = 1.0
        elif 12000 <= time_of_day < 14000:  # 黄昏
            light_level = 1 - (time_of_day - 12000) / 2000
        else:  # 夜晚
            light_level = max(0.1, 0.3 - (time_of_day - 14000) / 10000)
    elif dimension == "下界":
        light_level = 0.5  # 下界固定光照
    elif dimension == "末地":
        light_level = 0.7  # 末地固定光照
    
    # 天气影响光照
    if weather == "rain" or weather == "thunder":
        light_level *= 0.8
    
    # 重新渲染可见方块以更新光照
    start_x = round(player_x / BLOCK_SIZE) * BLOCK_SIZE - render_distance * BLOCK_SIZE
    end_x = round(player_x / BLOCK_SIZE) * BLOCK_SIZE + render_distance * BLOCK_SIZE
    
    for z in blocks:
        for (x, y), block_type in blocks[z].items():
            if start_x <= x <= end_x:
                draw_block(x, y, z, block_type, force=True)

def update_effects():
    """更新状态效果"""
    current_time = time.time()
    to_remove = []
    
    # 检查效果是否过期
    for i, effect in enumerate(player_effects):
        if current_time > effect["end_time"]:
            to_remove.append(i)
    
    # 移除过期效果
    for i in reversed(to_remove):
        player_effects.pop(i)
    
    # 应用持续效果
    speed_bonus = 1.0
    strength_bonus = 1.0
    
    for effect in player_effects:
        if effect["effect"] == "speed":
            speed_bonus = 1.0 + 0.2 * effect["amplifier"]
        elif effect["effect"] == "strength":
            strength_bonus = 1.0 + 0.3 * effect["amplifier"]
        elif effect["effect"] == "regeneration" and int(current_time) % 2 == 0:
            # 每2秒恢复生命值
            global player_health
            player_health = min(20, player_health + 1)
            draw_control_bar()
    
    return {
        "speed": speed_bonus,
        "strength": strength_bonus
    }

def effect_updater(update_func):
    """状态效果更新循环"""
    while True:
        if is_playing:
            update_func()
        time.sleep(0.5)  # 每0.5秒更新一次

# 生活系统函数
def add_life_systems():
    """添加生活系统（钓鱼、种植等）"""
    # 已经在全局变量中定义了相关内容，这里只提供函数
    
    def plant_seed(x, y, z, seed_type):
        """种植种子"""
        # 检查是否在耕地上
        if z in blocks and (x, y) in blocks[z] and blocks[z][(x, y)] == "farmland":
            # 检查上方是否有空间
            if not (z+1 in blocks and (x, y) in blocks[z+1]):
                plant_type = ITEMS[seed_type]["plant"]
                plants[(x, y, z+1)] = {
                    "type": plant_type,
                    "growth": 0,
                    "watered": False,
                    "last_growth": time.time()
                }
                draw_plant(x, y, z+1, plant_type, 0)
                return True
        return False
    
    def till_soil(x, y, z):
        """耕地（将泥土变为耕地）"""
        if z in blocks and (x, y) in blocks[z] and blocks[z][(x, y)] == "dirt":
            blocks[z][(x, y)] = "farmland"
            draw_block(x, y, z, "farmland", force=True)
            return True
        return False
    
    def open_furnace(x, y):
        """打开熔炉界面"""
        if not is_playing:
            return
            
        furnace_window = Tk()
        furnace_window.title("熔炉")
        furnace_window.geometry("300x300")
        
        # 熔炉界面布局
        Label(furnace_window, text="原料:").grid(row=0, column=0, padx=5, pady=5)
        input_btn = Button(furnace_window, width=5, height=2, bg="#ddd")
        input_btn.grid(row=0, column=1, padx=5, pady=5)
        
        Label(furnace_window, text="燃料:").grid(row=1, column=0, padx=5, pady=5)
        fuel_btn = Button(furnace_window, width=5, height=2, bg="#ddd")
        fuel_btn.grid(row=1, column=1, padx=5, pady=5)
        
        Label(furnace_window, text="产物:").grid(row=2, column=0, padx=5, pady=5)
        output_btn = Button(furnace_window, width=5, height=2, bg="#aaa")
        output_btn.grid(row=2, column=1, padx=5, pady=5)
        
        # 烧制按钮
        def smelt_item():
            """烧制物品逻辑"""
            play_sound("craft")
            messagebox.showinfo("烧制", "物品烧制中...")
            # 这里可以添加实际的烧制逻辑
            
        Button(furnace_window, text="烧制", command=smelt_item).pack(pady=10)
        Button(furnace_window, text="关闭", command=furnace_window.destroy).pack(pady=10)
        
        furnace_window.mainloop()
    
    def start_fishing(x, y):
        """开始钓鱼"""
        if "fishing_rod" not in inventory or inventory["fishing_rod"] <= 0:
            return False
            
        # 检查是否在水边
        block_x = round(x / BLOCK_SIZE) * BLOCK_SIZE
        block_y = round(y / BLOCK_SIZE) * BLOCK_SIZE
        
        if 0 in blocks and (block_x, block_y) in blocks[0] and blocks[0][(block_x, block_y)] == "water":
            # 显示钓鱼动画
            fish_window = Tk()
            fish_window.title("钓鱼中...")
            fish_window.geometry("200x100")
            fish_window.attributes('-topmost', True)
            
            Label(fish_window, text="正在钓鱼...").pack(pady=10)
            
            # 随机时间后钓到鱼
            def catch_fish():
                fish_type = random.choices(
                    ["fish", "salmon", "pufferfish"],
                    weights=[0.6, 0.3, 0.1]
                )[0]
                
                inventory[fish_type] = inventory.get(fish_type, 0) + 1
                # 更新快捷栏
                if fish_type not in hotbar:
                    for i in range(9):
                        if hotbar[i] is None:
                            hotbar[i] = fish_type
                            break
                
                play_sound("pickup")
                messagebox.showinfo("钓鱼", f"你钓到了一条{fish_type}!")
                fish_window.destroy()
                draw_control_bar()
            
            # 2-8秒后钓到鱼
            fish_window.after(random.randint(2000, 8000), catch_fish)
            return True
        return False
    
    # 启动植物生长更新线程
    threading.Thread(target=lambda: plant_updater(update_plants), daemon=True).start()
    
    return {
        "plant_seed": plant_seed,
        "till_soil": till_soil,
        "open_furnace": open_furnace,
        "start_fishing": start_fishing
    }

# 维度和生物函数
def add_more_dimensions_and_mobs():
    """添加更多维度和特殊生物"""
    def generate_dimension(dim):
        """生成特定维度的地形"""
        global dimension
        dimension = dim
        
        # 设置天空颜色
        screen.bgcolor(dimensions[dim]["sky_color"])
        
        # 清空现有方块
        for z in blocks:
            for (x, y) in list(blocks[z].keys()):
                remove_block(x, y, z)
        
        # 根据维度生成地形
        if dim == "天堂":
            generate_heaven_terrain()
        elif dim == "深渊":
            generate_abyss_terrain()
        elif dim == "下界":
            generate_nether_terrain()  # 新增下界地形生成
        elif dim == "末地":
            generate_end_terrain()  # 新增末地地形生成
        
        # 生成维度特定生物
        spawn_dimension_mobs(dim)
    
    def generate_heaven_terrain():
        """生成天堂地形"""
        start_x = round(player_x / BLOCK_SIZE) * BLOCK_SIZE - render_distance * BLOCK_SIZE
        end_x = round(player_x / BLOCK_SIZE) * BLOCK_SIZE + render_distance * BLOCK_SIZE
        
        # 生成云朵平台
        for x in range(start_x, end_x, BLOCK_SIZE * 5):
            for y in range(-200, 200, BLOCK_SIZE * 8):
                platform_size = random.randint(3, 6)
                for px in range(platform_size):
                    for py in range(platform_size):
                        draw_block(
                            x + px * BLOCK_SIZE, 
                            y + py * BLOCK_SIZE, 
                            0, 
                            "cloud" if random.random() < 0.8 else "holy_stone"
                        )
        
        # 生成漂浮岛屿
        for _ in range(5):
            x = random.randint(start_x, end_x)
            y = random.randint(-100, 200)
            size = random.randint(4, 8)
            
            for px in range(size):
                for py in range(size):
                    if px == 0 or px == size-1 or py == 0 or py == size-1:
                        draw_block(x + px * BLOCK_SIZE, y + py * BLOCK_SIZE, 0, "holy_stone")
                    else:
                        draw_block(x + px * BLOCK_SIZE, y + py * BLOCK_SIZE, 0, "grass")
    
    def generate_abyss_terrain():
        """生成深渊地形"""
        start_x = round(player_x / BLOCK_SIZE) * BLOCK_SIZE - render_distance * BLOCK_SIZE
        end_x = round(player_x / BLOCK_SIZE) * BLOCK_SIZE + render_distance * BLOCK_SIZE
        
        # 生成深渊地面
        for x in range(start_x, end_x, BLOCK_SIZE):
            for y in range(-300, -100, BLOCK_SIZE):
                if random.random() < 0.1:
                    draw_block(x, y, 0, "abyssal_ore")
                else:
                    draw_block(x, y, 0, "abyssal_stone")
        
        # 生成深渊柱体
        for _ in range(10):
            x = random.randint(start_x, end_x)
            y = random.randint(-250, -150)
            height = random.randint(5, 15)
            
            for h in range(height):
                draw_block(x, y + h * BLOCK_SIZE, 0, "abyssal_stone")
    
    # 新增下界地形生成
    def generate_nether_terrain():
        """生成下界地形"""
        start_x = round(player_x / BLOCK_SIZE) * BLOCK_SIZE - render_distance * BLOCK_SIZE
        end_x = round(player_x / BLOCK_SIZE) * BLOCK_SIZE + render_distance * BLOCK_SIZE
        
        # 生成下界地面
        for x in range(start_x, end_x, BLOCK_SIZE):
            for y in range(-300, -100, BLOCK_SIZE):
                if random.random() < 0.05:
                    draw_block(x, y, 0, "nether_brick")
                else:
                    draw_block(x, y, 0, "netherrack")
        
        # 生成下界熔岩池和柱体
        for _ in range(8):
            x = random.randint(start_x, end_x)
            y = random.randint(-250, -150)
            height = random.randint(3, 10)
            
            for h in range(height):
                draw_block(x, y + h * BLOCK_SIZE, 0, "netherrack")
    
    # 新增末地地形生成
    def generate_end_terrain():
        """生成末地地形"""
        start_x = round(player_x / BLOCK_SIZE) * BLOCK_SIZE - render_distance * BLOCK_SIZE
        end_x = round(player_x / BLOCK_SIZE) * BLOCK_SIZE + render_distance * BLOCK_SIZE
        
        # 生成末地石平台
        for x in range(start_x, end_x, BLOCK_SIZE):
            for y in range(-200, 0, BLOCK_SIZE):
                draw_block(x, y, 0, "end_stone")
        
        # 生成黑曜石平台（末影龙战斗平台）
        for x in range(-100, 100, BLOCK_SIZE):
            for y in range(-50, 50, BLOCK_SIZE):
                draw_block(x, y, 0, "obsidian")
        
        # 生成末地塔
        for _ in range(3):
            x = random.randint(start_x, end_x)
            y = -200
            height = random.randint(10, 20)
            
            for h in range(height):
                draw_block(x, y + h * BLOCK_SIZE, 0, "end_stone")
    
    def spawn_dimension_mobs(dim):
        """在特定维度生成生物"""
        global monsters, animals
        
        # 清空现有生物
        for monster in monsters:
            monster["pen"].hideturtle()
        monsters.clear()
        
        for animal in animals:
            animal["pen"].hideturtle()
        animals.clear()
        
        # 生成维度特定生物
        if dim == "天堂":
            # 天使和和平生物
            for i in range(3):
                x = random.randint(-500, 500)
                y = random.randint(-100, 200)
                
                animals.append({
                    "x": x, "y": y, "pen": animal_pens[i], 
                    "health": 15, "type": "angel",
                    "target_x": x, "target_y": y
                })
                animal_pens[i].color((255, 255, 204))
                animal_pens[i].goto(x, y)
                animal_pens[i].showturtle()
        
        elif dim == "深渊":
            # 深渊怪物
            for i in range(5):
                x = random.randint(-500, 500)
                y = random.randint(-250, -100)
                
                monsters.append({
                    "x": x, "y": y, "pen": monster_pens[i], 
                    "health": 30, "type": "abyssal_demon",
                    "target_x": x, "target_y": y,
                    "aggro": True
                })
                monster_pens[i].color((75, 0, 130))
                monster_pens[i].goto(x, y)
                monster_pens[i].showturtle()
            
            # 生成深渊领主（Boss）
            spawn_boss("深渊领主", -200, -200)
        
        # 新增下界生物生成
        elif dim == "下界":
            for i in range(6):
                x = random.randint(-500, 500)
                y = random.randint(-250, -50)
                
                monster_type = "zombie_pigman" if random.random() < 0.5 else "ghast"
                monsters.append({
                    "x": x, "y": y, "pen": monster_pens[i], 
                    "health": 20 if monster_type == "zombie_pigman" else 40, 
                    "type": monster_type,
                    "target_x": x, "target_y": y,
                    "aggro": False if monster_type == "zombie_pigman" else True
                })
                color = (139, 69, 19) if monster_type == "zombie_pigman" else (200, 100, 100)
                monster_pens[i].color(color)
                monster_pens[i].goto(x, y)
                monster_pens[i].showturtle()
            
            # 生成凋灵（Boss）
            spawn_boss("凋灵", 0, -100)
        
        # 新增末地生物生成
        elif dim == "末地":
            for i in range(4):
                x = random.randint(-500, 500)
                y = random.randint(-100, 100)
                
                monsters.append({
                    "x": x, "y": y, "pen": monster_pens[i], 
                    "health": 40, "type": "enderman",
                    "target_x": x, "target_y": y,
                    "aggro": False
                })
                monster_pens[i].color((100, 0, 200))
                monster_pens[i].goto(x, y)
                monster_pens[i].showturtle()
            
            # 显示末影龙
            ender_dragon.goto(0, 100)
            ender_dragon.showturtle()
    
    def spawn_boss(boss_type, x, y):
        """生成Boss生物"""
        if boss_type not in bosses:
            return
            
        boss_data = bosses[boss_type]
        boss_pen.clear()
        boss_pen.color(boss_data["color"])
        boss_pen.shapesize(boss_data["size"], boss_data["size"])
        boss_pen.goto(x, y)
        boss_pen.showturtle()
        
        monsters.append({
            "x": x, "y": y, "pen": boss_pen, 
            "health": boss_data["health"], "type": boss_type,
            "target_x": x, "target_y": y,
            "aggro": True,
            "is_boss": True
        })
        
        play_sound("dragon")  # 使用末影龙音效作为Boss出现音效
    
    return {
        "generate_dimension": generate_dimension,
        "spawn_boss": spawn_boss
    }

# 箱子功能
def add_chest_functionality():
    """添加箱子方块和交互逻辑"""
    def open_chest(x, y):
        """打开箱子界面"""
        if not is_playing:
            return
            
        chest_window = Tk()
        chest_window.title("箱子")
        chest_window.geometry("300x300")
        
        # 箱子有27个槽位(3x9)
        chest_frame = Frame(chest_window)
        chest_frame.pack(pady=10)
        
        for i in range(3):
            for j in range(9):
                btn = Button(chest_frame, width=5, height=2, bg="#ddd")
                btn.grid(row=i, column=j, padx=2, pady=2)
        
        # 关闭按钮
        Button(chest_window, text="关闭", command=chest_window.destroy).pack(pady=10)
        chest_window.mainloop()
    
    return open_chest

# 床和睡眠功能
def add_bed_functionality():
    """添加床和睡眠功能"""
    def sleep_in_bed():
        """睡眠功能，跳过夜晚"""
        global time_of_day, is_playing
        
        if not is_playing or 0 <= time_of_day < 12000:
            return False
            
        # 播放睡觉音效
        play_sound("sleep")
        
        # 快速将时间设置为第二天
        time_of_day = 0
        update_light_level()
        draw_control_bar()
        
        # 清除所有怪物
        for monster in monsters:
            monster["health"] = 0
            monster["pen"].hideturtle()
        monsters.clear()
        
        return True
    
    return sleep_in_bed

# 初始化高级功能
def init_advanced_features():
    """初始化所有高级功能"""
    redstone_system = {
        "update_redstone": update_redstone
    }
    potion_system = {}
    dimension_system = add_more_dimensions_and_mobs()
    life_system = add_life_systems()
    chest_system = add_chest_functionality()
    bed_system = add_bed_functionality()
    
    # 添加新按钮到界面
    buttons["redstone_guide"] = {"x": 400, "y": 240, "width": 100, "height": 30, "text": "红石指南"}
    buttons["brew_guide"] = {"x": 510, "y": 240, "width": 100, "height": 30, "text": "酿造指南"}
    buttons["heaven"] = {"x": 620, "y": 240, "width": 100, "height": 30, "text": "天堂"}
    buttons["abyss"] = {"x": 730, "y": 240, "width": 100, "height": 30, "text": "深渊"}
    buttons["nether"] = {"x": 400, "y": 180, "width": 100, "height": 30, "text": "下界"}  # 新增下界按钮
    buttons["end"] = {"x": 510, "y": 180, "width": 100, "height": 30, "text": "末地"}  # 新增末地按钮
    buttons["fishing"] = {"x": 840, "y": 320, "width": 100, "height": 30, "text": "钓鱼"}
    buttons["multiplayer"] = {"x": 840, "y": 240, "width": 100, "height": 30, "text": "多人游戏"}
    
    # 更新控制栏绘制函数以包含新按钮
    global draw_control_bar
    original_draw_control_bar = draw_control_bar
    
    def new_draw_control_bar():
        original_draw_control_bar()
        # 绘制新添加的按钮
        draw_button("redstone_guide")
        draw_button("brew_guide")
        draw_button("heaven")
        draw_button("abyss")
        draw_button("nether")  # 绘制下界按钮
        draw_button("end")     # 绘制末地按钮
        draw_button("fishing")
        draw_button("multiplayer")
    
    draw_control_bar = new_draw_control_bar
    
    # 更新点击处理函数以支持新功能
    global handle_click
    original_handle_click = handle_click

    
    def new_handle_click(x, y):
        original_handle_click(x, y)
        if not is_playing:
            return
            
        # 处理新添加的按钮点击
        if (buttons["heaven"]["x"] <= x <= buttons["heaven"]["x"] + buttons["heaven"]["width"] and 
            buttons["heaven"]["y"] <= y <= buttons["heaven"]["y"] + buttons["heaven"]["height"]):
            play_sound("click")
            dimension_system["generate_dimension"]("天堂")
            
        elif (buttons["abyss"]["x"] <= x <= buttons["abyss"]["x"] + buttons["abyss"]["width"] and 
              buttons["abyss"]["y"] <= y <= buttons["abyss"]["y"] + buttons["abyss"]["height"]):
            play_sound("click")
            dimension_system["generate_dimension"]("深渊")
            
        elif (buttons["nether"]["x"] <= x <= buttons["nether"]["x"] + buttons["nether"]["width"] and 
              buttons["nether"]["y"] <= y <= buttons["nether"]["y"] + buttons["nether"]["height"]):
            play_sound("click")
            dimension_system["generate_dimension"]("下界")  # 下界维度切换
            
        elif (buttons["end"]["x"] <= x <= buttons["end"]["x"] + buttons["end"]["width"] and 
              buttons["end"]["y"] <= y <= buttons["end"]["y"] + buttons["end"]["height"]):
            play_sound("click")
            dimension_system["generate_dimension"]("末地")  # 末地维度切换
            
        elif (buttons["fishing"]["x"] <= x <= buttons["fishing"]["x"] + buttons["fishing"]["width"] and 
              buttons["fishing"]["y"] <= y <= buttons["fishing"]["y"] + buttons["fishing"]["height"]):
            play_sound("click")
            life_system["start_fishing"](x, y)
    
    handle_click = new_handle_click
    
    return {
        "redstone": redstone_system,
        "potions": potion_system,
        "dimensions": dimension_system,
        "life": life_system,
        "chest": chest_system,
        "bed": bed_system
    }

# 事件处理
def handle_click(x, y):
    """处理鼠标点击"""
    global is_playing, player_x, player_y
    
    if not is_playing:
        # 处理菜单点击
        if ("start" in buttons and 
            buttons["start"]["x"] <= x <= buttons["start"]["x"] + buttons["start"]["width"] and 
            buttons["start"]["y"] <= y <= buttons["start"]["y"] + buttons["start"]["height"]):
            start_game()
        elif ("quit" in buttons and 
              buttons["quit"]["x"] <= x <= buttons["quit"]["x"] + buttons["quit"]["width"] and 
              buttons["quit"]["y"] <= y <= buttons["quit"]["y"] + buttons["quit"]["height"]):
            screen.bye()
        return
    
    # 游戏中的点击处理（放置/破坏方块等）
    block_x = round(x / BLOCK_SIZE) * BLOCK_SIZE
    block_y = round(y / BLOCK_SIZE) * BLOCK_SIZE
    
    # 简化的方块放置/破坏逻辑
    if y < 300:  # 点击游戏区域
        if (0 in blocks and (block_x, block_y) in blocks[0]):
            # 破坏方块
            block_type = blocks[0][(block_x, block_y)]
            remove_block(block_x, block_y, 0)
            spawn_item(block_x, block_y, BLOCK_TYPES[block_type]["drop"], 1)
        else:
            # 放置方块（默认为泥土，可以根据选择的快捷栏物品更改）
            # 这里简化处理，实际应根据当前选中的物品放置对应的方块
            draw_block(block_x, block_y, 0, "dirt")

def handle_key_press(key):
    """处理键盘按键"""
    global player_x, player_y, player_health, player_hunger, is_playing, time_of_day
    
    if not is_playing:
        return
        
    speed = BLOCK_SIZE // 2
    effects = update_effects()
    speed *= effects["speed"]
    
    # 处理特殊方块的影响
    current_block_x = round(player_x / BLOCK_SIZE) * BLOCK_SIZE
    current_block_y = round(player_y / BLOCK_SIZE) * BLOCK_SIZE
    current_block_type = blocks.get(0, {}).get((current_block_x, current_block_y), None)
    
    # 冰面会增加移动速度
    if current_block_type == "ice":
        speed *= 1.5
    
    # 仙人掌会造成伤害
    if current_block_type == "cactus":
        player_health = max(0, player_health - 0.1)
        draw_control_bar()
    
    # 移动控制
    if key == "w":
        new_y = player_y + speed
        if not is_colliding(player_x, new_y, 0):
            player_y = new_y
    elif key == "s":
        new_y = player_y - speed
        if not is_colliding(player_x, new_y, 0):
            player_y = new_y
    elif key == "a":
        new_x = player_x - speed
        if not is_colliding(new_x, player_y, 0):
            player_x = new_x
    elif key == "d":
        new_x = player_x + speed
        if not is_colliding(new_x, player_y, 0):
            player_x = new_x
    elif key == "Escape":
        draw_main_menu()
    elif key == "space":
        # 跳跃
        player_y += BLOCK_SIZE
    elif key == "e":
        # 打开背包
        pass
    elif key == "c":
        # 打开合成界面
        pass
    
    # 更新玩家位置
    player_pen.goto(player_x, player_y)
    
    # 更新饥饿值
    player_hunger = max(0, player_hunger - 0.01)
    if player_hunger <= 0:
        player_health = max(0, player_health - 0.01)
    
    draw_control_bar()

def start_game():
    """开始游戏"""
    global is_playing, player_x, player_y, player_health, player_hunger, time_of_day
    
    is_playing = True
    player_x, player_y = 0, 0
    player_health = 20
    player_hunger = 20
    time_of_day = 0
    screen.bgcolor(dimensions["主世界"]["sky_color"])
    
    # 清空数据结构
    blocks.clear()
    inventory.clear()
    hotbar[:] = [None] * 9
    players.clear()
    animals.clear()
    monsters.clear()
    items_on_ground.clear()
    plants.clear()
    
    # 生成初始地形
    generate_terrain()
    
    # 添加玩家
    add_player("local_player", 0, 0, 0, is_local=True)
    
    # 初始化高级功能
    init_advanced_features()
    
    # 绘制控制栏
    draw_control_bar()
    
    # 显示玩家
    player_pen.goto(0, 0)
    player_pen.showturtle()
    
    # 启动各种更新线程
    threading.Thread(target=lambda: redstone_updater(update_redstone), daemon=True).start()
    threading.Thread(target=lambda: effect_updater(update_effects), daemon=True).start()
    threading.Thread(target=entity_behavior, daemon=True).start()
    threading.Thread(target=selection_box_updater, daemon=True).start()
    threading.Thread(target=time_updater, daemon=True).start()

def generate_terrain():
    """生成初始地形"""
    # 生成地面
    for x in range(-500, 500, BLOCK_SIZE):
        for y in range(-300, -200, BLOCK_SIZE):
            draw_block(x, y, 0, "bedrock")
    
    for x in range(-500, 500, BLOCK_SIZE):
        for y in range(-200, -100, BLOCK_SIZE):
            draw_block(x, y, 0, "stone")
    
    for x in range(-500, 500, BLOCK_SIZE):
        draw_block(x, -100, 0, "dirt")
        draw_block(x, -80, 0, "grass")
    
    # 生成一些树木
    for _ in range(10):
        x = random.randint(-450, 450)
        y = -80
        height = random.randint(3, 5)
        
        # 树干
        for h in range(height):
            draw_block(x, y + h * BLOCK_SIZE, 0, "wood")
        
        # 树叶
        for dx in [-BLOCK_SIZE, 0, BLOCK_SIZE]:
            for dy in [height * BLOCK_SIZE, (height + 1) * BLOCK_SIZE]:
                draw_block(x + dx, y + dy, 0, "leaves")
    
    # 生成一些水
    for x in range(-200, 200, BLOCK_SIZE):
        for y in range(-150, -120, BLOCK_SIZE):
            draw_block(x, y, 0, "water")
    
    # 添加新方块到地形中
    # 生成一些雪地
    for x in range(-400, -300, BLOCK_SIZE):
        for y in range(-80, 20, BLOCK_SIZE):
            draw_block(x, y, 0, "snow")
    
    # 生成一些沙漠（沙子）
    for x in range(300, 400, BLOCK_SIZE):
        for y in range(-80, 50, BLOCK_SIZE):
            draw_block(x, y, 0, "sand")
            if random.random() < 0.1 and y < 0:  # 偶尔生成仙人掌
                draw_block(x, y + BLOCK_SIZE, 0, "cactus")
    
    # 生成一些黏土
    for x in range(-300, -200, BLOCK_SIZE):
        for y in range(-130, -110, BLOCK_SIZE):
            draw_block(x, y, 0, "clay")
    
    # 生成一些矿石
    for _ in range(5):
        x = random.randint(-450, 450)
        y = random.randint(-180, -120)
        ore_type = random.choice(["iron_ore", "gold_ore", "coal_ore"])
        draw_block(x, y, 0, ore_type)
    
    # 稀有矿石
    for _ in range(2):
        x = random.randint(-450, 450)
        y = random.randint(-190, -150)
        ore_type = random.choice(["diamond_ore", "emerald_ore", "lapis_ore"])
        draw_block(x, y, 0, ore_type)

def time_updater():
    """时间更新器"""
    global time_of_day, weather
    while True:
        if is_playing:
            time_of_day = (time_of_day + 1) % 24000
            if time_of_day % 100 == 0:
                update_light_level()
                draw_control_bar()
            
            # 随机天气变化
            if time_of_day % 1000 == 0 and random.random() < 0.01:
                weather = "rain" if weather == "clear" else "clear"
        
        time.sleep(0.1)

# 主函数
def main():
    """主函数"""
    draw_main_menu()
    
    # 设置事件监听
    screen.onscreenclick(handle_click)
    screen.onkeypress(lambda: handle_key_press("w"), "w")
    screen.onkeypress(lambda: handle_key_press("s"), "s")
    screen.onkeypress(lambda: handle_key_press("a"), "a")
    screen.onkeypress(lambda: handle_key_press("d"), "d")
    screen.onkeypress(lambda: handle_key_press("Left"), "Left")
    screen.onkeypress(lambda: handle_key_press("Right"), "Right")
    screen.onkeypress(lambda: handle_key_press("Delete"), "Delete")
    screen.onkeypress(lambda: handle_key_press("x"), "x")
    screen.onkeypress(lambda: handle_key_press("Escape"), "Escape")
    screen.onkeypress(lambda: handle_key_press("space"), "space")
    screen.onkeypress(lambda: handle_key_press("c"), "c")
    screen.onkeypress(lambda: handle_key_press("e"), "e")
    screen.onkeypress(lambda: handle_key_press("v"), "v")
    for i in range(1, 10):
        screen.onkeypress(lambda num=i: handle_key_press(str(num)), str(i))
    screen.listen()
    
    turtle.done()

if __name__ == "__main__":
    main()
