import turtle
import pygame
import math
import random
import time
import threading
from tkinter import messagebox

# 初始化pygame
pygame.mixer.init()

# 游戏设置
BLOCK_SIZE = 20
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
render_distance = 10  # 渲染距离（方块数量）

# 玩家属性
player_health = 20
player_hunger = 20

# 游戏状态
is_playing = False
in_main_menu = True
selected_hotbar = 0
last_ambient_time = 0

# 游戏世界
blocks = {}  # {z: {(x, y): block_type}}
plants = {}  # {(x,y,z): {"type": "wheat", "growth": 0, "watered": True, "stage": 0}}
fish = []
recipes = {}
buttons = {}
entities = []  # 生物列表
time_of_day = 0  # 游戏时间 (0-24000)
weather = "clear"  # 当前天气
current_dimension = "主世界"  # 当前维度

# 生物类型定义
ENTITY_TYPES = {
    # 被动生物
    "cow": {
        "health": 10, "speed": 0.2, "width": 1, "height": 1.5,
        "drops": [
            {"item": "leather", "count": (0, 2), "chance": 0.8},
            {"item": "beef", "count": (1, 3), "chance": 1.0}
        ],
        "ai": "passive"
    },
    "pig": {
        "health": 10, "speed": 0.25, "width": 1, "height": 1,
        "drops": [
            {"item": "porkchop", "count": (1, 3), "chance": 1.0}
        ],
        "ai": "passive"
    },
    "sheep": {
        "health": 8, "speed": 0.2, "width": 0.9, "height": 1.3,
        "drops": [
            {"item": "wool", "count": (1, 1), "chance": 1.0},
            {"item": "mutton", "count": (1, 2), "chance": 1.0}
        ],
        "ai": "passive"
    },
    # 敌对生物
    "zombie": {
        "health": 20, "speed": 0.23, "width": 0.6, "height": 1.95,
        "drops": [
            {"item": "rotten_flesh", "count": (0, 2), "chance": 0.8},
            {"item": "iron_ore", "count": (0, 1), "chance": 0.02}
        ],
        "ai": "hostile", "attack": 2, "follow_range": 16
    },
    "skeleton": {
        "health": 20, "speed": 0.25, "width": 0.6, "height": 1.95,
        "drops": [
            {"item": "arrow", "count": (0, 2), "chance": 0.8},
            {"item": "bone", "count": (0, 2), "chance": 0.8}
        ],
        "ai": "hostile", "attack": 1, "range_attack": True, "follow_range": 20
    },
}

# 天气类型定义
WEATHER_TYPES = {
    "clear": {
        "duration": (12000, 24000),  # 10-20分钟
        "sky_color": [(135, 206, 235), (240, 248, 255), (70, 130, 180)],  # 早、中、晚
        "ambient_sound": "ambient_day"
    },
    "rain": {
        "duration": (3000, 15000),  # 2.5-12.5分钟
        "sky_color": [(100, 120, 140), (120, 140, 160), (80, 100, 120)],
        "ambient_sound": "rain",
        "effects": ["crop_growth_boost"]
    },
    "thunder": {
        "duration": (1000, 5000),  # 0.8-4.2分钟
        "sky_color": [(80, 90, 100), (100, 110, 120), (60, 70, 80)],
        "ambient_sound": "thunder",
        "effects": ["crop_growth_boost", "lightning"]
    }
}

# 方块类型定义
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
    "farmland": {"breakable": True, "hardness": 0.6, "drop": "dirt", "tool": None, "transparent": False, "farmable": True},
    "obsidian": {"breakable": True, "hardness": 50, "drop": "obsidian", "tool": "diamond_pickaxe", "transparent": False},
    "composter": {"breakable": True, "hardness": 0.6, "drop": "composter", "tool": None, "transparent": False, "interactive": True},
    # 新增矿石
    "coal_ore": {"breakable": True, "hardness": 1.5, "drop": "coal", "tool": "pickaxe", "transparent": False},
    "iron_ore": {"breakable": True, "hardness": 3.0, "drop": "iron_ore", "tool": "stone_pickaxe", "transparent": False},
    "gold_ore": {"breakable": True, "hardness": 3.0, "drop": "gold_ore", "tool": "iron_pickaxe", "transparent": False},
    "diamond_ore": {"breakable": True, "hardness": 3.0, "drop": "diamond", "tool": "iron_pickaxe", "transparent": False},
    # 新增建筑方块
    "brick": {"breakable": True, "hardness": 2.0, "drop": "brick", "tool": "pickaxe", "transparent": False},
    "stone_brick": {"breakable": True, "hardness": 2.0, "drop": "stone_brick", "tool": "pickaxe", "transparent": False},
    "planks": {"breakable": True, "hardness": 2.0, "drop": "planks", "tool": "axe", "transparent": False},
    "wool": {"breakable": True, "hardness": 0.8, "drop": "wool", "tool": None, "transparent": False},
    # 新增功能方块
    "furnace": {"breakable": True, "hardness": 3.5, "drop": "furnace", "tool": "pickaxe", "transparent": False, "interactive": True},
    "crafting_table": {"breakable": True, "hardness": 2.5, "drop": "crafting_table", "tool": "axe", "transparent": False, "interactive": True},
    "door": {"breakable": True, "hardness": 3.0, "drop": "door", "tool": "axe", "transparent": True, "interactive": True},
    "torch": {"breakable": True, "hardness": 0.1, "drop": "torch", "tool": None, "transparent": True, "light": 15},
    # 新增装饰方块
    "flower": {"breakable": True, "hardness": 0.1, "drop": "flower", "tool": None, "transparent": True},
    "tall_grass": {"breakable": True, "hardness": 0.1, "drop": "grass", "tool": None, "transparent": True},
    "mushroom": {"breakable": True, "hardness": 0.1, "drop": "mushroom", "tool": None, "transparent": True},
    # 下界方块
    "netherrack": {"breakable": True, "hardness": 0.4, "drop": "netherrack", "tool": None, "transparent": False},
    "soul_sand": {"breakable": True, "hardness": 0.5, "drop": "soul_sand", "tool": None, "transparent": False},
    # 末地方块
    "end_stone": {"breakable": True, "hardness": 3.0, "drop": "end_stone", "tool": "pickaxe", "transparent": False},
}

# 物品定义
ITEMS = {
    "wood": {"type": "material"},
    "stick": {"type": "material"},
    "wheat_seeds": {"type": "seed", "plant": "wheat"},
    "wheat": {"type": "food", "hunger": 2},
    "carrot_seeds": {"type": "seed", "plant": "carrot"},
    "carrot": {"type": "food", "hunger": 3},
    "potato_seeds": {"type": "seed", "plant": "potato"},
    "potato": {"type": "food", "hunger": 3},
    "bread": {"type": "food", "hunger": 5},
    # 新增矿石物品
    "coal": {"type": "material"},
    "iron_ore": {"type": "material"},
    "gold_ore": {"type": "material"},
    "diamond": {"type": "material"},
    # 新增建筑材料
    "brick": {"type": "material"},
    "stone_brick": {"type": "material"},
    "planks": {"type": "material"},
    "wool": {"type": "material"},
    # 新增工具
    "wooden_pickaxe": {"type": "tool", "durability": 60, "efficiency": 2},
    "stone_pickaxe": {"type": "tool", "durability": 132, "efficiency": 4},
    "iron_pickaxe": {"type": "tool", "durability": 251, "efficiency": 6},
    "golden_pickaxe": {"type": "tool", "durability": 33, "efficiency": 12},
    "diamond_pickaxe": {"type": "tool", "durability": 1561, "efficiency": 8},
    # 新增功能物品
    "furnace": {"type": "block"},
    "crafting_table": {"type": "block"},
    "door": {"type": "block"},
    "torch": {"type": "block"},
    # 新增装饰物品
    "flower": {"type": "decor"},
    "grass": {"type": "decor"},
    "mushroom": {"type": "decor"},
    # 新增食物
    "beetroot_seeds": {"type": "seed", "plant": "beetroot"},
    "beetroot": {"type": "food", "hunger": 1},
    "beetroot_soup": {"type": "food", "hunger": 6},
    "porkchop": {"type": "food", "hunger": 3},
    "cooked_porkchop": {"type": "food", "hunger": 8},
    "beef": {"type": "food", "hunger": 3},
    "cooked_beef": {"type": "food", "hunger": 8},
    "chicken": {"type": "food", "hunger": 2},
    "cooked_chicken": {"type": "food", "hunger": 6},
    "mutton": {"type": "food", "hunger": 2},
    "cooked_mutton": {"type": "food", "hunger": 6},
    # 下界物品
    "netherrack": {"type": "material"},
    "soul_sand": {"type": "material"},
    # 末地物品
    "end_stone": {"type": "material"},
}

# 颜色定义
COLORS = {
    "grass": [(34, 139, 34), (139, 69, 19), (101, 67, 33)],
    "dirt": [(139, 69, 19), (130, 64, 18), (121, 59, 17)],
    "stone": [(169, 169, 169), (130, 130, 130), (100, 100, 100)],
    "farmland": [(139, 69, 19), (130, 64, 18), (121, 59, 17)],
    # 农作物相关颜色
    "wheat_stage_0": [(150, 150, 150), (140, 140, 140), (130, 130, 130)],
    "wheat_stage_1": [(180, 180, 100), (170, 170, 90), (160, 160, 80)],
    "wheat_stage_2": [(210, 210, 70), (200, 200, 60), (190, 190, 50)],
    "wheat_stage_3": [(240, 240, 40), (230, 230, 30), (220, 220, 20)],
    # 新增矿石颜色
    "coal_ore": [(100, 100, 100), (80, 80, 80), (60, 60, 60)],
    "iron_ore": [(180, 180, 180), (150, 150, 150), (120, 120, 120)],
    "gold_ore": [(255, 215, 0), (200, 180, 0), (180, 160, 0)],
    "diamond_ore": [(0, 255, 255), (0, 200, 200), (0, 180, 180)],
    # 新增建筑方块颜色
    "brick": [(178, 34, 34), (150, 30, 30), (130, 25, 25)],
    "stone_brick": [(169, 169, 169), (130, 130, 130), (100, 100, 100)],
    "planks": [(210, 180, 140), (190, 160, 120), (170, 140, 100)],
    "wool": [(255, 255, 255), (230, 230, 230), (210, 210, 210)],
    # 新增功能方块颜色
    "furnace": [(139, 69, 19), (120, 60, 15), (100, 50, 10)],
    "crafting_table": [(139, 69, 19), (120, 60, 15), (100, 50, 10)],
    "door": [(139, 69, 19), (120, 60, 15), (100, 50, 10)],
    "torch": [(255, 165, 0), (255, 140, 0), (255, 110, 0)],
    # 新增装饰方块颜色
    "flower": [(255, 0, 0), (230, 0, 0), (210, 0, 0)],
    "tall_grass": [(0, 255, 0), (0, 230, 0), (0, 210, 0)],
    "mushroom": [(255, 0, 255), (230, 0, 230), (210, 0, 210)],
    # 下界方块颜色
    "netherrack": [(139, 0, 0), (120, 0, 0), (100, 0, 0)],
    "soul_sand": [(101, 67, 33), (90, 60, 30), (80, 55, 25)],
    # 末地方块颜色
    "end_stone": [(255, 228, 181), (230, 200, 160), (210, 180, 140)],
    # 新增作物颜色
    "carrot_stage_0": [(255, 165, 0), (240, 150, 0), (225, 135, 0)],
    "carrot_stage_1": [(255, 140, 0), (240, 125, 0), (225, 110, 0)],
    "carrot_stage_2": [(255, 110, 0), (240, 95, 0), (225, 80, 0)],
    "carrot_stage_3": [(255, 80, 0), (240, 65, 0), (225, 50, 0)],
    "potato_stage_0": [(100, 200, 100), (90, 190, 90), (80, 180, 80)],
    "potato_stage_1": [(80, 180, 80), (70, 170, 70), (60, 160, 60)],
    "potato_stage_2": [(60, 160, 60), (50, 150, 50), (40, 140, 40)],
    "potato_stage_3": [(40, 140, 40), (30, 130, 30), (20, 120, 20)],
    "beetroot_stage_0": [(255, 0, 0), (230, 0, 0), (210, 0, 0)],
    "beetroot_stage_1": [(255, 50, 50), (230, 30, 30), (210, 20, 20)],
    "beetroot_stage_2": [(255, 100, 100), (230, 80, 80), (210, 60, 60)],
    "beetroot_stage_3": [(255, 150, 150), (230, 130, 130), (210, 110, 110)],
}

# 维度定义
dimensions = {
    "主世界": {"sky_color": (135, 206, 235), "ground_color": (34, 139, 34)},
    "下界": {"sky_color": (139, 0, 0), "ground_color": (101, 67, 33)},
    "末地": {"sky_color": (0, 0, 51), "ground_color": (255, 228, 181)},
}

# 合成配方定义
RECIPES = {
    # 工作台合成
    "crafting_table": {
        "pattern": [
            ["wood", "wood"],
            ["wood", "wood"]
        ],
        "result": {"item": "crafting_table", "count": 1}
    },
    # 木棍合成
    "stick": {
        "pattern": [
            ["wood"],
            ["wood"]
        ],
        "result": {"item": "stick", "count": 4}
    },
    # 木镐合成
    "wooden_pickaxe": {
        "pattern": [
            ["wood", "wood", "wood"],
            [None, "stick", None],
            [None, "stick", None]
        ],
        "result": {"item": "wooden_pickaxe", "count": 1}
    },
    # 石镐合成
    "stone_pickaxe": {
        "pattern": [
            ["cobblestone", "cobblestone", "cobblestone"],
            [None, "stick", None],
            [None, "stick", None]
        ],
        "result": {"item": "stone_pickaxe", "count": 1}
    },
    # 铁镐合成
    "iron_pickaxe": {
        "pattern": [
            ["iron_ore", "iron_ore", "iron_ore"],
            [None, "stick", None],
            [None, "stick", None]
        ],
        "result": {"item": "iron_pickaxe", "count": 1}
    },
    # 熔炉合成
    "furnace": {
        "pattern": [
            ["cobblestone", "cobblestone", "cobblestone"],
            ["cobblestone", None, "cobblestone"],
            ["cobblestone", "cobblestone", "cobblestone"]
        ],
        "result": {"item": "furnace", "count": 1}
    },
    # 门合成
    "door": {
        "pattern": [
            ["wood", "wood"],
            ["wood", "wood"],
            ["wood", "wood"]
        ],
        "result": {"item": "door", "count": 3}
    },
    # 火把合成
    "torch": {
        "pattern": [
            ["coal"],
            ["stick"]
        ],
        "result": {"item": "torch", "count": 4}
    },
    # 砖块合成
    "brick": {
        "pattern": [
            ["stone", "stone"],
            ["stone", "stone"]
        ],
        "result": {"item": "brick", "count": 4}
    },
    # 石砖合成
    "stone_brick": {
        "pattern": [
            ["stone", "stone"],
            ["stone", "stone"]
        ],
        "result": {"item": "stone_brick", "count": 4}
    },
    # 木板合成
    "planks": {
        "pattern": [
            ["wood", "wood"],
            ["wood", "wood"]
        ],
        "result": {"item": "planks", "count": 4}
    },
    # 面包合成
    "bread": {
        "pattern": [
            ["wheat", "wheat", "wheat"]
        ],
        "result": {"item": "bread", "count": 1}
    },
    # 甜菜汤合成
    "beetroot_soup": {
        "pattern": [
            ["beetroot", "beetroot", "beetroot"],
            ["beetroot", None, "beetroot"],
            [None, "wood", None]
        ],
        "result": {"item": "beetroot_soup", "count": 1}
    },
}

# 初始化屏幕
screen = turtle.Screen()
screen.title("Minecraft Ultimate")
screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
screen.setworldcoordinates(-SCREEN_WIDTH/2, -SCREEN_HEIGHT/2, SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
screen.bgcolor(135, 206, 235)
screen.tracer(0)  # 关闭自动刷新

# 创建画笔
pen = turtle.Turtle()
pen.speed(0)
pen.hideturtle()
pen.penup()

# 创建玩家画笔
player_pen = turtle.Turtle()
player_pen.speed(0)
player_pen.shape("triangle")
player_pen.color(0, 0, 0)
player_pen.penup()
player_pen.setheading(90)  # 初始朝向

# 创建选择框画笔
selection_box_pen = turtle.Turtle()
selection_box_pen.speed(0)
selection_box_pen.hideturtle()
selection_box_pen.penup()
selection_box_pen.color(255, 255, 255)

# 主页面按钮
menu_buttons = {
    "start": {"x": -100, "y": 50, "width": 200, "height": 50, "text": "开始游戏"},
    "options": {"x": -100, "y": -50, "width": 200, "height": 50, "text": "选项"},
    "quit": {"x": -100, "y": -150, "width": 200, "height": 50, "text": "退出"}
}

# 生成音效文件
def generate_sounds():
    """生成游戏所需的音效文件"""
    import os
    import wave
    import struct
    
    # 创建音效目录
    if not os.path.exists("sounds"):
        os.makedirs("sounds")
    
    # 音效参数
    sample_rate = 44100
    duration = 0.1
    volume = 32767
    
    # 生成不同音效的频率和持续时间
    sounds = {
        "click": {"freq": 800, "duration": 0.1},
        "walk": {"freq": 440, "duration": 0.2},
        "break_block": {"freq": 220, "duration": 0.3},
        "place_block": {"freq": 330, "duration": 0.2},
        "plant": {"freq": 392, "duration": 0.15},
        "harvest": {"freq": 523, "duration": 0.2},
        "ambient_day": {"freq": 659, "duration": 2.0},
        "ambient_night": {"freq": 320, "duration": 3.0},
        "hurt": {"freq": 220, "duration": 0.5},
        "death": {"freq": 110, "duration": 1.0},
        "rain": {"freq": 1000, "duration": 0.01, "repeat": 100},
        "thunder": {"freq": 100, "duration": 1.0},
        "lightning": {"freq": 2000, "duration": 0.2},
        "hit": {"freq": 660, "duration": 0.1}
    }
    
    for sound_name, params in sounds.items():
        sound_path = f"sounds/{sound_name}.wav"
        
        if not os.path.exists(sound_path):
            print(f"生成音效: {sound_name}.wav")
            
            # 创建WAV文件
            wav_file = wave.open(sound_path, "w")
            wav_file.setnchannels(1)  # 单声道
            wav_file.setsampwidth(2)  # 16位
            wav_file.setframerate(sample_rate)
            
            # 生成音频数据
            num_samples = int(params["duration"] * sample_rate)
            data = []
            
            for i in range(num_samples):
                # 生成正弦波
                t = i / sample_rate
                freq = params["freq"]
                sample = int(volume * math.sin(2 * math.pi * freq * t))
                data.append(struct.pack("<h", sample))
            
            # 如果需要重复音效（如雨声）
            if "repeat" in params:
                data *= params["repeat"]
            
            # 写入数据
            wav_file.writeframes(b"".join(data))
            wav_file.close()

# 播放音效
def play_sound(sound_name):
    """播放音效"""
    try:
        sound = pygame.mixer.Sound(f"sounds/{sound_name}.wav")
        sound.play()
    except Exception as e:
        print(f"播放音效失败: {e}")

# 播放环境音效
def play_ambient_sound():
    """根据时间播放环境音效"""
    global time_of_day, last_ambient_time, weather
    current_time = pygame.time.get_ticks()
    
    # 每30-60秒播放一次环境音效
    if current_time - last_ambient_time > random.randint(30000, 60000):
        last_ambient_time = current_time
        # 根据天气播放环境音效
        if weather == "rain":
            play_sound("rain")
        elif weather == "thunder":
            play_sound("thunder")
        else:
            if 0 <= time_of_day < 12000:  # 白天
                play_sound("ambient_day")
            else:  # 夜晚
                play_sound("ambient_night")

def create_entity(entity_type, x, y):
    """创建生物"""
    entity = {
        "type": entity_type,
        "x": x,
        "y": y,
        "health": ENTITY_TYPES[entity_type]["health"],
        "max_health": ENTITY_TYPES[entity_type]["health"],
        "speed": ENTITY_TYPES[entity_type]["speed"],
        "direction": random.randint(0, 359),
        "state": "idle",  # idle, walking, attacking, following
        "target": None,
        "ticks": 0,
        "pen": turtle.Turtle()
    }
    
    # 设置生物外观
    pen = entity["pen"]
    pen.speed(0)
    pen.penup()
    pen.goto(x, y)
    
    # 根据生物类型设置形状和颜色
    if entity_type == "cow":
        pen.shape("square")
        pen.shapesize(1.5, 1)
        pen.color(255, 255, 255)  # 白色
    elif entity_type == "pig":
        pen.shape("square")
        pen.shapesize(1, 1)
        pen.color(255, 165, 0)  # 橙色
    elif entity_type == "sheep":
        pen.shape("square")
        pen.shapesize(0.9, 0.9)
        pen.color(255, 255, 255)  # 白色
    elif entity_type == "zombie":
        pen.shape("square")
        pen.shapesize(1.95, 0.6)
        pen.color(34, 139, 34)  # 绿色
    elif entity_type == "skeleton":
        pen.shape("square")
        pen.shapesize(1.95, 0.6)
        pen.color(200, 200, 200)  # 灰色
    
    pen.showturtle()
    entities.append(entity)
    return entity

def update_entities():
    """更新所有生物"""
    global player_x, player_y, player_health
    
    for entity in list(entities):
        entity["ticks"] += 1
        entity_type = entity["type"]
        ai_type = ENTITY_TYPES[entity_type]["ai"]
        
        # 被动生物AI
        if ai_type == "passive":
            if entity["state"] == "idle":
                # 随机切换到行走状态
                if random.random() < 0.01:
                    entity["state"] = "walking"
                    entity["direction"] = random.randint(0, 359)
                    entity["ticks"] = 0
            elif entity["state"] == "walking":
                # 移动生物
                rad = math.radians(entity["direction"])
                dx = math.cos(rad) * entity["speed"] * BLOCK_SIZE
                dy = math.sin(rad) * entity["speed"] * BLOCK_SIZE
                
                new_x = entity["x"] + dx
                new_y = entity["y"] + dy
                
                # 检查碰撞
                if not is_colliding(new_x, new_y, 0):
                    entity["x"] = new_x
                    entity["y"] = new_y
                    entity["pen"].goto(new_x, new_y)
                
                # 随机停止行走
                if entity["ticks"] > random.randint(100, 300):
                    entity["state"] = "idle"
        
        # 敌对生物AI
        elif ai_type == "hostile":
            # 计算与玩家的距离
            distance = math.hypot(entity["x"] - player_x, entity["y"] - player_y)
            
            if distance < ENTITY_TYPES[entity_type]["follow_range"]:
                # 追踪玩家
                entity["state"] = "following"
                entity["target"] = (player_x, player_y)
                
                # 计算朝向玩家的方向
                rad = math.atan2(player_y - entity["y"], player_x - entity["x"])
                entity["direction"] = math.degrees(rad)
                
                # 移动生物
                dx = math.cos(rad) * entity["speed"] * BLOCK_SIZE
                dy = math.sin(rad) * entity["speed"] * BLOCK_SIZE
                
                new_x = entity["x"] + dx
                new_y = entity["y"] + dy
                
                # 检查碰撞
                if not is_colliding(new_x, new_y, 0):
                    entity["x"] = new_x
                    entity["y"] = new_y
                    entity["pen"].goto(new_x, new_y)
                
                # 攻击玩家
                if distance < BLOCK_SIZE * 1.5:
                    entity["state"] = "attacking"
                    if entity["ticks"] % 20 == 0:  # 每20 ticks攻击一次
                        take_damage(ENTITY_TYPES[entity_type]["attack"])
            else:
                entity["state"] = "idle"
                # 随机移动
                if random.random() < 0.005:
                    entity["direction"] = random.randint(0, 359)
                
                rad = math.radians(entity["direction"])
                dx = math.cos(rad) * entity["speed"] * BLOCK_SIZE * 0.5
                dy = math.sin(rad) * entity["speed"] * BLOCK_SIZE * 0.5
                
                new_x = entity["x"] + dx
                new_y = entity["y"] + dy
                
                if not is_colliding(new_x, new_y, 0):
                    entity["x"] = new_x
                    entity["y"] = new_y
                    entity["pen"].goto(new_x, new_y)

def draw_entity_health(entity):
    """绘制生物生命值"""
    if entity["health"] < entity["max_health"]:
        x = entity["x"]
        y = entity["y"] + BLOCK_SIZE
        
        # 绘制生命值背景
        pen.goto(x - BLOCK_SIZE/2, y)
        pen.color(100, 100, 100)
        pen.pendown()
        pen.begin_fill()
        pen.forward(BLOCK_SIZE)
        pen.left(90)
        pen.forward(5)
        pen.left(90)
        pen.forward(BLOCK_SIZE)
        pen.left(90)
        pen.forward(5)
        pen.end_fill()
        pen.penup()
        
        # 绘制生命值条
        health_percent = entity["health"] / entity["max_health"]
        pen.goto(x - BLOCK_SIZE/2, y)
        pen.color(255, 0, 0)
        pen.pendown()
        pen.begin_fill()
        pen.forward(BLOCK_SIZE * health_percent)
        pen.left(90)
        pen.forward(5)
        pen.left(90)
        pen.forward(BLOCK_SIZE * health_percent)
        pen.left(90)
        pen.forward(5)
        pen.end_fill()
        pen.penup()

def entity_take_damage(entity, amount):
    """生物受伤"""
    entity["health"] -= amount
    play_sound("hurt")
    
    if entity["health"] <= 0:
        # 生物死亡，掉落物品
        entity_type = entity["type"]
        for drop in ENTITY_TYPES[entity_type]["drops"]:
            if random.random() < drop["chance"]:
                count = random.randint(*drop["count"])
                if count > 0:
                    spawn_item(entity["x"], entity["y"], drop["item"], count)
        
        # 移除生物
        entity["pen"].hideturtle()
        entities.remove(entity)
        play_sound("death")
        return True
    return False

def update_weather():
    """更新天气"""
    global weather, weather_timer
    
    if 'weather_timer' not in globals():
        weather_timer = 0
    
    weather_timer += 1
    
    # 检查是否需要切换天气
    if weather_timer > random.randint(*WEATHER_TYPES[weather]["duration"]):
        # 随机选择新天气
        new_weather = random.choice(["clear", "rain", "thunder"])
        weather = new_weather
        weather_timer = 0
        
        # 播放天气音效
        if weather == "rain":
            play_sound("rain")
        elif weather == "thunder":
            play_sound("thunder")
    
    # 处理天气效果
    if weather == "rain":
        # 雨天气效果：加速作物生长
        if random.random() < 0.01:
            for pos in list(plants.keys()):
                crop = plants[pos]
                if crop["watered"]:
                    crop["growth"] += 1
                    new_stage = min(3, crop["growth"] // 3)
                    if new_stage != crop["stage"]:
                        crop["stage"] = new_stage
    elif weather == "thunder":
        # 雷暴天气效果：加速作物生长和随机闪电
        if random.random() < 0.02:
            for pos in list(plants.keys()):
                crop = plants[pos]
                if crop["watered"]:
                    crop["growth"] += 1
                    new_stage = min(3, crop["growth"] // 3)
                    if new_stage != crop["stage"]:
                        crop["stage"] = new_stage
        
        # 随机闪电
        if random.random() < 0.001:
            play_sound("lightning")
            # 闪电效果可以在这里添加

def get_sky_color():
    """根据时间和天气获取天空颜色"""
    global time_of_day, weather
    
    # 根据时间计算时段
    if 0 <= time_of_day < 6000:
        period = 0  # 早晨
    elif 6000 <= time_of_day < 12000:
        period = 1  # 中午
    elif 12000 <= time_of_day < 18000:
        period = 2  # 傍晚
    else:
        period = 0  # 夜晚（使用早晨的颜色，但更暗）
    
    # 根据天气获取基础颜色
    if weather in WEATHER_TYPES:
        base_color = WEATHER_TYPES[weather]["sky_color"][period]
    else:
        base_color = (135, 206, 235)  # 默认天空蓝
    
    # 夜晚调暗颜色
    if 18000 <= time_of_day < 24000:
        r = max(0, base_color[0] // 3)
        g = max(0, base_color[1] // 3)
        b = max(0, base_color[2] // 3)
        return (r, g, b)
    
    return base_color

# 绘制方块
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

# 移除方块
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

# 农作物系统函数
def plant_crop(x, y, z, crop_type):
    """种植农作物"""
    # 检查是否在耕地上
    block_below = blocks.get(z-1, {}).get((x, y), None)
    if block_below != "farmland":
        return False
    
    # 检查是否已有植物
    if (x, y, z) in plants:
        return False
    
    # 种植新作物
    plants[(x, y, z)] = {
        "type": crop_type,
        "growth": 0,
        "watered": is_near_water(x, y, z),
        "stage": 0
    }
    
    # 播放种植音效
    play_sound("plant")
    return True

def is_near_water(x, y, z):
    """检查作物是否靠近水源"""
    # 检查周围3x3范围内是否有水
    for dx in [-BLOCK_SIZE, 0, BLOCK_SIZE]:
        for dy in [-BLOCK_SIZE, 0, BLOCK_SIZE]:
            for dz in [-1, 0, 1]:
                check_x = x + dx
                check_y = y + dy
                check_z = z + dz
                if check_z in blocks and (check_x, check_y) in blocks[check_z]:
                    if blocks[check_z][(check_x, check_y)] == "water":
                        return True
    return False

def grow_crops():
    """让所有作物生长"""
    for pos in list(plants.keys()):
        crop = plants[pos]
        x, y, z = pos
        
        # 检查是否仍然在耕地上
        if blocks.get(z-1, {}).get((x, y), None) != "farmland":
            del plants[pos]
            continue
            
        # 更新浇水状态
        crop["watered"] = is_near_water(x, y, z)
        
        # 随机生长
        growth_chance = 0.1 if crop["watered"] else 0.02
        if random.random() < growth_chance:
            crop["growth"] += 1
            
            # 更新生长阶段 (0-3)
            new_stage = min(3, crop["growth"] // 3)
            if new_stage != crop["stage"]:
                crop["stage"] = new_stage
                
                # 如果完全成熟，停止生长
                if new_stage == 3:
                    crop["growth"] = 10  # 最大值

def draw_crop(x, y, z, crop):
    """绘制农作物"""
    crop_type = crop["type"]
    stage = crop["stage"]
    
    # 设置作物颜色和大小
    pen.goto(x, y)
    color_key = f"{crop_type}_stage_{stage}"
    if color_key not in COLORS:
        color_key = f"wheat_stage_{stage}"  # 默认使用小麦的颜色
    
    pen.color(COLORS[color_key][0])
    pen.pendown()
    pen.begin_fill()
    
    # 作物大小随生长阶段增加
    size = BLOCK_SIZE * (0.3 + stage * 0.15)
    half_size = size / 2
    
    # 绘制作物形状
    pen.penup()
    pen.goto(x + BLOCK_SIZE/2 - half_size, y + BLOCK_SIZE/2 - half_size)
    pen.pendown()
    for _ in range(4):
        pen.forward(size)
        pen.left(90)
    
    pen.end_fill()
    pen.penup()

def harvest_crop(x, y, z):
    """收获作物"""
    if (x, y, z) in plants:
        crop = plants[(x, y, z)]
        if crop["stage"] == 3:  # 只有成熟作物可以收获
            crop_type = crop["type"]
            del plants[(x, y, z)]
            
            # 掉落作物和种子
            spawn_item(x, y, crop_type, random.randint(1, 3))
            spawn_item(x, y, f"{crop_type}_seeds", random.randint(0, 2))
            
            # 播放收获音效
            play_sound("harvest")
            return True
    return False

# 主页面函数
def draw_main_menu():
    """绘制主页面"""
    # 清空屏幕
    screen.clear()
    screen.bgcolor(50, 100, 180)  # 天空蓝色
    
    # 绘制标题
    pen.goto(0, 150)
    pen.color(255, 215, 0)
    pen.write("Minecraft Ultimate", align="center", font=("Arial", 36, "bold"))
    
    # 绘制按钮
    for btn_id, btn in menu_buttons.items():
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
        pen.penup()
        
        pen.goto(btn["x"] + btn["width"]/2, btn["y"] + btn["height"]/2 - 10)
        pen.color(255, 255, 255)
        pen.write(btn["text"], align="center", font=("Arial", 16, "normal"))
    
    screen.update()

def start_game():
    """开始游戏"""
    global is_playing, in_main_menu, last_ambient_time
    in_main_menu = False
    is_playing = True
    last_ambient_time = pygame.time.get_ticks()
    
    # 初始化世界
    init_world()
    
    # 启动环境音效线程
    threading.Thread(target=ambient_sound_updater, daemon=True).start()
    
    # 开始游戏循环
    game_loop()

def init_world():
    """初始化世界"""
    global player_x, player_y, inventory, hotbar, blocks, plants, entities, time_of_day, weather, current_dimension
    
    # 清除现有世界
    blocks = {}
    plants = {}
    entities = []
    
    # 重置玩家位置
    player_x, player_y = 0, 0
    player_pen.goto(player_x, player_y)
    
    # 初始化物品栏
    inventory = {
        "dirt": 10,
        "wood": 5,
        "wheat_seeds": 8,
        "stone": 3,
        "crafting_table": 1,
        "furnace": 1,
        "torch": 5
    }
    hotbar = ["dirt", "wood", "wheat_seeds", "crafting_table", "furnace", "torch", None, None, None]
    
    # 根据当前维度生成地形
    if current_dimension == "主世界":
        generate_overworld()
    elif current_dimension == "下界":
        generate_nether()
    elif current_dimension == "末地":
        generate_end()

def generate_overworld():
    """生成主世界地形"""
    # 创建地形
    for x in range(-400, 400, BLOCK_SIZE):
        for y in range(-300, -200, BLOCK_SIZE):
            # 随机生成草地、泥土和石头
            if random.random() < 0.7:
                draw_block(x, y, 0, "grass")
            elif random.random() < 0.85:
                draw_block(x, y, 0, "dirt")
            else:
                draw_block(x, y, 0, "stone")
    
    # 添加矿石
    for x in range(-400, 400, BLOCK_SIZE):
        for y in range(-350, -300, BLOCK_SIZE):
            if random.random() < 0.05:
                draw_block(x, y, 0, "coal_ore")
            elif random.random() < 0.03:
                draw_block(x, y, 0, "iron_ore")
            elif random.random() < 0.01:
                draw_block(x, y, 0, "gold_ore")
            elif random.random() < 0.005:
                draw_block(x, y, 0, "diamond_ore")
            else:
                draw_block(x, y, 0, "stone")
    
    # 创建一些耕地
    for x in range(-100, 100, BLOCK_SIZE):
        for y in range(-250, -200, BLOCK_SIZE):
            draw_block(x, y, 0, "farmland")
    
    # 添加水源
    draw_block(120, -230, 0, "water")
    draw_block(120, -210, 0, "water")
    draw_block(140, -230, 0, "water")
    
    # 添加装饰植物
    for x in range(-350, 350, BLOCK_SIZE * 5):
        for y in range(-250, -200, BLOCK_SIZE * 5):
            if random.random() < 0.3:
                draw_block(x, y, 0, "flower")
            elif random.random() < 0.4:
                draw_block(x, y, 0, "tall_grass")
            elif random.random() < 0.1:
                draw_block(x, y, 0, "mushroom")
    
    # 生成生物
    for _ in range(5):
        x = random.randint(-300, 300)
        y = random.randint(-250, -200)
        entity_type = random.choice(["cow", "pig", "sheep"])
        create_entity(entity_type, x, y)

def generate_nether():
    """生成下界地形"""
    # 创建下界岩地形
    for x in range(-400, 400, BLOCK_SIZE):
        for y in range(-350, -200, BLOCK_SIZE):
            if random.random() < 0.8:
                draw_block(x, y, 0, "netherrack")
            else:
                draw_block(x, y, 0, "soul_sand")
    
    # 添加下界堡垒
    for x in range(-100, 100, BLOCK_SIZE):
        for y in range(-250, -150, BLOCK_SIZE):
            if random.random() < 0.3:
                draw_block(x, y, 0, "netherrack")
    
    # 生成下界生物
    for _ in range(8):
        x = random.randint(-300, 300)
        y = random.randint(-250, -200)
        create_entity("zombie", x, y)

def generate_end():
    """生成末地地形"""
    # 创建末地石地形
    for x in range(-400, 400, BLOCK_SIZE):
        for y in range(-350, -250, BLOCK_SIZE):
            draw_block(x, y, 0, "end_stone")
    
    # 创建末地城
    for x in range(-150, 150, BLOCK_SIZE):
        for y in range(-250, -150, BLOCK_SIZE):
            if (x % (BLOCK_SIZE * 4) == 0 or y % (BLOCK_SIZE * 4) == 0) and random.random() < 0.7:
                draw_block(x, y, 0, "end_stone")
    
    # 生成末地生物
    for _ in range(3):
        x = random.randint(-300, 300)
        y = random.randint(-250, -200)
        create_entity("skeleton", x, y)

def switch_dimension(dimension):
    """切换维度"""
    global current_dimension, is_playing
    
    # 暂停游戏
    is_playing = False
    
    # 显示维度切换消息
    messagebox.showinfo("维度切换", f"正在进入{dimension}...")
    
    # 切换维度
    current_dimension = dimension
    
    # 重新初始化世界
    init_world()
    
    # 恢复游戏
    is_playing = True
    
    # 开始游戏循环
    game_loop()

def check_crafting(recipe_pattern, inventory):
    """检查是否可以合成物品"""
    # 创建一个临时 inventory 副本
    temp_inventory = inventory.copy()
    
    # 检查每一行
    for row in recipe_pattern:
        # 检查每一列
        for item in row:
            if item is not None:
                if item not in temp_inventory or temp_inventory[item] <= 0:
                    return False
                temp_inventory[item] -= 1
    
    return True

def craft_item(recipe_pattern, inventory):
    """合成物品"""
    # 检查是否可以合成
    if not check_crafting(recipe_pattern, inventory):
        return None
    
    # 消耗材料
    for row in recipe_pattern:
        for item in row:
            if item is not None:
                inventory[item] -= 1
                if inventory[item] <= 0:
                    del inventory[item]
    
    return True

def find_matching_recipe(crafting_grid):
    """查找匹配的合成配方"""
    # 简化合成网格，移除空槽位
    simplified_grid = []
    for row in crafting_grid:
        simplified_row = [item for item in row if item is not None]
        if simplified_row:
            simplified_grid.append(simplified_row)
    
    # 如果没有材料，返回 None
    if not simplified_grid:
        return None
    
    # 查找匹配的配方
    for recipe_name, recipe_data in RECIPES.items():
        recipe_pattern = recipe_data["pattern"]
        
        # 简化配方模式
        simplified_recipe = []
        for row in recipe_pattern:
            simplified_recipe_row = [item for item in row if item is not None]
            if simplified_recipe_row:
                simplified_recipe.append(simplified_recipe_row)
        
        # 检查是否匹配
        if simplified_recipe == simplified_grid:
            return recipe_data["result"]
    
    return None

def draw_crafting_grid(x, y, grid):
    """绘制合成网格"""
    # 绘制网格背景
    pen.goto(x, y)
    pen.color(100, 100, 100)
    pen.pendown()
    pen.begin_fill()
    pen.forward(120)
    pen.left(90)
    pen.forward(120)
    pen.left(90)
    pen.forward(120)
    pen.left(90)
    pen.forward(120)
    pen.end_fill()
    pen.penup()
    
    # 绘制网格线
    for i in range(4):
        # 垂直线
        pen.goto(x + i * 40, y)
        pen.color(50, 50, 50)
        pen.pendown()
        pen.forward(120)
        pen.penup()
        
        # 水平线
        pen.goto(x, y + i * 40)
        pen.color(50, 50, 50)
        pen.pendown()
        pen.left(90)
        pen.forward(120)
        pen.right(90)
        pen.penup()
    
    # 绘制物品
    for i in range(3):
        for j in range(3):
            item = grid[i][j]
            if item:
                item_x = x + j * 40 + 20
                item_y = y + i * 40 + 20
                
                # 绘制物品背景
                pen.goto(item_x - 15, item_y - 15)
                pen.color(150, 150, 150)
                pen.pendown()
                pen.begin_fill()
                pen.forward(30)
                pen.left(90)
                pen.forward(30)
                pen.left(90)
                pen.forward(30)
                pen.left(90)
                pen.forward(30)
                pen.end_fill()
                pen.penup()
                
                # 绘制物品图标（简化为文字）
                pen.goto(item_x, item_y - 5)
                pen.color(255, 255, 255)
                pen.write(item[:2], align="center", font=("Arial", 10, "bold"))

def open_crafting_table():
    """打开工作台界面"""
    global is_playing, crafting_grid, selected_crafting_slot
    
    # 暂停游戏
    is_playing = False
    
    # 初始化合成网格
    crafting_grid = [[None for _ in range(3)] for _ in range(3)]
    selected_crafting_slot = None
    result_item = None
    
    # 创建临时画笔
    temp_pen = turtle.Turtle()
    temp_pen.speed(0)
    temp_pen.hideturtle()
    temp_pen.penup()
    
    # 绘制界面背景
    temp_pen.goto(-200, -200)
    temp_pen.color(50, 50, 50)
    temp_pen.pendown()
    temp_pen.begin_fill()
    temp_pen.forward(400)
    temp_pen.left(90)
    temp_pen.forward(400)
    temp_pen.left(90)
    temp_pen.forward(400)
    temp_pen.left(90)
    temp_pen.forward(400)
    temp_pen.end_fill()
    temp_pen.penup()
    
    # 绘制标题
    temp_pen.goto(0, 150)
    temp_pen.color(255, 255, 255)
    temp_pen.write("工作台", align="center", font=("Arial", 24, "bold"))
    
    # 绘制关闭按钮
    temp_pen.goto(150, 150)
    temp_pen.color(200, 0, 0)
    temp_pen.pendown()
    temp_pen.begin_fill()
    temp_pen.forward(30)
    temp_pen.left(90)
    temp_pen.forward(30)
    temp_pen.left(90)
    temp_pen.forward(30)
    temp_pen.left(90)
    temp_pen.forward(30)
    temp_pen.end_fill()
    temp_pen.penup()
    temp_pen.goto(165, 165)
    temp_pen.color(255, 255, 255)
    temp_pen.write("X", align="center", font=("Arial", 16, "bold"))
    
    # 绘制合成网格
    draw_crafting_grid(-100, 0, crafting_grid)
    
    # 绘制箭头
    temp_pen.goto(50, 60)
    temp_pen.color(255, 255, 255)
    temp_pen.write("→", align="center", font=("Arial", 24, "bold"))
    
    # 绘制结果槽位
    temp_pen.goto(100, 60)
    temp_pen.color(100, 100, 100)
    temp_pen.pendown()
    temp_pen.begin_fill()
    temp_pen.forward(40)
    temp_pen.left(90)
    temp_pen.forward(40)
    temp_pen.left(90)
    temp_pen.forward(40)
    temp_pen.left(90)
    temp_pen.forward(40)
    temp_pen.end_fill()
    temp_pen.penup()
    
    # 绘制物品栏
    temp_pen.goto(-150, -150)
    temp_pen.color(100, 100, 100)
    temp_pen.pendown()
    temp_pen.begin_fill()
    temp_pen.forward(300)
    temp_pen.left(90)
    temp_pen.forward(50)
    temp_pen.left(90)
    temp_pen.forward(300)
    temp_pen.left(90)
    temp_pen.forward(50)
    temp_pen.end_fill()
    temp_pen.penup()
    
    # 绘制物品栏物品
    slot_x = -140
    slot_y = -140
    for item, count in inventory.items():
        if count > 0:
            # 绘制物品槽位
            temp_pen.goto(slot_x, slot_y)
            temp_pen.color(150, 150, 150)
            temp_pen.pendown()
            temp_pen.begin_fill()
            temp_pen.forward(30)
            temp_pen.left(90)
            temp_pen.forward(30)
            temp_pen.left(90)
            temp_pen.forward(30)
            temp_pen.left(90)
            temp_pen.forward(30)
            temp_pen.end_fill()
            temp_pen.penup()
            
            # 绘制物品图标
            temp_pen.goto(slot_x + 15, slot_y + 10)
            temp_pen.color(255, 255, 255)
            temp_pen.write(item[:2], align="center", font=("Arial", 10, "bold"))
            
            # 绘制物品数量
            temp_pen.goto(slot_x + 25, slot_y + 5)
            temp_pen.color(255, 255, 255)
            temp_pen.write(str(count), align="right", font=("Arial", 8, "normal"))
            
            slot_x += 40
            if slot_x > 140:
                slot_x = -140
                slot_y += 40
    
    # 更新屏幕
    screen.update()
    
    # 等待用户交互
    def on_crafting_click(x, y):
        nonlocal result_item
        
        # 检查是否点击了关闭按钮
        if 150 <= x <= 180 and 150 <= y <= 180:
            # 清除界面
            temp_pen.clear()
            # 恢复游戏
            is_playing = True
            game_loop()
            return
        
        # 检查是否点击了合成网格
        if -100 <= x <= 20 and 0 <= y <= 120:
            grid_x = int((x + 100) // 40)
            grid_y = int((y) // 40)
            
            if 0 <= grid_x < 3 and 0 <= grid_y < 3:
                if selected_crafting_slot is not None:
                    # 将选中的物品放入合成网格
                    crafting_grid[grid_y][grid_x] = selected_crafting_slot
                    # 消耗物品
                    inventory[selected_crafting_slot] -= 1
                    if inventory[selected_crafting_slot] <= 0:
                        del inventory[selected_crafting_slot]
                    selected_crafting_slot = None
                else:
                    # 从合成网格中取出物品
                    item = crafting_grid[grid_y][grid_x]
                    if item:
                        # 添加到物品栏
                        if item in inventory:
                            inventory[item] += 1
                        else:
                            inventory[item] = 1
                        # 从合成网格中移除
                        crafting_grid[grid_y][grid_x] = None
            
            # 更新界面
            temp_pen.clear()
            draw_crafting_table_ui(temp_pen, crafting_grid, result_item)
            
            # 查找匹配的配方
            result_item = find_matching_recipe(crafting_grid)
            
            # 绘制结果
            if result_item:
                draw_result_slot(temp_pen, result_item)
        
        # 检查是否点击了物品栏
        elif -150 <= x <= 150 and -150 <= y <= -100:
            slot_x = int((x + 150) // 40)
            slot_y = int((y + 150) // 40)
            
            # 获取物品栏中的物品
            items = list(inventory.keys())
            index = slot_y * 8 + slot_x
            
            if 0 <= index < len(items):
                selected_crafting_slot = items[index]
            
            # 更新界面
            temp_pen.clear()
            draw_crafting_table_ui(temp_pen, crafting_grid, result_item)
            
            # 高亮显示选中的物品
            if selected_crafting_slot:
                temp_pen.goto(-140 + slot_x * 40, -140 + slot_y * 40)
                temp_pen.color(255, 255, 0)
                temp_pen.pendown()
                temp_pen.pensize(2)
                temp_pen.forward(30)
                temp_pen.left(90)
                temp_pen.forward(30)
                temp_pen.left(90)
                temp_pen.forward(30)
                temp_pen.left(90)
                temp_pen.forward(30)
                temp_pen.pensize(1)
                temp_pen.penup()
        
        # 检查是否点击了结果槽位
        elif 100 <= x <= 140 and 60 <= y <= 100 and result_item:
            # 添加到物品栏
            item = result_item["item"]
            count = result_item["count"]
            
            if item in inventory:
                inventory[item] += count
            else:
                inventory[item] = count
            
            # 消耗材料
            craft_item(crafting_grid, inventory)
            
            # 清空合成网格
            for i in range(3):
                for j in range(3):
                    crafting_grid[i][j] = None
            
            # 更新界面
            temp_pen.clear()
            draw_crafting_table_ui(temp_pen, crafting_grid, None)
    
    # 绘制工作台UI的辅助函数
    def draw_crafting_table_ui(pen, grid, result):
        # 绘制界面背景
        pen.goto(-200, -200)
        pen.color(50, 50, 50)
        pen.pendown()
        pen.begin_fill()
        pen.forward(400)
        pen.left(90)
        pen.forward(400)
        pen.left(90)
        pen.forward(400)
        pen.left(90)
        pen.forward(400)
        pen.end_fill()
        pen.penup()
        
        # 绘制标题
        pen.goto(0, 150)
        pen.color(255, 255, 255)
        pen.write("工作台", align="center", font=("Arial", 24, "bold"))
        
        # 绘制关闭按钮
        pen.goto(150, 150)
        pen.color(200, 0, 0)
        pen.pendown()
        pen.begin_fill()
        pen.forward(30)
        pen.left(90)
        pen.forward(30)
        pen.left(90)
        pen.forward(30)
        pen.left(90)
        pen.forward(30)
        pen.end_fill()
        pen.penup()
        pen.goto(165, 165)
        pen.color(255, 255, 255)
        pen.write("X", align="center", font=("Arial", 16, "bold"))
        
        # 绘制合成网格
        draw_crafting_grid(-100, 0, grid)
        
        # 绘制箭头
        pen.goto(50, 60)
        pen.color(255, 255, 255)
        pen.write("→", align="center", font=("Arial", 24, "bold"))
        
        # 绘制结果槽位
        pen.goto(100, 60)
        pen.color(100, 100, 100)
        pen.pendown()
        pen.begin_fill()
        pen.forward(40)
        pen.left(90)
        pen.forward(40)
        pen.left(90)
        pen.forward(40)
        pen.left(90)
        pen.forward(40)
        pen.end_fill()
        pen.penup()
        
        # 如果有结果，绘制结果
        if result:
            draw_result_slot(pen, result)
        
        # 绘制物品栏
        pen.goto(-150, -150)
        pen.color(100, 100, 100)
        pen.pendown()
        pen.begin_fill()
        pen.forward(300)
        pen.left(90)
        pen.forward(50)
        pen.left(90)
        pen.forward(300)
        pen.left(90)
        pen.forward(50)
        pen.end_fill()
        pen.penup()
        
        # 绘制物品栏物品
        slot_x = -140
        slot_y = -140
        for item, count in inventory.items():
            if count > 0:
                # 绘制物品槽位
                pen.goto(slot_x, slot_y)
                pen.color(150, 150, 150)
                pen.pendown()
                pen.begin_fill()
                pen.forward(30)
                pen.left(90)
                pen.forward(30)
                pen.left(90)
                pen.forward(30)
                pen.left(90)
                pen.forward(30)
                pen.end_fill()
                pen.penup()
                
                # 绘制物品图标
                pen.goto(slot_x + 15, slot_y + 10)
                pen.color(255, 255, 255)
                pen.write(item[:2], align="center", font=("Arial", 10, "bold"))
                
                # 绘制物品数量
                pen.goto(slot_x + 25, slot_y + 5)
                pen.color(255, 255, 255)
                pen.write(str(count), align="right", font=("Arial", 8, "normal"))
                
                slot_x += 40
                if slot_x > 140:
                    slot_x = -140
                    slot_y += 40
    
    # 绘制结果槽位的辅助函数
    def draw_result_slot(pen, result):
        item = result["item"]
        count = result["count"]
        
        # 绘制物品背景
        pen.goto(105, 65)
        pen.color(150, 150, 150)
        pen.pendown()
        pen.begin_fill()
        pen.forward(30)
        pen.left(90)
        pen.forward(30)
        pen.left(90)
        pen.forward(30)
        pen.left(90)
        pen.forward(30)
        pen.end_fill()
        pen.penup()
        
        # 绘制物品图标
        pen.goto(120, 75)
        pen.color(255, 255, 255)
        pen.write(item[:2], align="center", font=("Arial", 10, "bold"))
        
        # 绘制物品数量
        pen.goto(130, 70)
        pen.color(255, 255, 255)
        pen.write(str(count), align="right", font=("Arial", 8, "normal"))
    
    # 设置点击事件
    screen.onclick(on_crafting_click)
    screen.listen()

def open_furnace():
    """打开熔炉界面"""
    global is_playing
    
    # 暂停游戏
    is_playing = False
    
    # 创建临时画笔
    temp_pen = turtle.Turtle()
    temp_pen.speed(0)
    temp_pen.hideturtle()
    temp_pen.penup()
    
    # 绘制界面背景
    temp_pen.goto(-200, -200)
    temp_pen.color(50, 50, 50)
    temp_pen.pendown()
    temp_pen.begin_fill()
    temp_pen.forward(400)
    temp_pen.left(90)
    temp_pen.forward(400)
    temp_pen.left(90)
    temp_pen.forward(400)
    temp_pen.left(90)
    temp_pen.forward(400)
    temp_pen.end_fill()
    temp_pen.penup()
    
    # 绘制标题
    temp_pen.goto(0, 150)
    temp_pen.color(255, 255, 255)
    temp_pen.write("熔炉", align="center", font=("Arial", 24, "bold"))
    
    # 绘制关闭按钮
    temp_pen.goto(150, 150)
    temp_pen.color(200, 0, 0)
    temp_pen.pendown()
    temp_pen.begin_fill()
    temp_pen.forward(30)
    temp_pen.left(90)
    temp_pen.forward(30)
    temp_pen.left(90)
    temp_pen.forward(30)
    temp_pen.left(90)
    temp_pen.forward(30)
    temp_pen.end_fill()
    temp_pen.penup()
    temp_pen.goto(165, 165)
    temp_pen.color(255, 255, 255)
    temp_pen.write("X", align="center", font=("Arial", 16, "bold"))
    
    # 绘制熔炉界面
    # 燃料槽
    temp_pen.goto(-100, 50)
    temp_pen.color(100, 100, 100)
    temp_pen.pendown()
    temp_pen.begin_fill()
    temp_pen.forward(40)
    temp_pen.left(90)
    temp_pen.forward(40)
    temp_pen.left(90)
    temp_pen.forward(40)
    temp_pen.left(90)
    temp_pen.forward(40)
    temp_pen.end_fill()
    temp_pen.penup()
    temp_pen.goto(-80, 30)
    temp_pen.color(255, 255, 255)
    temp_pen.write("燃料", align="center", font=("Arial", 10, "normal"))
    
    # 箭头
    temp_pen.goto(-30, 70)
    temp_pen.color(255, 255, 255)
    temp_pen.write("→", align="center", font=("Arial", 24, "bold"))
    
    # 输入槽
    temp_pen.goto(0, 50)
    temp_pen.color(100, 100, 100)
    temp_pen.pendown()
    temp_pen.begin_fill()
    temp_pen.forward(40)
    temp_pen.left(90)
    temp_pen.forward(40)
    temp_pen.left(90)
    temp_pen.forward(40)
    temp_pen.left(90)
    temp_pen.forward(40)
    temp_pen.end_fill()
    temp_pen.penup()
    temp_pen.goto(20, 30)
    temp_pen.color(255, 255, 255)
    temp_pen.write("输入", align="center", font=("Arial", 10, "normal"))
    
    # 箭头
    temp_pen.goto(70, 70)
    temp_pen.color(255, 255, 255)
    temp_pen.write("→", align="center", font=("Arial", 24, "bold"))
    
    # 输出槽
    temp_pen.goto(100, 50)
    temp_pen.color(100, 100, 100)
    temp_pen.pendown()
    temp_pen.begin_fill()
    temp_pen.forward(40)
    temp_pen.left(90)
    temp_pen.forward(40)
    temp_pen.left(90)
    temp_pen.forward(40)
    temp_pen.left(90)
    temp_pen.forward(40)
    temp_pen.end_fill()
    temp_pen.penup()
    temp_pen.goto(120, 30)
    temp_pen.color(255, 255, 255)
    temp_pen.write("输出", align="center", font=("Arial", 10, "normal"))
    
    # 绘制物品栏
    temp_pen.goto(-150, -150)
    temp_pen.color(100, 100, 100)
    temp_pen.pendown()
    temp_pen.begin_fill()
    temp_pen.forward(300)
    temp_pen.left(90)
    temp_pen.forward(50)
    temp_pen.left(90)
    temp_pen.forward(300)
    temp_pen.left(90)
    temp_pen.forward(50)
    temp_pen.end_fill()
    temp_pen.penup()
    
    # 绘制物品栏物品
    slot_x = -140
    slot_y = -140
    for item, count in inventory.items():
        if count > 0:
            # 绘制物品槽位
            temp_pen.goto(slot_x, slot_y)
            temp_pen.color(150, 150, 150)
            temp_pen.pendown()
            temp_pen.begin_fill()
            temp_pen.forward(30)
            temp_pen.left(90)
            temp_pen.forward(30)
            temp_pen.left(90)
            temp_pen.forward(30)
            temp_pen.left(90)
            temp_pen.forward(30)
            temp_pen.end_fill()
            temp_pen.penup()
            
            # 绘制物品图标
            temp_pen.goto(slot_x + 15, slot_y + 10)
            temp_pen.color(255, 255, 255)
            temp_pen.write(item[:2], align="center", font=("Arial", 10, "bold"))
            
            # 绘制物品数量
            temp_pen.goto(slot_x + 25, slot_y + 5)
            temp_pen.color(255, 255, 255)
            temp_pen.write(str(count), align="right", font=("Arial", 8, "normal"))
            
            slot_x += 40
            if slot_x > 140:
                slot_x = -140
                slot_y += 40
    
    # 更新屏幕
    screen.update()
    
    # 等待用户交互
    def on_furnace_click(x, y):
        # 检查是否点击了关闭按钮
        if 150 <= x <= 180 and 150 <= y <= 180:
            # 清除界面
            temp_pen.clear()
            # 恢复游戏
            is_playing = True
            game_loop()
            return
    
    # 设置点击事件
    screen.onclick(on_furnace_click)
    screen.listen()

def draw_selection_box():
    """绘制选中的方块框"""
    # 获取玩家看向的方向
    look_dir = player_pen.heading()
    rad = math.radians(look_dir)
    
    # 计算视线终点
    max_distance = BLOCK_SIZE * 5
    end_x = player_x + math.cos(rad) * max_distance
    end_y = player_y + math.sin(rad) * max_distance
    
    # 找到视线内的方块
    hit_x = round(end_x / BLOCK_SIZE) * BLOCK_SIZE
    hit_y = round(end_y / BLOCK_SIZE) * BLOCK_SIZE
    
    # 绘制选择框
    selection_box_pen.clear()
    selection_box_pen.penup()
    selection_box_pen.goto(hit_x, hit_y)
    selection_box_pen.pendown()
    selection_box_pen.pensize(2)
    
    for _ in range(4):
        selection_box_pen.forward(BLOCK_SIZE)
        selection_box_pen.left(90)
    
    selection_box_pen.penup()

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
    
    # 绘制快捷栏
    for i in range(9):
        x = -200 + i * 50
        y = -320
        
        pen.goto(x, y)
        pen.color(100, 100, 100)
        if i == selected_hotbar:
            pen.color(150, 150, 150)  # 选中的槽位高亮
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
            pen.goto(x + 20, y + 10)
            pen.write(f"({inventory.get(hotbar[i], 0)})", align="center", font=("Arial", 8, "normal"))

def spawn_item(x, y, item_type, count=1):
    """生成物品"""
    item_pen = turtle.Turtle()
    item_pen.speed(0)
    item_pen.shape("circle")
    item_pen.shapesize(0.5, 0.5)
    
    # 设置物品颜色
    item_colors = {
        "wheat_seeds": (200, 200, 0),
        "wheat": (255, 255, 0),
        "carrot_seeds": (255, 165, 0),
        "carrot": (255, 165, 0),
        "potato_seeds": (100, 200, 100),
        "potato": (100, 200, 100),
        "dirt": (139, 69, 19),
        "wood": (139, 69, 19),
    }
    color = item_colors.get(item_type, (255, 215, 0))
    item_pen.color(color)
    item_pen.penup()
    item_pen.goto(x, y)
    item_pen.showturtle()
    
    items_on_ground.append({
        "x": x, "y": y, "type": item_type, "count": count, "pen": item_pen
    })

# 事件处理函数
def on_click(x, y):
    """处理鼠标点击"""
    global in_main_menu, is_playing, player_x, player_y
    
    if in_main_menu:
        # 播放点击音效
        play_sound("click")
        
        # 检查是否点击了菜单按钮
        for btn_id, btn in menu_buttons.items():
            if (btn["x"] <= x <= btn["x"] + btn["width"] and 
                btn["y"] <= y <= btn["y"] + btn["height"]):
                
                if btn_id == "start":
                    start_game()
                elif btn_id == "options":
                    messagebox.showinfo("选项", "选项功能待实现")
                elif btn_id == "quit":
                    screen.bye()
        return
    
    if not is_playing:
        return
    
    # 计算点击的方块坐标
    block_x = round(x / BLOCK_SIZE) * BLOCK_SIZE
    block_y = round(y / BLOCK_SIZE) * BLOCK_SIZE
    block_z = 0  # 简化版，只考虑z=0层
    
    # 检查是否点击了生物
    clicked_entity = None
    for entity in entities:
        distance = math.hypot(entity["x"] - x, entity["y"] - y)
        if distance < BLOCK_SIZE / 2:
            clicked_entity = entity
            break
    
    if clicked_entity:
        # 左键点击 - 攻击生物
        if screen.getcanvas().winfo_pointer_button() == 1:
            # 计算玩家朝向
            player_dir = player_pen.heading()
            entity_dir = math.degrees(math.atan2(clicked_entity["y"] - player_y, clicked_entity["x"] - player_x))
            
            # 检查玩家是否面对生物
            if abs(player_dir - entity_dir) < 45 or abs(player_dir - entity_dir) > 315:
                # 攻击生物
                entity_take_damage(clicked_entity, 2)
                play_sound("hit")
        return
    
    # 左键点击 - 破坏方块或收获作物
    if screen.getcanvas().winfo_pointer_button() == 1:
        # 先尝试收获作物
        if harvest_crop(block_x, block_y, block_z + 1):
            return
            
        # 破坏方块
        if block_z in blocks and (block_x, block_y) in blocks[block_z]:
            block_type = blocks[block_z][(block_x, block_y)]
            drop_item = BLOCK_TYPES[block_type]["drop"]
            if drop_item:
                spawn_item(block_x, block_y, drop_item)
            remove_block(block_x, block_y, block_z)
            play_sound("break_block")
    
    # 右键点击 - 放置方块、种植作物或使用物品
    elif screen.getcanvas().winfo_pointer_button() == 3:
        # 检查是否点击了交互方块
        if block_z in blocks and (block_x, block_y) in blocks[block_z]:
            block_type = blocks[block_z][(block_x, block_y)]
            if BLOCK_TYPES[block_type].get("interactive"):
                if block_type == "crafting_table":
                    open_crafting_table()
                elif block_type == "furnace":
                    open_furnace()
                elif block_type == "composter":
                    messagebox.showinfo("堆肥桶", "堆肥桶功能待实现")
                return
        
        # 检查是否手持种子
        selected_item = hotbar[selected_hotbar]
        if selected_item and selected_item.endswith("_seeds"):
            crop_type = selected_item.replace("_seeds", "")
            if plant_crop(block_x, block_y, block_z + 1, crop_type):
                # 消耗种子
                inventory[selected_item] -= 1
                if inventory[selected_item] <= 0:
                    del inventory[selected_item]
                    hotbar[selected_hotbar] = None
            return
        
        # 放置方块
        if selected_item and selected_item in BLOCK_TYPES:
            if block_z not in blocks or (block_x, block_y) not in blocks[block_z]:
                draw_block(block_x, block_y, block_z, selected_item)
                # 消耗物品
                inventory[selected_item] -= 1
                if inventory[selected_item] <= 0:
                    del inventory[selected_item]
                    hotbar[selected_hotbar] = None
                play_sound("place_block")

def on_key_press(key):
    """处理键盘按键"""
    global player_x, player_y, selected_hotbar, is_playing, in_main_menu, current_dimension
    
    if in_main_menu:
        return
    
    if key == "Escape":
        is_playing = False
        in_main_menu = True
        draw_main_menu()
        return
    
    # 维度切换
    if key == "n":
        # 切换到下界
        switch_dimension("下界")
        return
    elif key == "e":
        # 切换到末地
        switch_dimension("末地")
        return
    elif key == "o":
        # 切换到主世界
        switch_dimension("主世界")
        return
    
    # 移动玩家
    move_amount = BLOCK_SIZE // 2
    moved = False
    if key == "w":
        player_pen.setheading(90)
        new_y = player_y + move_amount
        if not is_colliding(player_x, new_y, 0):
            player_y = new_y
            moved = True
    elif key == "s":
        player_pen.setheading(270)
        new_y = player_y - move_amount
        if not is_colliding(player_x, new_y, 0):
            player_y = new_y
            moved = True
    elif key == "a":
        player_pen.setheading(180)
        new_x = player_x - move_amount
        if not is_colliding(new_x, player_y, 0):
            player_x = new_x
            moved = True
    elif key == "d":
        player_pen.setheading(0)
        new_x = player_x + move_amount
        if not is_colliding(new_x, player_y, 0):
            player_x = new_x
            moved = True
    
    # 如果移动了，播放脚步声
    if moved:
        play_sound("walk")
    
    # 切换快捷栏
    if key in "123456789":
        selected_hotbar = int(key) - 1
        play_sound("click")
    
    # 更新玩家位置
    player_pen.goto(player_x, player_y)

def is_colliding(x, y, z):
    """检查碰撞"""
    block_x = round(x / BLOCK_SIZE) * BLOCK_SIZE
    block_y = round(y / BLOCK_SIZE) * BLOCK_SIZE
    return z in blocks and (block_x, block_y) in blocks[z]

def take_damage(amount):
    """玩家受伤"""
    global player_health
    player_health = max(0, player_health - amount)
    play_sound("hurt")
    if player_health <= 0:
        game_over()

def game_over():
    """游戏结束"""
    global is_playing
    is_playing = False
    messagebox.showinfo("游戏结束", "你已死亡！")
    in_main_menu = True
    draw_main_menu()

def ambient_sound_updater():
    """环境音效更新器"""
    while True:
        if is_playing:
            play_ambient_sound()
            # 检查天气音效
            if weather == "rain" and not pygame.mixer.get_busy():
                play_sound("rain")
        time.sleep(1)

def game_loop():
    """游戏主循环"""
    global time_of_day, player_hunger, current_dimension
    
    if not is_playing:
        return
    
    # 清空屏幕
    pen.clear()
    
    # 设置背景色
    screen.bgcolor(get_sky_color())
    
    # 绘制地面
    pen.goto(-500, -350)
    pen.color(dimensions[current_dimension]["ground_color"])
    pen.pendown()
    pen.begin_fill()
    pen.goto(500, -350)
    pen.goto(500, 350)
    pen.goto(-500, 350)
    pen.goto(-500, -350)
    pen.end_fill()
    pen.penup()
    
    # 绘制方块
    for z in blocks:
        for (x, y), block_type in blocks[z].items():
            # 只绘制渲染范围内的方块
            if (abs(x - player_x) < render_distance * BLOCK_SIZE and 
                abs(y - player_y) < render_distance * BLOCK_SIZE):
                draw_block(x, y, z, block_type)
    
    # 绘制农作物
    for (x, y, z), crop in plants.items():
        if (abs(x - player_x) < render_distance * BLOCK_SIZE and 
            abs(y - player_y) < render_distance * BLOCK_SIZE):
            draw_crop(x, y, z, crop)
    
    # 更新生物
    update_entities()
    
    # 绘制生物生命值
    for entity in entities:
        if (abs(entity["x"] - player_x) < render_distance * BLOCK_SIZE and 
            abs(entity["y"] - player_y) < render_distance * BLOCK_SIZE):
            draw_entity_health(entity)
    
    # 更新天气
    update_weather()
    
    # 作物生长
    time_of_day += 1
    if time_of_day >= 24000
        time_of_day = 0
    
    if time_of_day % 50 == 0:  # 每50 ticks生长一次
        grow_crops()
    
    # 玩家饥饿度减少
    if time_of_day % 200 == 0 and player_hunger > 0:
        player_hunger -= 1
        if player_hunger <= 0 and player_health > 0:
            take_damage(1)
    
    # 绘制选择框
    draw_selection_box()
    
    # 绘制控制栏
    draw_control_bar()
    
    # 绘制当前维度
    pen.goto(300, 300)
    pen.color(255, 255, 255)
    pen.write(f"维度: {current_dimension}", font=("Arial", 12, "normal"))
    
    # 绘制当前时间
    time_str = f"{time_of_day // 1000:02d}:{(time_of_day % 1000) // 10:02d}"
    pen.goto(300, 280)
    pen.color(255, 255, 255)
    pen.write(f"时间: {time_str}", font=("Arial", 12, "normal"))
    
    # 绘制当前天气
    pen.goto(300, 260)
    pen.color(255, 255, 255)
    pen.write(f"天气: {weather}", font=("Arial", 12, "normal"))
    
    # 更新屏幕
    screen.update()
    
    # 继续循环
    screen.ontimer(game_loop, 50)

# 设置事件监听
screen.onscreenclick(on_click)
screen.onkeypress(lambda: on_key_press("w"), "w")
screen.onkeypress(lambda: on_key_press("s"), "s")
screen.onkeypress(lambda: on_key_press("a"), "a")
screen.onkeypress(lambda: on_key_press("d"), "d")
screen.onkeypress(lambda: on_key_press("1"), "1")
screen.onkeypress(lambda: on_key_press("2"), "2")
screen.onkeypress(lambda: on_key_press("3"), "3")
screen.onkeypress(lambda: on_key_press("4"), "4")
screen.onkeypress(lambda: on_key_press("5"), "5")
screen.onkeypress(lambda: on_key_press("6"), "6")
screen.onkeypress(lambda: on_key_press("7"), "7")
screen.onkeypress(lambda: on_key_press("8"), "8")
screen.onkeypress(lambda: on_key_press("9"), "9")
screen.onkeypress(lambda: on_key_press("Escape"), "Escape")
screen.onkeypress(lambda: on_key_press("n"), "n")
screen.onkeypress(lambda: on_key_press("e"), "e")
screen.onkeypress(lambda: on_key_press("o"), "o")
screen.listen()

# 生成音效文件
generate_sounds()

# 启动游戏，显示主页面
print("游戏启动成功！")
draw_main_menu()

# 保持窗口打开
turtle.mainloop()
