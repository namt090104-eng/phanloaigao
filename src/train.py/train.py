import pandas as pd
import numpy as np
import argparse
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Tên file dữ liệu gốc của bạn (ví dụ)
# Thay đổi tên file này cho phù hợp với tên file dữ liệu CSV của bạn
DEFAULT_DATA_FILE = 'rice_features_data.csv' 

def preprocess_data(df, target_column, test_size, random_state):
    """
    Tải, chia, chuẩn hóa và áp dụng PCA cho dữ liệu dạng bảng.
    """
    
    # 1. Chia đặc trưng (X) và nhãn (y)
    X = df.drop(columns=[target_column])
    y = df[target_column]
    
    # 2. Chia tập huấn luyện và kiểm tra
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # 3. Chuẩn hóa dữ liệu
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    
    # 4. Áp dụng PCA (Giả sử giữ lại 90% phương sai)
    # Tối ưu: Bạn có thể thay 0.9 bằng một số thành phần cố định (ví dụ: 5)
    pca = PCA(n_components=0.9, random_state=random_state) 
    
    X_train_pca = pca.fit_transform(X_train_scaled)
    X_val_pca = pca.transform(X_val_scaled)
    
    print(f"Dữ liệu gốc: {X.shape[1]} đặc trưng -> Dữ liệu PCA: {X_train_pca.shape[1]} thành phần.")

    # Trả về tất cả dữ liệu đã xử lý và các đối tượng tiền xử lý
    return X_train_pca, X_val_pca, y_train, y_val, scaler, pca


def main(args):
    # 1. Tải dữ liệu
    try:
        df = pd.read_csv(args.data)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file dữ liệu tại: {args.data}")
        return
    except Exception as e:
        print(f"Lỗi khi tải dữ liệu: {e}")
        return

    # 2. Tiền xử lý (Chia, Scaling, PCA)
    X_train_pca, X_val_pca, y_train, y_val, scaler, pca = preprocess_data(
        df, 
        target_column=args.target_col, # Cột nhãn
        test_size=args.test_size, 
        random_state=args.seed
    )
    
    # 3. Định nghĩa và Huấn luyện mô hình Random Forest
    rf_model = RandomForestClassifier(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        random_state=args.seed,
        n_jobs=-1,
        # Bạn có thể thêm các tham số khác ở đây (ví dụ: min_samples_split, class_weight)
    )
    
    print(f"\nBắt đầu huấn luyện Random Forest với {args.n_estimators} cây...")
    rf_model.fit(X_train_pca, y_train)
    print("Huấn luyện hoàn tất.")
    
    # 4. Đánh giá mô hình
    train_acc = rf_model.score(X_train_pca, y_train)
    val_acc = rf_model.score(X_val_pca, y_val)
    
    print(f"\nĐộ chính xác (Train): {train_acc*100:.2f}%")
    print(f"Độ chính xác (Validation): {val_acc*100:.2f}%")

    # 5. Lưu mô hình và các đối tượng tiền xử lý
    os.makedirs(os.path.dirname(args.model), exist_ok=True)
    
    # Lưu mô hình RF
    model_path = args.model
    with open(model_path, 'wb') as f:
        pickle.dump(rf_model, f)
        
    # Lưu Scaler và PCA (BẮT BUỘC để dự đoán dữ liệu mới)
    scaler_path = model_path.replace('.pkl', '_scaler.pkl')
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
        
    pca_path = model_path.replace('.pkl', '_pca.pkl')
    with open(pca_path, 'wb') as f:
        pickle.dump(pca, f)
        
    print(f"\nĐã lưu mô hình RF tới {model_path}")
    print(f"Đã lưu Scaler tới {scaler_path}")
    print(f"Đã lưu PCA tới {pca_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Huấn luyện mô hình Random Forest cho phân loại gạo.")
    
    # Tham số đầu vào mới cho Random Forest và dữ liệu dạng bảng
    parser.add_argument('--data', type=str, default=DEFAULT_DATA_FILE,
                        help='Đường dẫn đến file dữ liệu CSV chứa các đặc trưng của gạo.')
    parser.add_argument('--target_col', type=str, default='Label',
                        help='Tên cột chứa nhãn (loại gạo).')
    parser.add_argument('--model', type=str, default='models/rice_rf_model.pkl',
                        help='Đường dẫn để lưu mô hình Random Forest (.pkl).')
    parser.add_argument('--seed', type=int, default=42,
                        help='Seed ngẫu nhiên.')
    parser.add_argument('--test_size', type=float, default=0.2,
                        help='Tỷ lệ dữ liệu dành cho tập kiểm tra/validation.')

    # Siêu tham số của Random Forest
    parser.add_argument('--n_estimators', type=int, default=200,
                        help='Số lượng cây trong Random Forest.')
    parser.add_argument('--max_depth', type=int, default=12,
                        help='Độ sâu tối đa của mỗi cây.')
                        
    args = parser.parse_args()
    main(args)
