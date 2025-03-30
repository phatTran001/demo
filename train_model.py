import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from joblib import dump
from database import session

# Lấy dữ liệu từ Cassandra
rows = session.execute("SELECT num_dependents, gender, churned FROM customer_churn")
data = pd.DataFrame(rows, columns=['num_dependents', 'gender', 'churned'])

# Xử lý dữ liệu
le = LabelEncoder()
data['gender'] = le.fit_transform(data['gender'])

X = data[['num_dependents', 'gender']]
y = data['churned']

# Chia tập huấn luyện và kiểm tra
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Huấn luyện mô hình Logistic Regression
model = LogisticRegression()
model.fit(X_train, y_train)

# Lưu mô hình
dump(model, 'churn_model.joblib')
print("Mô hình đã được huấn luyện và lưu lại.")
