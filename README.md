# ML_FastApi
参考视频链接：https://www.youtube.com/watch?v=lXx-_1r0Uss&t=281s
## 1 创建虚拟环境并安装对应的算法包
conda create -p venv python=3.10 -y
requirements.txt

## 2 创建FastApi使用uvicorn访问
uvicorn main:app --reload
--reload ：每次修改代码后，不需要重新启动服务
fastapi会在/docs下自动生产对应api的SOP

## 3 使用pydantic去验证数据
from pydantic import BaseModel
class User(BaseModel):



