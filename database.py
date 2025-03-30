from cassandra.cluster import Cluster

def connect_to_cassandra():
    cluster = Cluster(['127.0.0.1'])  # Thay đổi nếu chạy trên server khác
    session = cluster.connect()

    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS customer_db 
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}
    """)

    session.set_keyspace('customer_db')

    session.execute("""
        CREATE TABLE IF NOT EXISTS customer_churn (
            id UUID PRIMARY KEY,
            num_dependents int,
            gender text,
            churned int
        )
    """)
    
    return session

session = connect_to_cassandra()
