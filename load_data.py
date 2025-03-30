import pandas as pd
import uuid
from database import session

# Đọc dữ liệu từ CSV và xử lý lỗi tên cột
df = pd.read_csv('WA_Fn-UseC_-Telco-Customer-Churn.csv')
df.columns = df.columns.str.strip()  # Xóa khoảng trắng trong tên cột

# Kiểm tra lại tên cột chính xác
if 'Dependents' not in df.columns or 'Churn' not in df.columns:
    raise KeyError("Tên cột không khớp! Kiểm tra lại tên cột trong CSV.")

# Chuyển đổi dữ liệu phù hợp với bảng Cassandra
df['num_dependents'] = df['Dependents'].apply(lambda x: 1 if str(x).strip().lower() == 'yes' else 0)
df['churned'] = df['Churn'].apply(lambda x: 1 if str(x).strip().lower() == 'yes' else 0)

# Chèn dữ liệu vào Cassandra
for _, row in df.iterrows():
    session.execute("""
        INSERT INTO customer_db.customer_churn (id, num_dependents, gender, churned)
        VALUES (%s, %s, %s, %s)
    """, (uuid.uuid4(), row['num_dependents'], row['gender'], row['churned']))

print("Dữ liệu đã được nạp vào Cassandra thành công!")

