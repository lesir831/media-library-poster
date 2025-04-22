import requests
import json
import os


def authenticate(base_url, username, password):
    """
    进行Jellyfin/Emby身份验证并返回User.Id和AccessToken

    Returns:
        dict: 包含User.Id和AccessToken的字典，验证失败则返回None
    """

    url = f"{base_url}/Users/AuthenticateByName"

    payload = json.dumps({"username": username, "Pw": password})

    headers = {
        "authorization": 'MediaBrowser Client="other", Device="client", DeviceId="123", Version="0.0.0"',
        "Content-Type": "application/json",
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()  # 检查HTTP错误

        data = response.json()
        auth_info = {
            "user_id": data.get("User", {}).get("Id"),
            "access_token": data.get("AccessToken"),
            "base_url": base_url,  # 同时返回base_url方便后续使用
        }

        # 验证是否成功获取了必要信息
        if auth_info["user_id"] and auth_info["access_token"]:
            return auth_info
        else:
            print("认证成功但未能获取User.Id或AccessToken")
            return None

    except requests.exceptions.RequestException as e:
        print(f"认证请求失败: {str(e)}")
        return None
    except json.JSONDecodeError:
        print("无法解析服务器响应")
        return None
