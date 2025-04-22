import os
import sys
import time
from datetime import datetime

# 导入自定义模块
import config
from gen_poster import gen_poster_workflow
from get_library import get_libraries


from get_poster import download_posters_workflow
from update_poster import upload_poster_workflow


def main():
    """
    主函数：先下载海报，然后生成九宫格海报，最后上传到 Jellyfin
    """
    print("=" * 50)
    print(f"开始执行 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 1. 获取媒体库列表

    libraries = get_libraries()
    if not libraries:
        print("未能获取媒体库列表，程序退出")
        return

    print(f"成功获取到 {len(libraries)} 个媒体库:")
    for i, library in enumerate(libraries, 1):
        print(f"  {i}. {library['Name']} (ID: {library['Id']})")

    # 这里可以根据需要选择特定的媒体库
    # 例如，选择名为"Anime"的媒体库
    target_library = None

    for library in libraries:
        print(f"找到媒体库: {library['Name']} (ID: {library['Id']})")
        # 2. 下载海报（这里假设您有一个函数来下载特定媒体库的海报）

        success = download_posters_workflow(library["Id"], library["Name"])

        if not success:
            print(f"下载海报失败: {library['Name']} (ID: {library['Id']})")
            continue

        # 3. 生成九宫格海报
        gen_poster_workflow(library["Name"])
        # 4. 上传海报到Jellyfin

        if config.JELLYFIN_CONFIG["UPDATE_POSTER"]:  # 检查是否需要更新海报
            if library["Name"] not in config.EXCLUDE_LIBRARY:
                print(f"[2/4] 上传[{library['Name']}]海报...")
                print("-" * 40)
                upload_poster_workflow(library["Id"], library["Name"])
            else:
                print(f"[2/4] 不更新[{library['Name']}]海报更新...")
                print("-" * 40)
        else:
            print(f"[2/4] 不更新[{library['Name']}]海报更新...")
            print("-" * 40)

    print("\n所有任务已完成")
    print("=" * 50)


if __name__ == "__main__":
    try:
        main()
        input("\n按回车键退出...")
    except Exception as e:
        print(f"程序运行出错: {e}")
        input("\n按回车键退出...")
