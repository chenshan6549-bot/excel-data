from pathlib import Path
import importlib.util

import streamlit as st

module_path = Path(__file__).with_name("excel data.py")
spec = importlib.util.spec_from_file_location("excel_data", module_path)
excel_data = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(excel_data)

st.set_page_config(page_title="NV 参数知识库", layout="wide")
st.title("展锐平台 NV/APN 参数查询")

st.markdown(
    """
将 `modem apn.xlsx` 导入本地仓库数据库后，可通过关键字检索 `path/value/meaning/module`。

> 示例路径（Windows）：`D:\\PycharmProject\\1\\modem apn.xlsx`
"""
)

excel_path = st.text_input("Excel 路径", value=r"D:\PycharmProject\1\modem apn.xlsx")

col1, col2 = st.columns([1, 2])
with col1:
    if st.button("导入 Excel 到仓库"):
        try:
            df = excel_data.load_excel(Path(excel_path))
            if df.empty:
                st.warning("Excel 没有可导入数据")
            else:
                excel_data.save_to_repository(df)
                st.success(f"导入完成，共 {len(df)} 行。数据库: {excel_data.DB_PATH}")
        except Exception as exc:
            st.error(f"导入失败: {exc}")

with col2:
    st.caption(f"数据库位置：{excel_data.DB_PATH.resolve()}")

keyword = st.text_input("输入关键字查询（例如 APN / ims / auth_type）")
limit = st.slider("返回条数", min_value=10, max_value=500, value=100, step=10)

if st.button("查询"):
    if not keyword.strip():
        st.warning("请输入关键字")
    else:
        try:
            result = excel_data.query_nv(keyword.strip(), limit=limit)
            st.write(f"命中 {len(result)} 条")
            st.dataframe(result, use_container_width=True)
        except Exception as exc:
            st.error(f"查询失败: {exc}")
