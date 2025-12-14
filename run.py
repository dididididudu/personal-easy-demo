import subprocess
import sys
import os


def main():
    """启动智能客服系统的主函数"""
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 构建 test.py 的完整路径
    test_py_path = os.path.join(current_dir, 'backend', 'agents', 'test.py')

    # 检查文件是否存在
    if not os.path.exists(test_py_path):
        print(f"错误: 找不到文件 {test_py_path}")
        return 1

    try:
        # 使用 subprocess.run 启动 test.py
        # 这样可以更好地控制子进程并捕获输出
        result = subprocess.run([sys.executable, test_py_path])
        return result.returncode
    except KeyboardInterrupt:
        print("\n程序已被用户中断")
        return 0
    except Exception as e:
        print(f"启动失败: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
