import requests
import json
import os
import config


def authenticate_jellyfin(base_url, username, password):
    """
    进行Jellyfin身份验证并返回User.Id和AccessToken

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
            print("Jellyfin认证成功但未能获取User.Id或AccessToken")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Jellyfin认证请求失败: {str(e)}")
        return None
    except json.JSONDecodeError:
        print("无法解析Jellyfin服务器响应")
        return None


def authenticate_emby(base_url, username, password, api_key=None):
    """
    进行Emby身份验证并返回User.Id和AccessToken
    Emby支持API密钥或用户名/密码认证

    Returns:
        dict: 包含User.Id和AccessToken的字典，验证失败则返回None
    """
    # 如果有API Key，优先使用API Key认证
    if api_key:
        try:
            # 使用API Key获取用户列表
            url = f"{base_url}/Users?api_key={api_key}"
            response = requests.get(url)
            response.raise_for_status()
            
            users = response.json()
            if not users:
                print("使用API Key认证成功，但未找到用户")
                return None
                
            # 通常使用第一个管理员用户
            admin_users = [u for u in users if u.get("Policy", {}).get("IsAdministrator", False)]
            user = admin_users[0] if admin_users else users[0]
            
            return {
                "user_id": user.get("Id"),
                "access_token": api_key,  # 使用API Key作为访问令牌
                "base_url": base_url,
                "is_api_key": True  # 标记使用API Key认证
            }
        except Exception as e:
            print(f"使用API Key认证失败: {str(e)}")
            # 失败后尝试用户名密码认证
    
    # 用户名密码认证
    url = f"{base_url}/Users/AuthenticateByName"
    
    payload = json.dumps({"username": username, "Pw": password})
    
    headers = {
        "authorization": 'MediaBrowser Client="other", Device="client", DeviceId="123", Version="0.0.0"',
        "Content-Type": "application/json",
    }
    
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()
        
        data = response.json()
        auth_info = {
            "user_id": data.get("User", {}).get("Id"),
            "access_token": data.get("AccessToken"),
            "base_url": base_url,
            "is_api_key": False
        }
        
        if auth_info["user_id"] and auth_info["access_token"]:
            return auth_info
        else:
            print("Emby认证成功但未能获取User.Id或AccessToken")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Emby认证请求失败: {str(e)}")
        return None
    except json.JSONDecodeError:
        print("无法解析Emby服务器响应")
        return None


def authenticate(base_url, username, password, api_key=None):
    """
    根据服务器类型选择适当的认证方法
    
    Returns:
        dict: 包含认证信息的字典，验证失败则返回None
    """
    server_type = config.SERVER_TYPE
    
    if server_type == "jellyfin":
        return authenticate_jellyfin(base_url, username, password)
    elif server_type == "emby":
        return authenticate_emby(base_url, username, password, api_key)
    else:
        print(f"不支持的服务器类型: {server_type}")
        return None
