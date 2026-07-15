from .cli import main


# 第 1 阶段：程序入口
# 当你运行 `python -m python_study_start ...` 时，Python 会执行这个文件。
if __name__ == "__main__":
    # main() 返回整数退出码：0 通常表示成功，非 0 通常表示失败。
    raise SystemExit(main())
