import os
import sys
root_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(root_dir, "../..")
## parenddir 是当前代码文件所在目录的父目录
# parenddir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
# sys.path.append(parenddir)
sys.path.append(project_dir)

from gameUtils.recognition import Rectangle

__all__ = ['Rectangle']