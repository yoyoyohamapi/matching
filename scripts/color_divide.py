# coding: utf8
"""
颜色冷暖、深浅区分
"""

print (__doc__)

import color as colorLib
import json

with open("../config/web_safe_color.json") as clothingColorConfig:
    colorMap = json.load(clothingColorConfig)

cwConfig = {}
colors = colorMap.keys()

# 红润皮肤适宜：
# 适宜：淡橙红、柠檬黄、苹果绿、紫红、天蓝
# 不适宜：
redWhiteSkinFits = [
    {
        "belongs": "orange",
        "isLight": 1
    },
    {
        "belongs": "yellow",
        "isLight": 1
    },
    {
        "belongs": "green",
        "isLight": 1
    },
    {
        "belongs": "blue",
        "isLight": 1
    },
    {
        "belongs": "purple",
        "isLight": 1
    }
]

redWhiteSkinUnfits = []

# 冷白皮肤适宜：
# 适宜：蓝、黄、浅橙黄、淡玫瑰色、浅绿色
# 不适宜：冷色调（非蓝，黄）
coldWhiteFits = [
    {
        "belongs": "orange",
        "isLight": 1
    },
    {
        "belongs": "yellow"
    },
    {
        "belongs": "green",
        "isLight": 1
    },
    {
        "belongs": "blue"
    },
    {
        "belongs": "purple",
        "isLight": 1
    }
]

coldWhiteUnfits = [
    {
        "isCold": 1
    }
]

# 小麦色皮肤:
# 适宜：深蓝、碳灰
# 不适宜：墨绿、枣红、咖啡色、金黄色
wheatFits = [
    {
        "belongs": "blue",
        "isLight": 1
    },
    {
        "belongs": "gray"
    }
]

wheatUnfits = [
    {
        "belongs": "green",
        "isCold": 0
    },
    {
        "belongs": "red",
        "isLight": 0
    },
    {
        "belongs": "brown"
    },
    {
        "belongs": "yellow",
        "isLight": 0
    }
]

# 偏黄色皮肤：
# 适宜：浅蓝色，酒红、淡紫
# 不适宜：褐色、蓝紫色、橘红
yellowFits = [
    {
        "belongs": "blue",
        "isLight": 1
    },
    {
        "belongs": "red",
        "isLight": 0
    },
    {
        "belongs": "purple",
        "isLight": 1
    }
]

yellowUnfits = [
    {
        "belongs": "brown"
    },
    {
        "belongs": "orange"
    },
    {
        "belongs": "purple",
        "isCold": 1
    }
]

# 偏黑色皮肤：
# 适宜：浅黄、浅粉、米白、黑色
# 不适宜：深蓝、深红等
blackFits = [
    {
        "belongs": "yellow",
        "isLight": 1
    },
    {
        "belongs": "pink",
        "isLight": 1
    },
    {
        "belongs": "white",
        "isLight": 0
    },
    {
        "belongs": "black"
    }
]

blackUnfits = [
    {
        "belongs": "blue",
        "isLight": 0
    },
    {
        "belongs": "red",
        "isLight": 0
    }
]

skinColorNames = [
    "red_white",
    "cold_white",
    "yellow",
    "wheat",
    "black"
]

fits = [
    redWhiteSkinFits,
    coldWhiteFits,
    yellowFits,
    wheatFits,
    blackFits
]

unfits = [
    redWhiteSkinUnfits,
    coldWhiteUnfits,
    yellowUnfits,
    wheatUnfits,
    blackUnfits
]

def colorCompare(color, condition):
    """
    获得字典子集

    Args:
        src 源字典
    """
    compColor = dict([ (k, color.get(k)) for k in condition.keys() ])
    return cmp(compColor, condition)

# 先标注颜色的冷暖、深浅、所属色系
for color in colors:
    r,g,b = colorLib.hex2Rgb(color)
    isCold = 0
    isLight = 1
    grayLevel = r*0.299 + g*0.587 + b*0.114
    if grayLevel > 192:
        isLight = 0
    if r < b:
        isLight = 1
    cwConfig[color] = {
        "isCold": isCold,
        "isLight": isLight,
        "belongs": colorMap[color],
        "fit": [],
        "unfit": []
    }
    # 该颜色适合的肤色
    for skin, fit in zip(skinColorNames, fits):
        for fitColor in fit:
            if colorCompare(cwConfig[color], fitColor) is 0:
                cwConfig[color]["fit"].append(skin)
                break

    # 该颜色不适合的肤色
    for skin, unfit in zip(skinColorNames, unfits):
        for unfitColor in unfit:
            if colorCompare(cwConfig[color], unfitColor) is 0 and \
                skin not in cwConfig[color]["fit"]:
                cwConfig[color]["unfit"].append(skin)
                break

with open("../config/web_safe_color_divide.json", "w") as f:
    f.write(json.dumps(cwConfig))
