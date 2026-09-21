import streamlit as st
import pandas as pd

# ตั้งค่าหน้าเพจ
st.set_page_config(page_title="Parking Dashboard", page_icon="🚗", layout="wide")

st.title("🚗 Dashboard สรุปข้อมูลลานจอดรถ")
st.markdown("แสดงผลข้อมูลการเข้า-ออก และรายได้ของลานจอดรถ")

# ฟังก์ชันสำหรับโหลดข้อมูล
@st.cache_data # เพื่อให้ Streamlit ไม่ต้องอ่านไฟล์ใหม่ทุกครั้งที่รีเฟรช
def load_data():
    try:
        df = pd.read_csv("parking_records.csv", encoding="utf-8-sig")
        return df
    except FileNotFoundError:
        # ถ้าไม่มีไฟล์ ให้สร้าง DataFrame เปล่าๆ ขึ้นมาเพื่อไม่ให้พัง
        return pd.DataFrame(columns=["ทะเบียนรถ", "เวลาเข้า", "เวลาออก", "เวลารวม", "จำนวนเงินที่ต้องชำระ"])

df = load_data()

if df.empty:
    st.warning("⚠️ ยังไม่มีข้อมูลในระบบ หรือไม่พบไฟล์ parking_records.csv")
else:
    # --- Data Cleaning ---
    # ลบคำว่า ' บาท' ออก แล้วแปลงเป็นตัวเลขเพื่อนำไปคำนวณรายได้
    df['รายได้ (บาท)'] = df['จำนวนเงินที่ต้องชำระ'].astype(str).str.replace(' บาท', '')
    df['รายได้ (บาท)'] = pd.to_numeric(df['รายได้ (บาท)'], errors='coerce').fillna(0)
    
    # สกัดข้อมูล "วันที่" จาก "เวลาเข้า" สำหรับทำกราฟ
    df['เวลาเข้า_dt'] = pd.to_datetime(df['เวลาเข้า'], format="%Y-%m-%d %H:%M", errors='coerce')
    df['วันที่เข้า'] = df['เวลาเข้า_dt'].dt.date

    # --- ส่วนสรุปข้อมูล (KPIs) ---
    st.markdown("### 📊 สรุปข้อมูลโดยรวม (KPIs)")
    total_cars = len(df)
    total_revenue = df['รายได้ (บาท)'].sum()
    cars_with_no_checkout = len(df[df['เวลาออก'].isna() | (df['เวลาออก'] == "")])

    col1, col2, col3 = st.columns(3)
    col1.metric("🚗 จำนวนรถที่บันทึกทั้งหมด", f"{total_cars} คัน")
    col2.metric("💰 รายได้รวมทั้งหมด", f"{total_revenue:,.0f} บาท")
    col3.metric("⏳ รถที่ยังไม่ออก (ค้างในลาน)", f"{cars_with_no_checkout} คัน")

    st.divider() # เส้นคั่น

    # --- ส่วนกราฟ ---
    st.markdown("### 📈 กราฟแสดงรายได้ตามวันที่")
    if not df['วันที่เข้า'].isna().all():
        # รวมรายได้ตามวันที่
        revenue_by_date = df.groupby('วันที่เข้า')['รายได้ (บาท)'].sum().reset_index()
        st.bar_chart(data=revenue_by_date, x='วันที่เข้า', y='รายได้ (บาท)', color="#4CAF50")
    else:
        st.info("ยังไม่มีข้อมูลวันที่ที่สมบูรณ์พอสำหรับสร้างกราฟ")

    # --- ส่วนตารางข้อมูล ---
    st.markdown("### 📋 ตารางบันทึกการจอดรถทั้งหมด")
    # แสดงตาราง (ซ่อนคอลัมน์ที่ใช้คำนวณหลังบ้าน)
    display_df = df.drop(columns=['รายได้ (บาท)', 'เวลาเข้า_dt', 'วันที่เข้า'], errors='ignore')
    st.dataframe(display_df, use_container_width=True)