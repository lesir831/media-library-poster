import requests
import json

import config


def get_jellyfin_libraries():
    """
    获取Jellyfin的媒体库列表

    Returns:
        list: 包含媒体库信息的字典列表，每个字典包含'Id'和'Name'
    """
    auth_info = config.get_auth_info()
    url = f"{auth_info['base_url']}/Library/MediaFolders"

    headers = {
        "Authorization": f'MediaBrowser Token="{auth_info["access_token"]}"'
    }

    try:
        response = requests.request("GET", url, headers=headers)
        response.raise_for_status()  # 检查HTTP错误

        data = response.json()
        libraries = []

        # 解析返回的JSON数据，提取每个媒体库的ID和名称
        if "Items" in data:
            for item in data["Items"]:
                if "Id" in item and "Name" in item:
                    libraries.append({"Id": item["Id"], "Name": item["Name"]})

        return libraries
    except requests.exceptions.RequestException as e:
        print(f"获取Jellyfin媒体库列表失败: {str(e)}")
        return []
    except (json.JSONDecodeError, KeyError) as e:
        print(f"解析Jellyfin媒体库列表数据失败: {str(e)}")
        return []


def get_emby_libraries():
    """
    获取Emby的媒体库列表

    Returns:
        list: 包含媒体库信息的字典列表，每个字典包含'Id'和'Name'
    """
    auth_info = config.get_auth_info()
    
    # Emby API可以使用API密钥或访问令牌
    if auth_info.get("is_api_key", False):
        url = f"{auth_info['base_url']}/Library/MediaFolders?api_key={auth_info['access_token']}"
        headers = {}
    else:
        url = f"{auth_info['base_url']}/Library/MediaFolders"
        headers = {
            "Authorization": f'MediaBrowser Token="{auth_info["access_token"]}"'
        }

    try:
        response = requests.request("GET", url, headers=headers)
        response.raise_for_status()  # 检查HTTP错误

        data = response.json()
        libraries = []

        # 解析返回的JSON数据，提取每个媒体库的ID和名称
        if "Items" in data:
            for item in data["Items"]:
                if "Id" in item and "Name" in item:
                    libraries.append({"Id": item["Id"], "Name": item["Name"]})

        return libraries
    except requests.exceptions.RequestException as e:
        print(f"获取Emby媒体库列表失败: {str(e)}")
        return []
    except (json.JSONDecodeError, KeyError) as e:
        print(f"解析Emby媒体库列表数据失败: {str(e)}")
        return []


def get_libraries():
    """
    根据服务器类型获取媒体库列表

    Returns:
        list: 包含媒体库信息的字典列表，每个字典包含'Id'和'Name'
    """
    # 确保已经完成认证
    config.get_auth_info()
    print("\n[1/4] 获取媒体库列表...")
    print("-" * 40)
    
    server_type = config.SERVER_TYPE
    
    if server_type == "jellyfin":
        print("使用Jellyfin API获取媒体库")
        return get_jellyfin_libraries()
    elif server_type == "emby":
        print("使用Emby API获取媒体库")
        return get_emby_libraries()
    else:
        print(f"不支持的服务器类型: {server_type}")
        return []
