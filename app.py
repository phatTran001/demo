import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from joblib import load
from database import session  # Giả định đây là kết nối đến Cassandra

# Load mô hình đã huấn luyện
try:
    model = load('churn_model.joblib')
except FileNotFoundError:
    st.error("Không tìm thấy file 'churn_model.joblib'. Vui lòng đảm bảo file mô hình đã được huấn luyện và đặt đúng thư mục.")
    st.stop()

# Truy vấn dữ liệu từ Cassandra
try:
    rows = session.execute("SELECT num_dependents, gender, churned FROM customer_churn")
    data = pd.DataFrame(rows, columns=['num_dependents', 'gender', 'churned'])
except Exception as e:
    st.error(f"Lỗi khi truy vấn dữ liệu từ Cassandra: {str(e)}")
    st.stop()

# Thêm cột "has_dependents" để phân loại Có/Không người phụ thuộc
data['has_dependents'] = data['num_dependents'].apply(lambda x: 'Yes' if x > 0 else 'No')

# Thêm cột customerID nếu không có trong dữ liệu
if 'customerID' not in data.columns:
    data['customerID'] = [f'000{i}-XYZ' for i in range(1, len(data) + 1)]

# Thiết lập giao diện
st.set_page_config(layout="wide")
st.title("Phân Tích Khả Năng Khách Hàng Rời Khỏi Dịch Vụ Dựa Trên Số Người Phụ Thuộc Và Giới Tính")

# Tạo các tab
tab1, tab2 = st.tabs(["Dữ Liệu & Thống Kê", "Trực Quan Hóa Dữ Liệu"])

# --- Tab 1: Dữ Liệu & Thống Kê ---
with tab1:
    # Phần 1: Lọc dữ liệu & Dự đoán
    st.subheader("🔎 Lọc Dữ Liệu & Dự Đoán")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    # Lọc theo giới tính
    with col1:
        gender_filter = st.selectbox("Lọc theo giới tính", ["All", "Male", "Female"])

    # Lọc theo trạng thái có/không người phụ thuộc
    with col2:
        dependents_filter = st.selectbox("Lọc theo trạng thái người phụ thuộc", ["All", "Yes", "No"])

    # Nhập liệu để dự đoán
    with col3:
        has_dependents = st.selectbox("Có người phụ thuộc (Dự đoán)", ["Yes", "No"])  # Thay slider bằng selectbox
    with col4:
        gender = st.selectbox("Giới tính (Dự đoán)", ["Male", "Female"])
    gender_encoded = 1 if gender == "Male" else 0

    # Chuyển đổi has_dependents thành num_dependents để phù hợp với mô hình
    num_dependents = 1 if has_dependents == "Yes" else 0

    # Áp dụng bộ lọc
    filtered_data = data.copy()
    if gender_filter != "All":
        filtered_data = filtered_data[filtered_data['gender'] == gender_filter]
    if dependents_filter != "All":
        filtered_data = filtered_data[filtered_data['has_dependents'] == dependents_filter]

    # Nút "Dự đoán" được tích hợp vào phần lọc
    if st.button("Dự đoán"):
        # Chuẩn bị dữ liệu đầu vào cho mô hình
        input_data = np.array([[num_dependents, gender_encoded]])
        try:
            prediction = model.predict(input_data)[0]
            if prediction == 1:
                st.error(f"Kết quả: Khách hàng SẼ rời bỏ dịch vụ!")
            else:
                st.success(f"Kết quả: Khách hàng KHÔNG rời bỏ dịch vụ.")
            st.write(f"Có người phụ thuộc: {has_dependents}")
            st.write(f"Giới tính: {gender}")
        except Exception as e:
            st.error(f"Lỗi khi dự đoán: {str(e)}")
            st.write("Vui lòng kiểm tra mô hình và dữ liệu đầu vào.")

    # Hiển thị dữ liệu đã lọc
    st.subheader("📌 Dữ Liệu Khách Hàng Đã Lọc")
    st.dataframe(filtered_data[['customerID', 'num_dependents', 'gender', 'has_dependents', 'churned']])

    # Phần 2: Thống kê dữ liệu bằng bảng số liệu
    st.subheader("📈 Thống Kê Dữ Liệu")
    total_customers = len(filtered_data)
    customers_churned = filtered_data['churned'].sum()
    churn_rate = (customers_churned / total_customers) * 100 if total_customers > 0 else 0
    avg_num_dependents = filtered_data['num_dependents'].mean()

    # Hiển thị thống kê
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tổng số khách hàng", total_customers)
    col2.metric("Số khách hàng rời bỏ", customers_churned)
    col3.metric("Tỷ lệ rời bỏ", f"{churn_rate:.2f}%")
    col4.metric("Số người phụ thuộc trung bình", f"{avg_num_dependents:.2f}")

# --- Tab 2: Trực Quan Hóa Dữ Liệu ---
with tab2:
    st.subheader("📊 Trực Quan Hóa Dữ Liệu")

    # Sắp xếp 2 biểu đồ trên 1 hàng
    col1, col2 = st.columns(2)

    # Biểu đồ 1: Phân bố số người phụ thuộc theo trạng thái rời bỏ
    with col1:
        st.write("Phân bố số người phụ thuộc theo trạng thái rời bỏ")
        fig1, ax1 = plt.subplots(figsize=(5, 3))
        sns.histplot(data=filtered_data, x="num_dependents", hue="churned", multiple="stack", ax=ax1)
        ax1.set_title("Churn by Number of Dependents", fontsize=10)
        ax1.set_xlabel("Number of Dependents", fontsize=8)
        ax1.set_ylabel("Count", fontsize=8)
        ax1.tick_params(axis='both', labelsize=8)
        plt.tight_layout()
        st.pyplot(fig1)

    # Biểu đồ 2: Tỷ lệ rời bỏ theo giới tính
    with col2:
        st.write("Tỷ lệ rời bỏ theo giới tính")
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        sns.countplot(data=filtered_data, x='gender', hue='churned', ax=ax2)
        ax2.set_title("Churn Rate by Gender", fontsize=10)
        ax2.set_xlabel("Gender", fontsize=8)
        ax2.set_ylabel("Count", fontsize=8)
        ax2.tick_params(axis='both', labelsize=8)
        plt.tight_layout()
        st.pyplot(fig2)

    # Sắp xếp 2 biểu đồ tiếp theo trên 1 hàng
    col3, col4 = st.columns(2)

    # Biểu đồ 3: Tỷ lệ rời bỏ theo trạng thái có/không người phụ thuộc
    with col3:
        st.write("Tỷ lệ rời bỏ theo trạng thái có/không người phụ thuộc")
        fig3, ax3 = plt.subplots(figsize=(5, 3))
        sns.countplot(data=filtered_data, x='has_dependents', hue='churned', ax=ax3)
        ax3.set_title("Churn Rate by Dependents Status", fontsize=10)
        ax3.set_xlabel("Has Dependents", fontsize=8)
        ax3.set_ylabel("Count", fontsize=8)
        ax3.tick_params(axis='both', labelsize=8)
        plt.tight_layout()
        st.pyplot(fig3)

    # Biểu đồ 4: Phân bố trạng thái rời bỏ
    with col4:
        st.write("Phân bố trạng thái rời bỏ")
        fig4, ax4 = plt.subplots(figsize=(4, 3))
        filtered_data['churned'].value_counts().plot.pie(autopct='%1.1f%%', labels=['Not Churned', 'Churned'], ax=ax4, textprops={'fontsize': 8})
        ax4.set_title("Churn Distribution", fontsize=10)
        plt.tight_layout()
        st.pyplot(fig4)