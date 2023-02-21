from pathlib import Path

import pandas as pd
import streamlit as st
import utils
import numpy as np
import time

st.set_page_config(
    page_title="صادرات مصر",
    page_icon=str(Path(__file__).parent / "assets/bar-chart_.png"),
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None,
)

# Read data
dataset_path = Path(__file__).parent / "dataset"
df_metadata = pd.read_json(dataset_path / "metadata.json", orient="records")
df_metadata = utils.normalize_money(df_metadata, "Export Amount", "Export Value")
if 'start_time' not in st.session_state:
    st.session_state['start_time'] = time.time()

# Zip dataset folder
zip_path = Path(__file__).parent / "exports_dataset.zip"
utils.zip_directory(dataset_path, zip_path)

# Global style for the app
global_style = """
			<style>
            @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600&family=Tajawal:wght@700&display=swap');

            html, body, [class*="css"]  {
			font-family: 'Cairo';
			}
            .sidebar {
            font-weight: bold;
            # color: #0f0d09;
            }
            table {
            direction: rtl;
            text-align: center;
            width: 100%;
            }
            th {
            text-align: center;
            font-family: 'Tajawal';
            color: black; 
            }
            p {
            text-align: center;
            }
			</style>
			"""
st.markdown(global_style, unsafe_allow_html=True)

# Some useful templates
country_name_template = "<p style='color: {country_color};text-align: center;'>{country_name} ({country_code})</p>"
beautiful_shape = "<br> . <br> ……… <br> ……………… <br> ……………………… <br> …………………………… <br> ……………………… <br> ……………… <br> ……… <br> ."

# Add sidebar to streamlit and use it to customize the experience
st.sidebar.markdown("<h1><b class='sidebar'>Customi</b>ze <b class='sidebar'>you</b>r <b class='sidebar'>Experien</b>ce</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<h3> ⭐ <b class='sidebar'>Chapt</b>er 1 <b class='sidebar'>Configurati</b>ons</h3>", unsafe_allow_html=True)
show_legend = st.sidebar.checkbox("Show Legend", value=True)
top_k_countries = st.sidebar.slider("Top Exporting Countries to Show", min_value=1, max_value=len(df_metadata), value=int(0.25*len(df_metadata)))
st.sidebar.markdown("""---""")
st.sidebar.markdown("<h3> ⭐ <b class='sidebar'>Chapt</b>er 2 <b class='sidebar'>Configurati</b>ons</h3>", unsafe_allow_html=True)
diagram_option = st.sidebar.selectbox("Select Type of Diagram to show", ["Bar Chart", "Line Chart"], index=1)
chapter2_num_columns = st.sidebar.slider("Number of side-by-side graphs", min_value=1, max_value=4, value=2)
st.sidebar.markdown("""---""")
st.sidebar.markdown("<h3> ⭐ <b class='sidebar'>Chapt</b>er 3 <b class='sidebar'>Configurati</b>ons</h3>", unsafe_allow_html=True)
# chapter3_num_columns = st.sidebar.select_slider("Number of side-by-side dataframes", options=[1,2,3], value=1)
chapter3_num_columns = 1
top_n_items = st.sidebar.select_slider("Show only top N items", options=list(range(1,21))+["All"], value=10)

# Make a hidden present pop after 5 minutes
if time.time() - st.session_state['start_time'] > 60*5:
    enable_surprise = st.sidebar.checkbox("🎁 Unlock Present", value=False, help="Congrats, You can click to view a hidden chapter")
else:
    enable_surprise = st.sidebar.checkbox("🎁 Unlock Present", value=False, help="I can crawl, I can fly, I have hands but no legs or wings either. What am I?", disabled=True)

# Add title to the app
st.markdown("<h1 style='text-align:center;'>This will be a fun story about Egypt's exports 🤭</h1> <br>", unsafe_allow_html=True)

# Chapter 1: The Story of the largest countries we export to
with st.expander("Chapter 1: The Story of the largest countries we export to", expanded=False):
    st.markdown("<h3 style='direction: rtl; text-align:center;'>أكثر الدول التى صدرت لها مصر 🇪🇬</h3> <br>", unsafe_allow_html=True)
    sorted_df_metadata = df_metadata.sort_values(by="Export Amount", ascending=False)[:top_k_countries].reset_index()
    # print(sorted_df_metadata)
    st.vega_lite_chart(
                sorted_df_metadata,
                {
                    "mark": {"type": "bar", "cornerRadiusEnd": 8},
                    "encoding": {
                        "x": {"field": "Country Code", "type": "nominal", "title": "Country Code", "axis": {"labelAngle": -60}, "sort": "-y"},
                        "y": {
                            "field": "Export Amount",
                            "type": "quantitative",
                            "title": "Export Amount in Million Dollars",
                        }
                    },
                },
                use_container_width=True,
            )
    if show_legend:
        num_columns_to_split = 4
        columns = st.columns(num_columns_to_split)
        legend = sorted_df_metadata[["Country Code", "Country Name"]]
        legend = legend.rename(columns={"Country Code": "كود البلد", "Country Name": "أسم الدولة"})
        splits = np.array_split(legend, num_columns_to_split)
        for idx, legend in enumerate(splits):
            columns[idx].markdown(legend.to_html(index=False), unsafe_allow_html=True)

# Chapter 2: What happened in the last 10 years ?
with st.expander("Chapter 2: What happened in the last 10 years ?", expanded=False):
    st.markdown("<h3 style='direction: rtl; text-align:center;'>كم صدرنا إلى الدول المختلفة على مدار ال 10 سنين السابقة ؟ 💸</h3> <br>", unsafe_allow_html=True)
    countries_selected = st.multiselect("Select Countries", df_metadata["Country Name"].values, default="السعودية")

    columns = st.columns(chapter2_num_columns)
    for idx, country_selected_name in enumerate(countries_selected):
        country_selected_code = df_metadata.loc[df_metadata["Country Name"] == country_selected_name, "Country Code"].values[0]
        country_path = dataset_path / country_selected_code
        country_color = df_metadata.loc[df_metadata["Country Name"] == country_selected_name, "Color"].values[0]
        # monthly_df = pd.read_csv(country_path / "monthly.csv", index_col=False)
        # monthly_df["Export Amount"] = monthly_df["Export Amount"].apply(lambda x: utils.str_money2int(x))
        
        yearly_df = pd.read_csv(country_path / "yearly.csv", index_col=False)
        yearly_df = utils.normalize_money(yearly_df, "Export Amount", "Export Value")

        columns[idx % chapter2_num_columns].markdown(country_name_template.format(country_name=country_selected_name, country_code=country_selected_code, country_color=country_color), unsafe_allow_html=True)
        if diagram_option == "Bar Chart":
            columns[idx % chapter2_num_columns].vega_lite_chart(
                yearly_df,
                {
                    "mark": {"type": "bar", "cornerRadiusEnd": 8, "color": df_metadata.iloc[idx]["Color"]},
                    "encoding": {
                        "y": {"field": "Year", "type": "ordinal", "title": "Year"},
                        "x": {
                            "field": "Export Amount",
                            "type": "quantitative",
                            "title": "Export Amount in Million Dollars",
                        },
                    },
                },
                use_container_width=True,
            )
        elif diagram_option == "Line Chart":
            columns[idx % chapter2_num_columns].vega_lite_chart(
                yearly_df,
                {
                    "mark": {"type": "line", "point": True, "color": df_metadata.iloc[idx]["Color"]},
                    "encoding": {
                        "x": {"field": "Year", "type": "ordinal", "title": "Year", "axis": {"labelAngle": 0}},
                        "y": {
                            "field": "Export Amount",
                            "type": "quantitative",
                            "title": "Export Amount in Million Dollars",
                        },
                    },
                },
                use_container_width=True,
            )
        else:
            raise ValueError("Diagram option not found")
        
# Chapter 3: What items we export ?
with st.expander("Chapter 3: What items we export ?", expanded=False):
    st.markdown("<h3 style='direction: rtl; text-align:center;'>لماذا الغاز الطبيعى والبرتقال ؟ 🍊</h3> <br>", unsafe_allow_html=True)

    countries_picked = st.multiselect("Pick a Country", df_metadata["Country Name"].values, default="السعودية")
    chapter3_columns = st.columns(chapter3_num_columns)
    for idx, country_picked_name in enumerate(countries_picked):
        country_code = df_metadata.loc[df_metadata["Country Name"] == country_picked_name, "Country Code"].values[0]
        country_path = dataset_path / country_code
        country_name = df_metadata.loc[df_metadata["Country Code"] == country_code, "Country Name"].values[0]
        country_color = df_metadata.loc[df_metadata["Country Code"] == country_code, "Color"].values[0]
        items_df = pd.read_csv(country_path / "items.csv", index_col=False)
        items_df = utils.normalize_money(items_df, "Amount", "Value")
        items_df.drop(columns=["Value"], inplace=True)
        items_df["Amount"] = items_df["Amount"].apply(lambda x: f"{x:.3f}")
        items_df.rename(columns={"Amount": "الصادرات بالمليون دولار"}, inplace=True)
        items_df.rename(columns={"Item": "المنتجات"}, inplace=True)
        items_df.fillna("غير معلوم", inplace=True)
        filtered_items_df = items_df[:top_n_items] if isinstance(top_n_items, int) else items_df

        chapter3_columns[idx % chapter3_num_columns].markdown(country_name_template.format(country_name=country_name, country_code=country_code, country_color=country_color), unsafe_allow_html=True)
        chapter3_columns[idx % chapter3_num_columns].markdown(filtered_items_df.to_html(index=False) + "<br>", unsafe_allow_html=True)
        
with st.expander("Chapter 4: What do you think ?", expanded=False):
    st.markdown("<p>💝 أتمنى هذه الأداة المتواضعة تساعد شخص ما على إتخاذ قرار جيد بخصوص مشروعه القادم</p>", unsafe_allow_html=True)
    st.markdown(f"<p>💩 أخيرا وليس أخرا … إذا وجدت الموقع مفيد يمكنك دعمه عن طريق <a href='https://www.youtube.com/watch?v=m7KFeyJigAc'> النجاح فى الحياة </a></p>", unsafe_allow_html=True)
    st.markdown(f"<p>🕵️ أو التبرع لمؤسسة <a href='https://mersal-ngo.org/'>مرسال</a> أو مساعدة <a href='https://www.facebook.com/profile.php?id=100090486334314'>طلبة هندسة عين شمس</a> {beautiful_shape}</p>", unsafe_allow_html=True)

    if enable_surprise:
        # Download dataset zip file
        with open(zip_path, "rb") as fp:
            st.columns(3)[1].download_button(
            # st.sidebar.download_button(
                label="📦 تحميل البيانات",
                data=fp,
                file_name="dataset.zip",
                mime="application/zip",
                use_container_width=True,
            )

    st.balloons()

if enable_surprise:
    st.snow()
    with st.expander("Chapter 5: Helpful Material", expanded=False):
        st.markdown("<h3 style='direction: rtl; text-align:center;'> مصادر أقتصادية مفيدة 📚</h3> <br>", unsafe_allow_html=True)
        st.write('- [When Client Says "Your Price Is Too High"– How To Respond](https://www.youtube.com/watch?v=RFk8ZmIDrFM) ')
        st.write('- [Feel the Pain](https://www.youtube.com/watch?v=uWX2g0QplSg)')
        st.write('- [How & When To Raise Your Rates (The 3x Rule)](https://www.youtube.com/watch?v=Dr4Ux8_mfU8)')
        st.write('- [MBA in one day Book](https://www.kutubpdfbook.com/book/%D9%85%D8%A7%D8%AC%D8%B3%D8%AA%D9%8A%D8%B1-%D8%A3%D8%AF%D8%A7%D8%B1%D8%A9-%D8%A7%D9%84%D8%A7%D8%B9%D9%85%D8%A7%D9%84-%D9%81%D9%8A-%D9%8A%D9%88%D9%85-%D9%88%D8%A7%D8%AD%D8%AF)')
        st.write('- [Why Customers Buy (Marketing Fundamentals)](https://www.youtube.com/watch?v=TVqXHVCmfHE)')
        st.markdown("<br> <span style='text-align: right;'> هذا ملف صوتى غير مهم (لا تضيع وقتك فى سماعه)</span> <br>", unsafe_allow_html=True)
        st.audio(str(Path(__file__).parent / "assets"  / "surprise.webm"), format="audio/webm")