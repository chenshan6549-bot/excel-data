from pathlib import Path
import importlib.util

import streamlit as st

module_path = Path(__file__).with_name("excel data.py")
spec = importlib.util.spec_from_file_location("excel_data", str(module_path))
excel_data = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(excel_data)

st.set_page_config(page_title="NV 参数知识库", layout="wide")
st.title("展锐平台 NV/APN 参数查询")

st.markdown(
    """
将仓库中的 `modem apn.xlsx` 导入本地数据库后，可通过关键字检索 `path/value/meaning/module`。
"""
)

default_excel = str(excel_data.DEFAULT_EXCEL_PATH)
excel_path = st.text_input("Excel 路径", value=default_excel)

col1, col2 = st.columns([1, 2])
with col1:
    if st.button("导入 Excel 到仓库"):
        try:
            df = excel_data.load_excel(Path(excel_path))
            if df.empty:
                st.warning("Excel 没有可导入数据")
            else:
                excel_data.save_to_repository(df)
                st.success("导入完成，共 {} 行。数据库: {}".format(len(df), excel_data.DB_PATH))
        except Exception as exc:
            st.error("导入失败: {}".format(exc))

with col2:
    st.caption("数据库位置：{}".format(excel_data.DB_PATH.resolve()))

keyword = st.text_input("输入关键字查询（例如 APN / ims / auth_type）")
limit = st.slider("返回条数", min_value=10, max_value=500, value=100, step=10)

if st.button("查询"):
    if not keyword.strip():
        st.warning("请输入关键字")
    else:
        try:
            result = excel_data.query_nv(keyword.strip(), limit=limit)
            st.write("命中 {} 条".format(len(result)))
            st.dataframe(result, use_container_width=True)
        except Exception as exc:
            st.error("查询失败: {}".format(exc))
