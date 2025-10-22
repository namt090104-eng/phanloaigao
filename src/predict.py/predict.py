import pickle
import numpy as np
import argparse
import pandas as pd

# Tên các lớp gạo thực tế của bạn
# Đảm bảo thứ tự này khớp với thứ tự nhãn (y) khi huấn luyện mô hình.
CLASS_NAMES = ['Gạo Basmati', 'Gạo Arborio', 'Gạo Jasmine', 'Gạo Lòng Vàng', 'Gạo Giả', '...'] 

# Tên các đặc trưng gốc (không phải PCA components)
# PHẢI KHỚP VỚI ĐẶC TRƯNG BẠN DÙNG ĐỂ CHUẨN HÓA VÀ ÁP DỤNG PCA
FEATURE_NAMES = [
    'Area', 'Perimeter', 'MajorAxisLength', 'MinorAxisLength', 
    'Eccentricity', 'ConvexArea', 'EquivalentDiameter', '...' # Thêm các đặc trưng khác của bạn
]

# ----------------------------------------------------------------------
# HÀM XỬ LÝ DỮ LIỆU ĐẦU VÀO
# ----------------------------------------------------------------------

def load_and_preprocess_rf(features, scaler, pca):
    """
    Chuẩn hóa và áp dụng PCA cho dữ liệu đặc trưng đầu vào (một hạt gạo).
    
    :param features: List hoặc array các giá trị đặc trưng của hạt gạo mới.
    :param scaler: Đối tượng StandardScaler đã huấn luyện (tải từ file .pkl).
    :param pca: Đối tượng PCA đã huấn luyện (tải từ file .pkl).
    :return: Dữ liệu đã qua PCA, sẵn sàng cho dự đoán.
    """
    # 1. Chuyển đổi list đặc trưng thành mảng numpy 2D (1 mẫu, N đặc trưng)
    x = np.array(features).reshape(1, -1)
    
    # Kiểm tra số lượng đặc trưng
    if x.shape[1] != len(FEATURE_NAMES):
        raise ValueError(f"Lỗi: Số lượng đặc trưng đầu vào phải là {len(FEATURE_NAMES)}.")
    
    # 2. Chuẩn hóa (Scaling)
    x_scaled = scaler.transform(x)
    
    # 3. Áp dụng PCA
    x_pca = pca.transform(x_scaled)
    
    return x_pca

def main(args):
    # ----------------------------------------------------------------------
    # TẢI CÁC THÀNH PHẦN (SỬ DỤNG PICKLE)
    # ----------------------------------------------------------------------
    try:
        # Tải mô hình Random Forest
        with open(args.model, 'rb') as f:
            rf_model = pickle.load(f)
        
        # Tải Scaler và PCA (BẮT BUỘC nếu mô hình của bạn sử dụng chúng)
        with open(args.scaler, 'rb') as f:
            scaler = pickle.load(f)
            
        with open(args.pca, 'rb') as f:
            pca = pickle.load(f)
            
    except FileNotFoundError as e:
        print(f"Lỗi: Không tìm thấy file cần thiết. Hãy kiểm tra đường dẫn: {e}")
        return

    # ----------------------------------------------------------------------
    # XỬ LÝ ĐẦU VÀO VÀ DỰ ĐOÁN
    # ----------------------------------------------------------------------
    
    # Đầu vào là một chuỗi giá trị đặc trưng, chuyển thành list số thực
    try:
        input_features = [float(val.strip()) for val in args.features.split(',')]
    except ValueError:
        print("Lỗi: Các giá trị đặc trưng phải là số và được ngăn cách bằng dấu phẩy.")
        return

    try:
        # Tiền xử lý dữ liệu
        x_pca = load_and_preprocess_rf(input_features, scaler, pca)
        
        # Dự đoán
        pred_proba = rf_model.predict_proba(x_pca)
        idx = np.argmax(pred_proba)
        
        # In kết quả
        print("\n--- KẾT QUẢ DỰ ĐOÁN ---")
        print(f"Các đặc trưng đầu vào ({len(input_features)}): {input_features}")
        print(f"Dự đoán lớp: {CLASS_NAMES[idx]}")
        print(f"Độ tin cậy: {pred_proba[0][idx]*100:.2f}%")
        
        # Hiển thị tất cả xác suất
        print("\nXác suất chi tiết:")
        for i, class_name in enumerate(CLASS_NAMES):
             print(f"- {class_name}: {pred_proba[0][i]*100:.2f}%")
             
    except Exception as e:
        print(f"Đã xảy ra lỗi khi dự đoán: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dự đoán loại gạo bằng mô hình Random Forest.")
    
    # Thay đổi tham số đầu vào: mô hình, scaler, pca, và đặc trưng
    parser.add_argument('--model', type=str, default='random_forest_model.pkl',
                        help='Đường dẫn đến file mô hình Random Forest (.pkl)')
    parser.add_argument('--scaler', type=str, default='scaler.pkl',
                        help='Đường dẫn đến file StandardScaler (.pkl)')
    parser.add_argument('--pca', type=str, default='pca.pkl',
                        help='Đường dẫn đến file PCA (.pkl)')
    parser.add_argument('--features', type=str, required=True,
                        help=f'Giá trị đặc trưng (ví dụ: 5000, 300, 10.5, 5.2, ...). Cần {len(FEATURE_NAMES)} giá trị.')
                        
    args = parser.parse_args()
    main(args)
