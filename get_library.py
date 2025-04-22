import requests
import json

import config


def get_libraries():
    """
    获取Jellyfin的媒体库列表

    Returns:
        list: 包含媒体库信息的字典列表，每个字典包含'Id'和'Name'
    """
    # 确保已经完成认证
    config.get_auth_info()
    print("\n[1/4] 获取媒体库列表...")
    print("-" * 40)
    url = f"{config.JELLYFIN_CONFIG['BASE_URL']}/Library/MediaFolders"

    headers = {
        "Authorization": f'MediaBrowser Token="{config.JELLYFIN_CONFIG["ACCESS_TOKEN"]}"'
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
        print(f"获取媒体库列表失败: {str(e)}")
        return []
    except (json.JSONDecodeError, KeyError) as e:
        print(f"解析媒体库列表数据失败: {str(e)}")
        return []
