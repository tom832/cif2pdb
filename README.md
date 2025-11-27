# cif2pdb FastAPI 服务 / cif2pdb FastAPI Service

使用 PyMOL (`pymol-open-source`) 将 mmCIF 转换为 PDB 的简易 API。  
This project exposes a lightweight API using PyMOL (`pymol-open-source`) to convert mmCIF files into PDB format.

## 环境准备 / Environment Setup

本项目使用 [uv](https://github.com/astral-sh/uv) 管理依赖。若尚未安装，请参照 uv 官方说明完成安装。  
Dependencies are managed with [uv](https://github.com/astral-sh/uv). Install uv first following its official guide.

```bash
uv sync
```

上述指令会创建虚拟环境并安装 `pyproject.toml` 中列出的所有依赖。  
The command above creates a virtual environment and pulls all dependencies declared in `pyproject.toml`.

## 开发与运行 / Development & Run

```bash
# 启动 FastAPI 服务（默认监听 8000 端口）
# Start the FastAPI service (default: port 8000)
uv run uvicorn app.main:app --reload
```

启动后可发送 POST 请求到 `http://127.0.0.1:8000/convert`：  
After the server is up, send a POST request to `http://127.0.0.1:8000/convert`:

```bash
curl -X POST \
  -F "file=@example.cif" \
  http://127.0.0.1:8000/convert \
  -o output.pdb
```

若需确认服务状态，可访问 `http://127.0.0.1:8000/health`。  
Check `http://127.0.0.1:8000/health` for a basic health probe.

## Python 调用示例 / Python Usage Example

```python
import requests

url = "http://127.0.0.1:8000/convert"
with open("input_model_0.cif", "rb") as handle:
    files = {"file": ("input_model_0.cif", handle, "application/mmcif")}
    response = requests.post(url, files=files, timeout=120)
    response.raise_for_status()

with open("output_model_0.pdb", "wb") as writer:
    writer.write(response.content)
```

将本地 `input_model_0.cif` 上传转换，并保存为 `output_model_0.pdb`。  
The snippet uploads `input_model_0.cif`, receives the converted payload, and writes it to `output_model_0.pdb`.

## 测试 / Testing

```bash
uv run pytest
```

使用 `uv run pytest` 运行所有单元测试。  
Execute `uv run pytest` to run the full test suite.

