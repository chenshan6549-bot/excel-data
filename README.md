# NV/APN Excel 知识库工具

该仓库用于把 `modem apn.xlsx` 等 NV 参数 Excel 文件导入成可持续扩展的本地知识库（SQLite + CSV），并提供 UI 关键字查询。

## 1. 安装依赖

```bash
pip install -r requirements.txt
```

## 2. 导入 Excel 到仓库

```bash
python "excel data.py" import --excel "D:\\PycharmProject\\1\\modem apn.xlsx"
```

执行后会生成：
- `data/nv_knowledge.db`
- `data/nv_knowledge.csv`

后续新增更多 `.xlsx`，重复导入即可更新库。

## 3. 命令行查询

```bash
python "excel data.py" query --keyword "ims"
```

## 4. 启动 UI 查询

```bash
streamlit run app.py
```

打开浏览器后：
1. 输入 Excel 路径并点击“导入 Excel 到仓库”；
2. 输入关键字查询 NV 配置路径、默认值和含义。

## 数据库说明

默认表名：`nv_configs`，字段来自 Excel 全量列并自动补齐以下常用字段：
- `path`
- `value`
- `meaning`
- `module`
- `sheet_name`

可作为后续更多 NV Excel 的统一查询仓库。
