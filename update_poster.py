import os
import requests
import sys
import base64
from urllib.parse import urljoin
import config
from PIL import Image, ImageFilter, ImageEnhance


def load_config():
    """加载配置信息"""
    return config.SERVER_CONFIG


def read_image_file(path):
    """读取图片文件并转换为base64编码"""
    try:
        with open(path, "rb") as img_file:
            image_data = img_file.read()
            image_data_base64 = base64.b64encode(image_data).decode("utf-8")
            return image_data_base64
    except Exception as e:
        raise IOError(f"错误: 读取图片文件时出错: {e}")


def upload_jellyfin_image(item_id, image_data):
    """上传图片到Jellyfin服务器"""
    try:
        auth_info = config.get_auth_info()
        # 构造 URL 和请求头
        url = f"{auth_info['base_url']}/Items/{item_id}/Images/{config.SERVER_CONFIG['IMAGE_TYPE']}"
        headers = {
            "Authorization": f'MediaBrowser Token="{auth_info["access_token"]}"',
            "Content-Type": "Image/jpeg",
        }
        response = requests.post(url, headers=headers, data=image_data, timeout=30)

        if response.status_code in (200, 204):
            print("成功: 图片上传到Jellyfin成功")
            return True
        else:
            print(f"错误: 图片上传到Jellyfin失败，状态码: {response.status_code}")
            try:
                print(f"错误详情: {response.json()}")
            except ValueError:
                print(f"错误详情: {response.text[:500]}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"错误: 上传到Jellyfin请求过程中出错: {e}")
        return False

def upload_emby_image(item_id, image_data):
    """上传图片到Emby服务器"""
    try:
        auth_info = config.get_auth_info()
        
        # Emby API可以使用API密钥或访问令牌
        if auth_info.get("is_api_key", False):
            url = f"{auth_info['base_url']}/Items/{item_id}/Images/{config.SERVER_CONFIG['IMAGE_TYPE']}?api_key={auth_info['access_token']}"
            headers = {
                "Content-Type": "Image/jpeg",
            }
        else:
            url = f"{auth_info['base_url']}/Items/{item_id}/Images/{config.SERVER_CONFIG['IMAGE_TYPE']}"
            headers = {
                "Authorization": f'MediaBrowser Token="{auth_info["access_token"]}"',
                "Content-Type": "Image/jpeg",
            }
        
        response = requests.post(url, headers=headers, data=image_data, timeout=30)

        if response.status_code in (200, 204):
            print("成功: 图片上传到Emby成功")
            return True
        else:
            print(f"错误: 图片上传到Emby失败，状态码: {response.status_code}")
            try:
                print(f"错误详情: {response.json()}")
            except ValueError:
                print(f"错误详情: {response.text[:500]}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"错误: 上传到Emby请求过程中出错: {e}")
        return False

def upload_image(item_id, image_data):
    """根据服务器类型上传图片"""
    server_type = config.SERVER_TYPE
    
    if server_type == "jellyfin":
        return upload_jellyfin_image(item_id, image_data)
    elif server_type == "emby":
        return upload_emby_image(item_id, image_data)
    else:
        print(f"不支持的服务器类型: {server_type}")
        return False


def add_shadow(img, offset=(5, 5), shadow_color=(0, 0, 0, 100), blur_radius=3):
    """
    给图片添加右侧和底部阴影

    参数:
        img: 原始图片（PIL.Image对象）
        offset: 阴影偏移量，(x, y)格式
        shadow_color: 阴影颜色，RGBA格式
        blur_radius: 阴影模糊半径

    返回:
        添加了阴影的新图片
    """
    # 创建一个透明背景，比原图大一些，以容纳阴影
    shadow_width = img.width + offset[0] + blur_radius * 2
    shadow_height = img.height + offset[1] + blur_radius * 2

    shadow = Image.new("RGBA", (shadow_width, shadow_height), (0, 0, 0, 0))

    # 创建阴影层
    shadow_layer = Image.new("RGBA", img.size, shadow_color)

    # 将阴影层粘贴到偏移位置
    shadow.paste(shadow_layer, (blur_radius + offset[0], blur_radius + offset[1]))

    # 模糊阴影
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))

    # 创建结果图像
    result = Image.new("RGBA", shadow.size, (0, 0, 0, 0))

    # 将原图粘贴到结果图像上
    result.paste(img, (blur_radius, blur_radius), img if img.mode == "RGBA" else None)

    # 合并阴影和原图（保持原图在上层）
    shadow_img = Image.alpha_composite(shadow, result)

    return shadow_img


def upload_poster_workflow(item_id, name):
    """
    封装上传海报到Jellyfin的完整工作流程

    返回:
        bool: 上传是否成功
    """
    try:
        print("\n[4/4] 正在更新Jellyfin海报...")
        print("-" * 40)

        file_path = os.path.join(config.OUTPUT_FOLDER, f"{name}.png")
        # 读取图片文件
        image_data_base64 = read_image_file(file_path)

        # 上传图片
        success = upload_image(item_id, image_data_base64)

        if success:
            print("\n海报上传成功！")
            return True
        else:
            print("\n海报上传失败！")
            return False

    except Exception as e:
        print(f"\n[错误] 上传海报时出错: {e}")
        return False
