import turtle
import random
import time
import json
import os
import winsound
from tkinter import simpledialog, messagebox, Tk, Frame, Button, Label
import threading
import math
from collections import defaultdict

# 确保中文显示正常
turtle.rcParams = {"font.family": ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]}

# 隐藏Tkinter主窗口
root = Tk()
root.withdraw()

# 目录设置
SAVE_DIR = "minecraft_saves"
SOUND_DIR = "minecraft_sounds"
for dir_path in [SAVE_DIR, SOUND_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

# 音效设置
SOUNDS = {
    "click": os.path.join(SOUND_DIR, "click.wav"),
    "place_block": os.path.join(SOUND_DIR, "place_block.wav"),
    "break_block": os.path.join(SOUND_DIR, "break_block.wav"),
    "ambient": os.path.join(SOUND_DIR, "ambient.wav"),
    "monster": os.path.join(SOUND_DIR, "monster.wav"),
    "dragon": os.path.join(SOUND_DIR, "dragon.wav"),
    "attack": os.path.join(SOUND_DIR, "attack.wav"),
    "jump": os.path.join(SOUND_DIR, "jump.wav"),
    "craft": os.path.join(SOUND_DIR, "craft.wav"),
    "day": os.path.join(SOUND_DIR, "day.wav"),
    "night": os.path.join(SOUND_DIR, "night.wav")
}

# 全局变量
current_world = None
is_playing = False
game_mode = "生存"  # 生存/创造
player_x, player_y = 0, -100
dimension = "主世界"  # 主世界/下界/末地
monsters = []
player_health = 20
player_hunger = 20
inventory = defaultdict(int)  # 物品栏
hotbar = [None]*9  # 快捷栏
selected_slot = 0  # 选中的快捷栏槽位
blocks = {}  # 跟踪所有方块
recipes = {}  # 合成配方
time_of_day = 0  # 0-24000，模拟昼夜
weather = "clear"  # 天气：clear/rain/thunder

# 画布设置
screen = turtle.Screen()
screen.title("我的世界 - Turtle版")
screen.setup(width=1200, height=800)
screen.bgcolor("#87CEEB")
screen.tracer(0)
screen.colormode(255)  # 允许RGB颜色

# 创建画笔
pen = turtle.Turtle()
pen.speed(0)
pen.hideturtle()
pen.penup()

# 按钮画笔
button_pen = turtle.Turtle()
button_pen.speed(0)
button_pen.hideturtle()
button_pen.penup()

# 文本画笔
text_pen = turtle.Turtle()
text_pen.speed(0)
text_pen.hideturtle()
text_pen.penup()

# 玩家画笔
player_pen = turtle.Turtle()
player_pen.speed(0)
player_pen.shape("square")
player_pen.color("#FFD700")
player_pen.shapesize(0.8, 0.8)
player_pen.penup()

# 怪物画笔
monster_pens = [turtle.Turtle() for _ in range(8)]
for pen in monster_pens:
    pen.speed(0)
    pen.shape("square")
    pen.color("#FF0000")
    pen.shapesize(0.8, 0.8)
    pen.penup()
    pen.hideturtle()

# 末影龙画笔
ender_dragon = turtle.Turtle()
ender_dragon.speed(0)
ender_dragon.shape("square")
ender_dragon.color((75, 0, 130))  # 末影紫色
ender_dragon.shapesize(2, 3)
ender_dragon.penup()
ender_dragon.hideturtle()

# 物品掉落画笔
item_pens = [turtle.Turtle() for _ in range(20)]
for pen in item_pens:
    pen.speed(0)
    pen.shape("square")
    pen.shapesize(0.5, 0.5)
    pen.penup()
    pen.hideturtle()

# 定义游戏参数
BLOCK_SIZE = 20
GRAVITY = 0.5
JUMP_STRENGTH = -10
player_velocity_y = 0
is_on_ground = False
render_distance = 15  # 渲染距离（方块数）

# 定义颜色（带光影和不同状态）
COLORS = {
    "grass": [(124, 252, 0), (112, 224, 0), (102, 204, 0)],
    "dirt": [(139, 69, 19), (125, 60, 15), (110, 52, 11)],
    "stone": [(169, 169, 169), (153, 153, 153), (136, 136, 136)],
    "water": [(30, 144, 255), (28, 134, 238), (24, 116, 205)],
    "sand": [(244, 164, 96), (230, 149, 80), (216, 132, 64)],
    "wood": [(222, 184, 135), (210, 180, 140), (193, 154, 107)],
    "leaf": [(34, 139, 34), (32, 128, 32), (30, 122, 30)],
    "bedrock": [(68, 68, 68), (58, 58, 58), (51, 51, 51)],
    "diamond": [(176, 226, 255), (151, 216, 255), (129, 205, 255)],
    "iron": [(192, 192, 192), (176, 176, 176), (160, 160, 160)],
    "obsidian": [(42, 0, 69), (36, 0, 59), (31, 0, 51)],
    "end_stone": [(255, 228, 181), (255, 218, 185), (245, 222, 179)],
    "coal": [(30, 30, 30), (25, 25, 25), (20, 20, 20)],
    "gold": [(255, 215, 0), (255, 200, 0), (255, 180, 0)],
    "glass": [(200, 200, 200, 100), (180, 180, 180, 100), (160, 160, 160, 100)],
    "button": (210, 180, 140),
    "button_hover": (245, 222, 179),
    "text": (0, 0, 0),
    "control_bg": (51, 51, 51),
    "control_text": (255, 255, 255),
    "health": (255, 0, 0),
    "hunger": (139, 69, 19),
    "hotbar": (50, 50, 50, 150),
    "hotbar_selected": (200, 200, 200, 150)
}

# 方块类型定义（包含属性）
BLOCK_TYPES = {
    "grass": {"breakable": True, "hardness": 0.6, "drop": "dirt", "tool": None},
    "dirt": {"breakable": True, "hardness": 0.5, "drop": "dirt", "tool": None},
    "stone": {"breakable": True, "hardness": 1.5, "drop": "cobblestone", "tool": "pickaxe"},
    "water": {"breakable": True, "hardness": 100, "drop": None, "tool": "bucket"},
    "sand": {"breakable": True, "hardness": 0.5, "drop": "sand", "tool": None},
    "wood": {"breakable": True, "hardness": 2.0, "drop": "wood", "tool": "axe"},
    "leaf": {"breakable": True, "hardness": 0.2, "drop": None, "tool": "shears"},
    "bedrock": {"breakable": False, "hardness": -1, "drop": None, "tool": None},
    "diamond": {"breakable": True, "hardness": 3.0, "drop": "diamond", "tool": "pickaxe"},
    "iron": {"breakable": True, "hardness": 2.5, "drop": "iron_ore", "tool": "pickaxe"},
    "obsidian": {"breakable": True, "hardness": 50, "drop": "obsidian", "tool": "diamond_pickaxe"},
    "end_stone": {"breakable": True, "hardness": 3.0, "drop": "end_stone", "tool": "pickaxe"},
    "coal": {"breakable": True, "hardness": 2.0, "drop": "coal", "tool": "pickaxe"},
    "gold": {"breakable": True, "hardness": 3.0, "drop": "gold_ore", "tool": "pickaxe"},
    "glass": {"breakable": True, "hardness": 0.3, "drop": None, "tool": None}
}

# 物品定义
ITEMS = {
    # 工具
    "wooden_pickaxe": {"type": "tool", "durability": 59, "mining_level": 1, "material": "wood"},
    "stone_pickaxe": {"type": "tool", "durability": 131, "mining_level": 2, "material": "stone"},
    "iron_pickaxe": {"type": "tool", "durability": 250, "mining_level": 3, "material": "iron"},
    "diamond_pickaxe": {"type": "tool", "durability": 1561, "mining_level": 4, "material": "diamond"},
    
    "wooden_axe": {"type": "tool", "durability": 59, "mining_level": 1, "material": "wood"},
    "stone_axe": {"type": "tool", "durability": 131, "mining_level": 2, "material": "stone"},
    "iron_axe": {"type": "tool", "durability": 250, "mining_level": 3, "material": "iron"},
    "diamond_axe": {"type": "tool", "durability": 1561, "mining_level": 4, "material": "diamond"},
    
    # 武器
    "wooden_sword": {"type": "weapon", "damage": 2, "durability": 59, "material": "wood"},
    "stone_sword": {"type": "weapon", "damage": 3, "durability": 131, "material": "stone"},
    "iron_sword": {"type": "weapon", "damage": 5, "durability": 250, "material": "iron"},
    "diamond_sword": {"type": "weapon", "damage": 7, "durability": 1561, "material": "diamond"},
    
    # 资源
    "diamond": {"type": "resource"},
    "iron_ingot": {"type": "resource"},
    "gold_ingot": {"type": "resource"},
    "coal": {"type": "resource"},
    "cobblestone": {"type": "resource"},
    "stick": {"type": "resource"}
}

# 合成配方
def init_recipes():
    """初始化合成配方"""
    global recipes
    
    # 木棍
    recipes["stick"] = {
        "pattern": [
            ["wood"],
            ["wood"]
        ],
        "result": {"item": "stick", "count": 4}
    }
    
    # 木镐
    recipes["wooden_pickaxe"] = {
        "pattern": [
            ["wood", "wood", "wood"],
            ["", "stick", ""],
            ["", "stick", ""]
        ],
        "result": {"item": "wooden_pickaxe", "count": 1}
    }
    
    # 木剑
    recipes["wooden_sword"] = {
        "pattern": [
            ["wood"],
            ["wood"],
            ["stick"]
        ],
        "result": {"item": "wooden_sword", "count": 1}
    }
    
    # 其他配方可以类似地添加...

# 按钮定义
buttons = {
    "new_world": {"x": -150, "y": 50, "width": 300, "height": 50, "text": "创建新世界"},
    "load_world": {"x": -150, "y": -20, "width": 300, "height": 50, "text": "加载世界"},
    "quit": {"x": -150, "y": -90, "width": 300, "height": 50, "text": "退出游戏"},
    "survival_mode": {"x": 400, "y": 320, "width": 100, "height": 30, "text": "生存模式"},
    "creative_mode": {"x": 510, "y": 320, "width": 100, "height": 30, "text": "创造模式"},
    "overworld": {"x": 400, "y": 280, "width": 100, "height": 30, "text": "主世界"},
    "nether": {"x": 510, "y": 280, "width": 100, "height": 30, "text": "下界"},
    "end": {"x": 620, "y": 280, "width": 100, "height": 30, "text": "末地"},
    "crafting": {"x": 730, "y": 320, "width": 100, "height": 30, "text": "合成"}
}

# 控制栏方块选择按钮
block_buttons = {i: {"x": -550 + i*50, "y": 320, "width": 40, "height": 40, "type": block_type} 
                for i, block_type in enumerate(BLOCK_TYPES.keys())}

def play_sound(sound_name):
    """播放音效"""
    try:
        if os.path.exists(SOUNDS[sound_name]):
            winsound.PlaySound(SOUNDS[sound_name], winsound.SND_ASYNC)
    except:
        pass

def draw_button(button_name, hover=False):
    """绘制按钮"""
    btn = buttons[button_name]
    button_pen.goto(btn["x"], btn["y"])
    button_pen.color(COLORS["text"], COLORS["button_hover"] if hover else COLORS["button"])
    button_pen.begin_fill()
    button_pen.pendown()
    for _ in range(2):
        button_pen.forward(btn["width"])
        button_pen.left(90)
        button_pen.forward(btn["height"])
        button_pen.left(90)
    button_pen.end_fill()
    button_pen.penup()
    
    # 绘制按钮文本
    text_pen.goto(btn["x"] + btn["width"]/2, btn["y"] + btn["height"]/2 - 10)
    text_pen.color(COLORS["text"])
    text_pen.write(btn["text"], align="center", font=("SimHei", 10, "normal"))

def draw_block_button(index, selected=False):
    """绘制方块选择按钮"""
    btn = block_buttons[index]
    block_type = btn["type"]
    button_pen.goto(btn["x"], btn["y"])
    
    # 获取方块颜色
    if block_type in COLORS:
        color = COLORS[block_type][0] if not selected else (255, 255, 255)
    else:
        color = (200, 200, 200) if not selected else (255, 255, 255)
    
    button_pen.color(COLORS["text"], color)
    button_pen.begin_fill()
    button_pen.pendown()
    for _ in range(2):
        button_pen.forward(btn["width"])
        button_pen.left(90)
        button_pen.forward(btn["height"])
        button_pen.left(90)
    button_pen.end_fill()
    button_pen.penup()
    
    if selected:
        button_pen.goto(btn["x"], btn["y"])
        button_pen.color((255, 255, 0))
        button_pen.pensize(2)
        button_pen.pendown()
        for _ in range(2):
            button_pen.forward(btn["width"])
            button_pen.left(90)
            button_pen.forward(btn["height"])
            button_pen.left(90)
        button_pen.penup()
        button_pen.pensize(1)

def draw_hotbar():
    """绘制快捷栏"""
    # 快捷栏背景
    button_pen.goto(-450, -350)
    button_pen.color(COLORS["control_text"], COLORS["hotbar"])
    button_pen.begin_fill()
    button_pen.pendown()
    button_pen.forward(900)
    button_pen.left(90)
    button_pen.forward(50)
    button_pen.left(90)
    button_pen.forward(900)
    button_pen.left(90)
    button_pen.forward(50)
    button_pen.left(90)
    button_pen.end_fill()
    button_pen.penup()
    
    # 快捷栏槽位
    for i in range(9):
        x = -430 + i * 100
        y = -340
        
        # 选中的槽位高亮
        if i == selected_slot:
            button_pen.goto(x - 5, y - 5)
            button_pen.color(COLORS["hotbar_selected"])
            button_pen.begin_fill()
            button_pen.pendown()
            button_pen.forward(40)
            button_pen.left(90)
            button_pen.forward(40)
            button_pen.left(90)
            button_pen.forward(40)
            button_pen.left(90)
            button_pen.forward(40)
            button_pen.left(90)
            button_pen.end_fill()
            button_pen.penup()
        
        # 绘制槽位内容
        item = hotbar[i]
        if item:
            # 绘制物品图标
            button_pen.goto(x, y)
            if item in BLOCK_TYPES:
                color = COLORS[item][0]
            else:
                color = (150, 150, 150)  # 默认颜色
            
            button_pen.color(color)
            button_pen.begin_fill()
            button_pen.pendown()
            button_pen.forward(30)
            button_pen.left(90)
            button_pen.forward(30)
            button_pen.left(90)
            button_pen.forward(30)
            button_pen.left(90)
            button_pen.forward(30)
            button_pen.left(90)
            button_pen.end_fill()
            button_pen.penup()
            
            # 绘制数量
            text_pen.goto(x + 25, y - 5)
            text_pen.color(COLORS["text"])
            text_pen.write(str(inventory[item]), align="right", font=("SimHei", 10, "bold"))
    
    # 绘制快捷栏提示
    text_pen.goto(0, -370)
    text_pen.color(COLORS["control_text"])
    text_pen.write("1-9键切换物品 | E键打开背包", align="center", font=("SimHei", 10, "normal"))

def draw_control_bar():
    """绘制控制栏"""
    # 绘制控制栏背景
    button_pen.goto(-600, 320)
    button_pen.color(COLORS["control_text"], COLORS["control_bg"])
    button_pen.begin_fill()
    button_pen.pendown()
    button_pen.forward(1200)
    button_pen.left(90)
    button_pen.forward(50)
    button_pen.left(90)
    button_pen.forward(1200)
    button_pen.left(90)
    button_pen.forward(50)
    button_pen.left(90)
    button_pen.end_fill()
    button_pen.penup()
    
    # 绘制模式按钮
    draw_button("survival_mode", game_mode == "生存")
    draw_button("creative_mode", game_mode == "创造")
    
    # 绘制维度按钮
    draw_button("overworld", dimension == "主世界")
    draw_button("nether", dimension == "下界")
    draw_button("end", dimension == "末地")
    draw_button("crafting", False)
    
    # 绘制方块选择按钮
    for i in block_buttons:
        draw_block_button(i, i == selected_slot and game_mode == "创造")
    
    # 绘制状态信息
    text_pen.goto(0, 340)
    text_pen.color(COLORS["control_text"])
    time_str = "白天" if 0 <= time_of_day < 12000 else "夜晚"
    text_pen.write(
        f"模式: {game_mode} | 维度: {dimension} | 时间: {time_str} | 天气: {weather}", 
        align="center", 
        font=("SimHei", 12, "normal")
    )
    
    # 绘制生命值条
    text_pen.goto(-500, 340)
    text_pen.color(COLORS["health"])
    text_pen.begin_fill()
    text_pen.pendown()
    text_pen.forward(player_health * 5)
    text_pen.left(90)
    text_pen.forward(10)
    text_pen.left(90)
    text_pen.forward(player_health * 5)
    text_pen.left(90)
    text_pen.forward(10)
    text_pen.left(90)
    text_pen.end_fill()
    text_pen.penup()
    
    # 绘制饥饿值条
    text_pen.goto(-350, 340)
    text_pen.color(COLORS["hunger"])
    text_pen.begin_fill()
    text_pen.pendown()
    text_pen.forward(player_hunger * 5)
    text_pen.left(90)
    text_pen.forward(10)
    text_pen.left(90)
    text_pen.forward(player_hunger * 5)
    text_pen.left(90)
    text_pen.forward(10)
    text_pen.left(90)
    text_pen.end_fill()
    text_pen.penup()
    
    # 绘制快捷栏
    draw_hotbar()

def draw_block(x, y, block_type, force=False):
    """绘制带光影效果的方块并跟踪位置"""
    # 仅在需要更新或首次绘制时才操作
    if not force and (x, y) in blocks and blocks[(x, y)] == block_type:
        return
        
    blocks[(x, y)] = block_type
    pen.goto(x, y)
    
    # 选择颜色（带光影效果）
    color_index = 0
    if (x // BLOCK_SIZE + y // BLOCK_SIZE) % 2 == 0:
        color_index = 1
    if y > player_y:
        color_index = 2
        
    # 处理透明方块（如水和玻璃）
    if block_type in ["water", "glass"]:
        pen.color(COLORS[block_type][color_index])
        pen.pensize(1)
    else:
        pen.color(COLORS[block_type][color_index])
        pen.pensize(1)
        
    pen.begin_fill()
    pen.pendown()
    for _ in range(4):
        pen.forward(BLOCK_SIZE)
        pen.left(90)
    pen.end_fill()
    pen.penup()
    
    # 绘制顶部高光，增强立体感
    pen.goto(x, y)
    pen.color((255, 255, 255, 50))  # 半透明白色
    pen.pendown()
    pen.forward(BLOCK_SIZE)
    pen.left(90)
    pen.forward(BLOCK_SIZE)
    pen.penup()

def remove_block(x, y):
    """移除方块"""
    if (x, y) in blocks:
        block_type = blocks[(x, y)]
        del blocks[(x, y)]
        
        # 用背景色填充
        pen.goto(x, y)
        pen.color(screen.bgcolor())
        pen.begin_fill()
        pen.pendown()
        for _ in range(4):
            pen.forward(BLOCK_SIZE)
            pen.left(90)
        pen.end_fill()
        pen.penup()
        
        # 返回被移除的方块类型
        return block_type
    return None

def is_colliding(x, y):
    """检查碰撞"""
    block_x = round(x / BLOCK_SIZE) * BLOCK_SIZE
    block_y = round(y / BLOCK_SIZE) * BLOCK_SIZE
    return (block_x, block_y) in blocks

def generate_terrain(world_params):
    """生成带不同维度的地形，考虑渲染距离"""
    global blocks
    blocks = {}  # 重置方块跟踪
    pen.clear()
    
    # 根据维度和时间调整天空颜色
    if dimension == "主世界":
        if 0 <= time_of_day < 1000 or 22000 <= time_of_day < 24000:  # 日出/日落
            screen.bgcolor((255, 165, 79))
        elif 1000 <= time_of_day < 12000:  # 白天
            screen.bgcolor((135, 206, 235))
        elif 12000 <= time_of_day < 14000:  # 黄昏
            screen.bgcolor((255, 140, 0))
        else:  # 夜晚
            screen.bgcolor((20, 20, 40))
    elif dimension == "下界":
        screen.bgcolor((139, 0, 0))
    elif dimension == "末地":
        screen.bgcolor((0, 0, 51))
    
    # 只渲染玩家周围一定范围内的方块（提高性能）
    start_x = round(player_x / BLOCK_SIZE) * BLOCK_SIZE - render_distance * BLOCK_SIZE
    end_x = round(player_x / BLOCK_SIZE) * BLOCK_SIZE + render_distance * BLOCK_SIZE
    
    # 绘制地面
    for x in range(start_x, end_x, BLOCK_SIZE):
        # 根据世界参数调整地形高度
        height = random.randint(world_params["min_height"], world_params["max_height"])
        
        # 根据维度调整方块类型
        if dimension == "主世界":
            if random.random() < world_params["sand_chance"] and x % 100 < 200:
                ground_type = "sand"
            else:
                ground_type = "grass"
        elif dimension == "下界":
            ground_type = "stone"
        else:  # 末地
            ground_type = "end_stone"
            
        # 绘制顶层方块
        draw_block(x, -100, ground_type)
        
        # 绘制下层方块
        for i in range(1, height):
            if dimension == "主世界":
                if random.random() < world_params["stone_chance"]:
                    sub_type = "stone"
                else:
                    sub_type = "dirt"
            elif dimension == "下界":
                sub_type = "obsidian" if random.random() < 0.1 else "stone"
            else:  # 末地
                sub_type = "end_stone"
                
            draw_block(x, -100 - i * BLOCK_SIZE, sub_type)
    
    # 生成基岩
    for x in range(start_x, end_x, BLOCK_SIZE):
        for i in range(3):
            draw_block(x, -100 - (world_params["max_height"] + 3 + i) * BLOCK_SIZE, "bedrock")
    
    # 生成矿物资源
    for _ in range(world_params["diamond_count"]):
        x = random.randint(start_x, end_x - BLOCK_SIZE)
        y = -100 - random.randint(5, world_params["max_height"]) * BLOCK_SIZE
        draw_block(x, y, "diamond")
    
    for _ in range(world_params["iron_count"]):
        x = random.randint(start_x, end_x - BLOCK_SIZE)
        y = -100 - random.randint(3, world_params["max_height"]) * BLOCK_SIZE
        draw_block(x, y, "iron")
    
    for _ in range(world_params["coal_count"]):
        x = random.randint(start_x, end_x - BLOCK_SIZE)
        y = -100 - random.randint(2, world_params["max_height"]) * BLOCK_SIZE
        draw_block(x, y, "coal")
    
    # 根据维度生成特色地形
    if dimension == "主世界":
        # 树木
        for _ in range(world_params["tree_count"]):
            x = random.randint(start_x, end_x - BLOCK_SIZE)
            y = -100
            
            trunk_height = random.randint(3, 5)
            for i in range(trunk_height):
                draw_block(x, y + i * BLOCK_SIZE, "wood")
            
            # 树叶
            leaf_size = 3
            for dx in range(-leaf_size, leaf_size + 1):
                for dy in range(1, leaf_size + 1):
                    if abs(dx) + abs(dy) < leaf_size + 1:
                        draw_block(x + dx * BLOCK_SIZE, 
                                  y + trunk_height * BLOCK_SIZE + dy * BLOCK_SIZE, 
                                  "leaf")
        
        # 水域
        for _ in range(world_params["water_count"]):
            x = random.randint(start_x, end_x - BLOCK_SIZE)
            y = -100
            width = random.randint(5, 10)
            depth = random.randint(1, 3)
            
            for w in range(width):
                for d in range(depth):
                    draw_block(x + w * BLOCK_SIZE, y - (d + 1) * BLOCK_SIZE, "water")
    
    elif dimension == "下界":
        # 下界堡垒
        for _ in range(world_params["fortress_count"]):
            x = random.randint(start_x, end_x - BLOCK_SIZE * 8)
            y = -50
            
            width = random.randint(5, 8)
            height = random.randint(3, 5)
            
            for w in range(width):
                for h in range(height):
                    draw_block(x + w * BLOCK_SIZE, y + h * BLOCK_SIZE, "obsidian")
    
    elif dimension == "末地":
        # 末地石塔
        for _ in range(3):
            x = random.randint(start_x, end_x - BLOCK_SIZE)
            y = -100
            
            height = random.randint(10, 20)
            for h in range(height):
                draw_block(x, y + h * BLOCK_SIZE, "end_stone")
            
            # 塔顶
            for dx in range(-2, 3):
                for dy in range(2):
                    draw_block(x + dx * BLOCK_SIZE, y + height * BLOCK_SIZE + dy * BLOCK_SIZE, "end_stone")
        
        # 显示末影龙
        ender_dragon.goto(0, 100)
        ender_dragon.showturtle()
        play_sound("dragon")

def spawn_monsters():
    """生成怪物并确保不与方块重叠"""
    global monsters
    monsters = []
    for i, pen in enumerate(monster_pens):
        # 只在夜晚或特定维度生成怪物
        if (dimension == "主世界" and 13000 <= time_of_day < 23000) or dimension in ["下界", "末地"]:
            # 找到不与方块碰撞的位置
            while True:
                x = random.randint(-530, 530)
                y = random.randint(-100, 200)
                block_x = round(x / BLOCK_SIZE) * BLOCK_SIZE
                block_y = round(y / BLOCK_SIZE) * BLOCK_SIZE
                if (block_x, block_y) not in blocks:
                    break
                    
            # 随机怪物类型
            monster_type = random.choices(
                ["zombie", "skeleton", "creeper"],
                weights=[0.4, 0.4, 0.2]
            )[0]
            
            # 设置怪物颜色
            if monster_type == "zombie":
                color = (255, 0, 0)
            elif monster_type == "skeleton":
                color = (169, 169, 169)
            else:  # creeper
                color = (0, 128, 0)
                
            monsters.append({
                "x": x, "y": y, "pen": pen, 
                "health": 10 if monster_type != "creeper" else 20, 
                "type": monster_type,
                "target_x": x, "target_y": y,
                "aggro": False
            })
            pen.color(color)
            pen.goto(x, y)
            pen.showturtle()
        else:
            pen.hideturtle()

def move_monsters():
    """移动怪物，实现更智能的AI"""
    global player_health, player_hunger
    while is_playing:
        # 简单的怪物AI
        for monster in monsters:
            if monster["health"] <= 0:
                monster["pen"].hideturtle()
                continue
                
            # 检测玩家距离，进入攻击状态
            distance_to_player = math.sqrt(
                (monster["x"] - player_x)**2 + 
                (monster["y"] - player_y)** 2
            )
            
            #  creeper在近距离会爆炸
            if monster["type"] == "creeper" and distance_to_player < 80:
                # 爆炸效果
                monster["health"] = 0
                monster["pen"].hideturtle()
                player_health -= 10
                play_sound("attack")
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
            block_x = round(new_x / BLOCK_SIZE) * BLOCK_SIZE
            block_y = round(new_y / BLOCK_SIZE) * BLOCK_SIZE
            
            # 如果不碰撞则移动
            if (block_x, block_y) not in blocks:
                monster["x"] = new_x
                monster["y"] = new_y
                monster["pen"].goto(new_x, new_y)
            
            # 攻击玩家
            if (abs(monster["x"] - player_x) < BLOCK_SIZE and 
                abs(monster["y"] - player_y) < BLOCK_SIZE):
                player_health -= 1 if monster["type"] == "skeleton" else 2
                player_hunger -= 1
                if player_health <= 0:
                    messagebox.showinfo("游戏结束", "你被怪物击败了!")
                    draw_main_menu()
                play_sound("attack")
                draw_control_bar()
        
        # 末影龙移动（仅在末地）
        if dimension == "末地" and is_playing:
            ender_dragon_x, ender_dragon_y = ender_dragon.xcor(), ender_dragon.ycor()
            
            # 末影龙会追踪玩家
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
        
        screen.update()
        time.sleep(0.3 if dimension != "末地" else 0.2)  # 末地怪物更快

def player_physics():
    """玩家物理系统（重力和碰撞）"""
    global player_y, player_velocity_y, is_on_ground, player_hunger, time_of_day
    while is_playing:
        # 应用重力
        player_velocity_y += GRAVITY
        new_y = player_y + player_velocity_y
        
        # 检查地面碰撞
        block_y = round(new_y / BLOCK_SIZE) * BLOCK_SIZE
        block_x = round(player_x / BLOCK_SIZE) * BLOCK_SIZE
        
        # 检查是否站在方块上
        is_on_ground = (block_x, block_y - BLOCK_SIZE) in blocks
        
        if is_on_ground and player_velocity_y > 0:
            # 落到地面
            player_y = block_y - BLOCK_SIZE
            player_velocity_y = 0
        else:
            # 在空中
            player_y = new_y
            
        # 限制玩家移动范围
        player_x = max(-530, min(530, player_x))
        player_y = max(-300, min(300, player_y))
        
        # 更新玩家位置
        player_pen.goto(player_x, player_y)
        
        # 缓慢减少饥饿值
        if time_of_day % 200 == 0 and is_on_ground:
            player_hunger = max(0, player_hunger - 1)
            # 饥饿值为0时减少生命值
            if player_hunger == 0 and time_of_day % 1000 == 0:
                player_health = max(0, player_health - 1)
                draw_control_bar()
        
        screen.update()
        time.sleep(0.05)

def day_night_cycle():
    """昼夜循环系统"""
    global time_of_day, weather
    while is_playing and dimension == "主世界":
        time_of_day = (time_of_day + 1) % 24000
        
        # 天气变化
        if time_of_day % 10000 == 0:
            weather = random.choice(["clear", "rain", "thunder"])
        
        # 昼夜交替时更新地形和怪物
        if time_of_day % 12000 == 0:
            generate_terrain(current_world["params"])
            spawn_monsters()
            play_sound("day" if time_of_day == 0 else "night")
        
        draw_control_bar()
        time.sleep(0.1)

def open_crafting_menu():
    """打开合成菜单"""
    if not is_playing:
        return
        
    # 创建临时窗口
    craft_window = Tk()
    craft_window.title("合成")
    craft_window.geometry("300x300")
    
    # 创建3x3合成网格
    frame = Frame(craft_window)
    frame.pack(pady=10)
    
    cells = [[None for _ in range(3)] for _ in range(3)]
    
    for i in range(3):
        for j in range(3):
            btn = Button(frame, width=5, height=2, bg="#ddd")
            btn.grid(row=i, column=j, padx=2, pady=2)
            cells[i][j] = btn
    
    # 结果槽位
    result_frame = Frame(craft_window)
    result_frame.pack(pady=10)
    
    Label(result_frame, text="结果:").pack(side="left", padx=5)
    result_btn = Button(result_frame, width=5, height=2, bg="#aaa")
    result_btn.pack(side="left")
    
    # 关闭按钮
    Button(craft_window, text="关闭", command=craft_window.destroy).pack(pady=10)
    
    craft_window.mainloop()

def draw_main_menu():
    """绘制主菜单"""
    global is_playing, ender_dragon
    is_playing = False
    ender_dragon.hideturtle()
    
    # 清空屏幕
    pen.clear()
    button_pen.clear()
    text_pen.clear()
    for pen in monster_pens:
        pen.hideturtle()
    
    # 绘制标题
    text_pen.goto(0, 200)
    text_pen.color(COLORS["text"])
    text_pen.write("我的世界 - Turtle版", align="center", font=("SimHei", 30, "bold"))
    
    # 绘制背景装饰性方块
    for x in range(-500, 500, BLOCK_SIZE*2):
        for y in range(-200, 100, BLOCK_SIZE*2):
            if random.random() < 0.2:
                block_type = random.choice(["grass", "dirt", "stone"])
                draw_block(x, y, block_type, force=True)
    
    # 绘制按钮
    for btn_name in ["new_world", "load_world", "quit"]:
        draw_button(btn_name)
    
    screen.update()

def create_new_world():
    """创建新世界（增加更多参数）"""
    global current_world, is_playing
    
    world_name = simpledialog.askstring("世界名称", "请输入世界名称:")
    if not world_name:
        return
    
    try:
        tree_count = int(simpledialog.askstring("树木数量", "请输入树木数量 (5-30):", initialvalue="15"))
        tree_count = max(5, min(30, tree_count))
        
        water_count = int(simpledialog.askstring("水域数量", "请输入水域数量 (1-5):", initialvalue="3"))
        water_count = max(1, min(5, water_count))
        
        stone_chance = float(simpledialog.askstring("石头概率", "请输入石头出现概率 (0.0-1.0):", initialvalue="0.2"))
        stone_chance = max(0.0, min(1.0, stone_chance))
        
        sand_chance = float(simpledialog.askstring("沙子概率", "请输入沙子出现概率 (0.0-1.0):", initialvalue="0.1"))
        sand_chance = max(0.0, min(1.0, sand_chance))
        
        diamond_count = int(simpledialog.askstring("钻石数量", "请输入钻石矿数量 (3-10):", initialvalue="5"))
        diamond_count = max(3, min(10, diamond_count))
        
        iron_count = int(simpledialog.askstring("铁矿数量", "请输入铁矿数量 (5-20):", initialvalue="10"))
        iron_count = max(5, min(20, iron_count))
        
        coal_count = int(simpledialog.askstring("煤矿数量", "请输入煤矿数量 (10-30):", initialvalue="15"))
        coal_count = max(10, min(30, coal_count))
        
        fortress_count = int(simpledialog.askstring("下界堡垒", "请输入下界堡垒数量 (1-3):", initialvalue="2"))
        fortress_count = max(1, min(3, fortress_count))
        
        min_height = int(simpledialog.askstring("最小高度", "请输入地形最小高度 (2-5):", initialvalue="3"))
        min_height = max(2, min(5, min_height))
        
        max_height = int(simpledialog.askstring("最大高度", "请输入地形最大高度 (6-10):", initialvalue="8"))
        max_height = max(6, min(10, max_height))
        
        if max_height <= min_height:
            max_height = min_height + 3
            
    except:
        messagebox.showerror("输入错误", "请输入有效的数值!")
        return
    
    current_world = {
        "name": world_name,
        "params": {
            "tree_count": tree_count,
            "water_count": water_count,
            "stone_chance": stone_chance,
            "sand_chance": sand_chance,
            "diamond_count": diamond_count,
            "iron_count": iron_count,
            "coal_count": coal_count,
            "fortress_count": fortress_count,
            "min_height": min_height,
            "max_height": max_height
        },
        "seed": random.randint(0, 1000000),
        "time": 0,
        "weather": "clear"
    }
    
    save_path = os.path.join(SAVE_DIR, f"{world_name}.json")
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(current_world, f, ensure_ascii=False, indent=4)
    
    messagebox.showinfo("成功", f"世界 '{world_name}' 创建成功!")
    play_world()

def load_world():
    """加载世界"""
    global current_world
    
    try:
        save_files = [f for f in os.listdir(SAVE_DIR) if f.endswith(".json")]
        if not save_files:
            messagebox.showinfo("提示", "没有保存的世界!")
            return
        
        world_names = [os.path.splitext(f)[0] for f in save_files]
        world_name = simpledialog.askstring("选择世界", 
                                           f"请输入要加载的世界名称:\n{', '.join(world_names)}")
        
        if not world_name or world_name + ".json" not in save_files:
            messagebox.showerror("错误", "世界不存在!")
            return
        
        save_path = os.path.join(SAVE_DIR, f"{world_name}.json")
        with open(save_path, "r", encoding="utf-8") as f:
            current_world = json.load(f)
        
        play_world()
        
    except Exception as e:
        messagebox.showerror("错误", f"加载世界失败: {str(e)}")

def play_world():
    """进入游戏世界"""
    global is_playing, player_x, player_y, dimension, player_health, player_hunger, time_of_day, weather
    is_playing = True
    player_x, player_y = 0, -100
    dimension = "主世界"
    player_health = 20
    player_hunger = 20
    time_of_day = current_world.get("time", 0)
    weather = current_world.get("weather", "clear")
    
    # 初始化物品栏
    global inventory, hotbar
    inventory = defaultdict(int)
    hotbar = [None]*9
    hotbar[0] = "wooden_pickaxe"
    inventory["wooden_pickaxe"] = 1
    hotbar[1] = "wooden_sword"
    inventory["wooden_sword"] = 1
    
    # 清空屏幕
    pen.clear()
    button_pen.clear()
    text_pen.clear()
    
    # 绘制玩家
    player_pen.goto(player_x, player_y)
    player_pen.showturtle()
    
    # 设置随机种子
    random.seed(current_world["seed"])
    
    # 生成地形
    generate_terrain(current_world["params"])
    
    # 生成怪物
    spawn_monsters()
    
    # 启动各种系统线程
    threading.Thread(target=move_monsters, daemon=True).start()
    threading.Thread(target=player_physics, daemon=True).start()
    threading.Thread(target=day_night_cycle, daemon=True).start()
    
    # 初始化合成配方
    init_recipes()
    
    # 绘制控制栏
    draw_control_bar()
    
    # 播放环境音效
    play_sound("ambient")
    
    screen.update()

def attack_monsters():
    """攻击附近的怪物"""
    global monsters
    # 获取当前武器的伤害值
    current_weapon = hotbar[selected_slot]
    if current_weapon in ITEMS and ITEMS[current_weapon]["type"] == "weapon":
        damage = ITEMS[current_weapon]["damage"]
    else:
        damage = 1  # 拳头伤害
    
    for monster in monsters:
        if monster["health"] <= 0:
            continue
            
        # 检查距离
        distance = math.sqrt((monster["x"] - player_x)**2 + (monster["y"] - player_y)** 2)
        if distance < 50:  # 攻击范围
            monster["health"] -= damage
            play_sound("attack")
            if monster["health"] <= 0:
                monster["pen"].hideturtle()
                # 掉落物品
                if random.random() < 0.3:
                    drop_item = "dirt" if random.random() < 0.7 else "stone"
                    inventory[drop_item] += 1
                    # 更新快捷栏
                    if drop_item not in hotbar:
                        for i in range(9):
                            if hotbar[i] is None:
                                hotbar[i] = drop_item
                                break
            draw_control_bar()
            break

def handle_click(x, y):
    """处理鼠标点击"""
    global game_mode, dimension, selected_slot
    
    if not is_playing:
        for btn_name in ["new_world", "load_world", "quit"]:
            btn = buttons[btn_name]
            if (btn["x"] <= x <= btn["x"] + btn["width"] and 
                btn["y"] <= y <= btn["y"] + btn["height"]):
                
                play_sound("click")
                if btn_name == "new_world":
                    create_new_world()
                elif btn_name == "load_world":
                    load_world()
                elif btn_name == "quit":
                    screen.bye()
                    root.destroy()
                    exit()
    else:
        # 控制栏按钮
        for btn_name in ["survival_mode", "creative_mode", "overworld", "nether", "end", "crafting"]:
            btn = buttons[btn_name]
            if (btn["x"] <= x <= btn["x"] + btn["width"] and 
                btn["y"] <= y <= btn["y"] + btn["height"]):
                
                play_sound("click")
                if btn_name == "survival_mode":
                    game_mode = "生存"
                elif btn_name == "creative_mode":
                    game_mode = "创造"
                elif btn_name == "crafting":
                    open_crafting_menu()
                elif btn_name in ["overworld", "nether", "end"]:
                    dimension = "主世界" if btn_name == "overworld" else "下界" if btn_name == "nether" else "末地"
                    generate_terrain(current_world["params"])
                    spawn_monsters()
                draw_control_bar()
                screen.update()
        
        # 方块选择按钮
        for i in block_buttons:
            btn = block_buttons[i]
            if (btn["x"] <= x <= btn["x"] + btn["width"] and 
                btn["y"] <= y <= btn["y"] + btn["height"]):
                
                play_sound("click")
                selected_slot = i
                # 在创造模式下自动添加到快捷栏
                if game_mode == "创造":
                    block_type = btn["type"]
                    hotbar[selected_slot] = block_type
                    inventory[block_type] = 999
                draw_control_bar()
                screen.update()
        
        # 放置方块
        if y < 320:  # 不在控制栏区域
            block_x = round(x / BLOCK_SIZE) * BLOCK_SIZE
            block_y = round(y / BLOCK_SIZE) * BLOCK_SIZE
            
            # 检查是否可以放置
            if (block_x, block_y) not in blocks:
                current_item = hotbar[selected_slot]
                if current_item in BLOCK_TYPES:
                    # 创造模式无限放置
                    if game_mode == "创造":
                        draw_block(block_x, block_y, current_item)
                        play_sound("place_block")
                    # 生存模式需要消耗物品
                    elif game_mode == "生存" and inventory[current_item] > 0:
                        draw_block(block_x, block_y, current_item)
                        inventory[current_item] -= 1
                        if inventory[current_item] == 0:
                            hotbar[selected_slot] = None
                        play_sound("place_block")
                    screen.update()

def handle_key_press(key):
    """处理键盘按键"""
    global player_x, player_y, player_velocity_y, is_on_ground, selected_slot, inventory
    
    if key == "Escape":
        play_sound("click")
        # 保存世界状态
        if current_world:
            current_world["time"] = time_of_day
            current_world["weather"] = weather
            save_path = os.path.join(SAVE_DIR, f"{current_world['name']}.json")
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(current_world, f, ensure_ascii=False, indent=4)
        draw_main_menu()
    elif is_playing:
        step = BLOCK_SIZE
        # 玩家移动
        if key == "Up" or key == "w":
            if is_on_ground:
                player_velocity_y = JUMP_STRENGTH  # 跳跃
                play_sound("jump")
        elif key == "Down" or key == "s":
            player_y -= step//2
        elif key == "Left" or key == "a":
            new_x = player_x - step//2
            if not is_colliding(new_x, player_y):
                player_x = new_x
        elif key == "Right" or key == "d":
            new_x = player_x + step//2
            if not is_colliding(new_x, player_y):
                player_x = new_x
        
        # 破坏方块
        elif key == "Delete" or key == "x":
            block_x = round(player_x / BLOCK_SIZE) * BLOCK_SIZE
            block_y = round(player_y / BLOCK_SIZE) * BLOCK_SIZE
            block_type = remove_block(block_x, block_y)
            
            if block_type and BLOCK_TYPES[block_type]["breakable"]:
                play_sound("break_block")
                # 处理方块掉落
                drop_item = BLOCK_TYPES[block_type]["drop"] or block_type
                if drop_item:
                    inventory[drop_item] += 1
                    # 自动添加到快捷栏
                    if drop_item not in hotbar:
                        for i in range(9):
                            if hotbar[i] is None:
                                hotbar[i] = drop_item
                                break
                draw_control_bar()
        
        # 攻击
        elif key == "space":
            attack_monsters()
            
        # 切换快捷栏
        elif key in [str(i) for i in range(1, 10)]:
            slot = int(key) - 1
            selected_slot = slot
            draw_control_bar()
            
        # 打开合成菜单
        elif key.lower() == "e":
            open_crafting_menu()
        
        # 更新玩家位置
        player_pen.goto(player_x, player_y)
        screen.update()

def main():
    """主函数"""
    draw_main_menu()
    
    # 设置事件监听
    screen.onscreenclick(handle_click)
    screen.onkeypress(lambda: handle_key_press("Up"), "Up")
    screen.onkeypress(lambda: handle_key_press("Down"), "Down")
    screen.onkeypress(lambda: handle_key_press("Left"), "Left")
    screen.onkeypress(lambda: handle_key_press("Right"), "Right")
    screen.onkeypress(lambda: handle_key_press("w"), "w")
    screen.onkeypress(lambda: handle_key_press("s"), "s")
    screen.onkeypress(lambda: handle_key_press("a"), "a")
    screen.onkeypress(lambda: handle_key_press("d"), "d")
    screen.onkeypress(lambda: handle_key_press("Delete"), "Delete")
    screen.onkeypress(lambda: handle_key_press("x"), "x")
    screen.onkeypress(lambda: handle_key_press("Escape"), "Escape")
    screen.onkeypress(lambda: handle_key_press("space"), "space")
    screen.onkeypress(lambda: handle_key_press("e"), "e")
    for i in range(1, 10):
        screen.onkeypress(lambda num=i: handle_key_press(str(num)), str(i))
    screen.listen()
    
    turtle.done()

if __name__ == "__main__":
    main()
    
