import os
import json

# 获取当前脚本所在目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 加载JSON配置文件
CONFIG_JSON_PATH = os.path.join(CURRENT_DIR, "config.json")
try:
    with open(CONFIG_JSON_PATH, "r", encoding="utf-8") as f:
        JSON_CONFIG = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"无法加载配置文件 config.json: {e}")
    JSON_CONFIG = {
        "jellyfin": {
            "base_url": "http://47.122.74.12:12118",
            "user_name": "your_username",
            "password": "your_password",
        },
        "template_mapping": [{"template_name": "Anime", "library_name": "Anime"}],
    }

# 文件路径配置
POSTER_FOLDER = os.path.join(CURRENT_DIR, "poster")  # 海报图片文件夹
TEMPLATE_FOLDER = os.path.join(CURRENT_DIR, "template")  # 模板图片
OUTPUT_FOLDER = os.path.join(CURRENT_DIR, "output")  # 输出文件夹

# 服务器类型配置（jellyfin 或 emby）
SERVER_TYPE = JSON_CONFIG.get("server_type", "jellyfin")

# 服务器配置
SERVER_CONFIG = {
    "BASE_URL": JSON_CONFIG[SERVER_TYPE]["base_url"],  # 从JSON配置获取服务地址
    "USER_NAME": JSON_CONFIG[SERVER_TYPE]["user_name"],  # 用户名
    "PASSWORD": JSON_CONFIG[SERVER_TYPE]["password"],  # 密码
    "AUTHORIZATION": 'MediaBrowser Client="other", Device="client", DeviceId="123", Version="0.0.0"',  # 认证头
    "ACCESS_TOKEN": "",  # API令牌
    "USER_ID": "",  # 用户ID
    "IMAGE_TYPE": "Primary",  # 图片类型
    "IMAGE_PATH": "poster.png",  # 图片文件名
    "UPDATE_POSTER": JSON_CONFIG[SERVER_TYPE].get(
        "update_poster", False
    ),  # 是否更新海报
    "API_KEY": JSON_CONFIG[SERVER_TYPE].get("api_key", "") if SERVER_TYPE == "emby" else "",  # Emby API密钥（仅Emby使用）
}

# 兼容旧代码，保留JELLYFIN_CONFIG变量名
JELLYFIN_CONFIG = SERVER_CONFIG

EXCLUDE_LIBRARY = JSON_CONFIG["exclude_Update_library"]  # 排除更新的媒体库列表

TEMPLATE_MAPPING = JSON_CONFIG["template_mapping"]

# 海报生成配置
POSTER_GEN_CONFIG = {
    "ROWS": 3,  # 每列图片数
    "COLS": 3,  # 总列数
    "MARGIN": 22,  # 图片垂直间距
    "CORNER_RADIUS": 46.1,  # 圆角半径
    "ROTATION_ANGLE": -15.8,  # 旋转角度
    "START_X": 835,  # 第一列的 x 坐标
    "START_Y": -362,  # 第一列的 y 坐标
    "COLUMN_SPACING": 100,  # 列间距
    "SAVE_COLUMNS": True,  # 是否保存每列图片
    "CELL_WIDTH": 410,  # 海报宽度
    "CELL_HEIGHT": 610,  # 海报高度
}

# 海报下载配置
POSTER_DOWNLOAD_CONFIG = {
    "POSTER_COUNT": 9,  # 要下载的海报数量
    "POSTER_DIR": POSTER_FOLDER,  # 海报保存目录
}


# 初始化认证信息
def init_auth():
    """初始化认证信息并更新JELLYFIN_CONFIG"""
    from auth import authenticate

    # 进行认证
    auth_info = authenticate(
        JELLYFIN_CONFIG["BASE_URL"],
        JELLYFIN_CONFIG["USER_NAME"],
        JELLYFIN_CONFIG["PASSWORD"],
    )

    if auth_info:
        # 更新JELLYFIN_CONFIG
        JELLYFIN_CONFIG["ACCESS_TOKEN"] = auth_info.get("access_token", "")
        JELLYFIN_CONFIG["USER_ID"] = auth_info.get("user_id", "")
        return True
    else:
        print("认证失败，无法获取认证信息")
        return False


# 获取认证信息
def get_auth_info():
    """获取认证信息，如果尚未认证则进行认证"""
    # 如果尚未进行认证，先初始化认证
    if not JELLYFIN_CONFIG["ACCESS_TOKEN"] or not JELLYFIN_CONFIG["USER_ID"]:
        init_auth()

    # 返回认证相关信息
    return {
        "user_id": JELLYFIN_CONFIG["USER_ID"],
        "access_token": JELLYFIN_CONFIG["ACCESS_TOKEN"],
        "base_url": JELLYFIN_CONFIG["BASE_URL"],
    }


# 刷新认证信息
def refresh_auth():
    """强制刷新认证信息"""
    return init_auth()


# 模块加载时尝试进行认证
try:
    init_auth()
except Exception as e:
    print(f"初始化认证时出错: {e}")
