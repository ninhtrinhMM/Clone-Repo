import joblib
import pandas as pd
import sys
import os

# Define path
MODEL_DIR = "models"

def test_model_correctness():
    """Test model với dữ liệu mẫu và kiểm tra output"""
    try:
        # Load model
        model_path = os.path.join(MODEL_DIR, "model_ml.joblib") if os.path.exists(MODEL_DIR) else "model_ml.joblib"
        clf = joblib.load(model_path)
        print(f"✓ Model loaded successfully from: {model_path}")
        
        # Test data chuẩn
        data = {
            'person_age': -1.1189630855346455,
            'person_gender': 0.0,
            'person_education': 3.0,
            'person_income': -0.8376860072077456,
            'person_emp_exp': -0.8922841294316539,
            'person_home_ownership': 2.0,
            'loan_amnt': -1.1216727402611317,
            'loan_intent': 5.0,
            'loan_int_rate': -1.2980522333205324,
            'loan_percent_income': 0.5764744779449389,
            'cb_person_cred_hist_length': -0.9968631652782397,
            'credit_score': -1.9948081280606218,
            'previous_loan_defaults_on_file': 0.0
        }
        
        # Dự đoán
        df = pd.DataFrame(data, index=[0])
        prediction = clf.predict(df)[0]
        
        # Test trả về kết qủa 0 hoặc 1
        assert prediction in [0, 1], f"Expected prediction to be 0 or 1, got {prediction}"
        
        print(f"✓ Model prediction test passed: {prediction}")
        return True
        
    except FileNotFoundError as e:
        print(f"✗ Model file not found: {e}")
        return False
    except Exception as e:
        print(f"✗ Model test failed: {e}")
        return False


def test_multiple_predictions():
    """Test với nhiều samples cùng 1 lúc"""
    try:
        model_path = os.path.join(MODEL_DIR, "model_ml.joblib") if os.path.exists(MODEL_DIR) else "model_ml.joblib"
        clf = joblib.load(model_path)
        
        # Test đầu vào input nhiều hơn 1 mẫu
        test_data = [
            {
                'person_age': -0.6226885394054382,
                'person_gender': 0.0,
                'person_education': 3.0,
                'person_income': 0.056601043653745166,
                'person_emp_exp': -0.3975174998410627,
                'person_home_ownership': 3.0,
                'loan_amnt': 2.441376148307039,
                'loan_intent': 1.0,
                'loan_int_rate': 0.2864916517801927,
                'loan_percent_income': 1.7231143663598933,
                'cb_person_cred_hist_length': -0.4813539064709655,
                'credit_score': -1.2611950311618465,
                'previous_loan_defaults_on_file': 0.0
            },
            {
                'person_age': -0.788113388115174,
                'person_gender': 1.0,
                'person_education': 0.0,
                'person_income': 3.2976331003833987,
                'person_emp_exp': -0.8922841294316539,
                'person_home_ownership': 3.0,
                'loan_amnt': 2.322607852021433,
                'loan_intent': 1.0,
                'loan_int_rate': 0.5114163134364397,
                'loan_percent_income': -0.7994933881530069,
                'cb_person_cred_hist_length': -0.7391085358746026,
                'credit_score': 0.38447759161108175,
                'previous_loan_defaults_on_file': 1.0
            }
        ]
        
        df = pd.DataFrame(test_data)
        predictions = clf.predict(df)
        
        # Check kết quả trả về
        assert len(predictions) == 2, f"Expected 2 predictions, got {len(predictions)}"
        assert all(p in [0, 1] for p in predictions), f"All predictions should be 0 or 1, got {predictions}"
        
        print(f"✓ Multiple predictions test passed: {predictions}")
        return True
        
    except Exception as e:
        print(f"✗ Multiple predictions test failed: {e}")
        return False

def test_data_validation():
    """Test xử lý dữ liệu không hợp lệ"""
    try:
        model_path = os.path.join(MODEL_DIR, "model_ml.joblib") if os.path.exists(MODEL_DIR) else "model_ml.joblib"
        clf = joblib.load(model_path)
        
        # Test với dữ liệu thiếu Feature
        incomplete_data = {
            'person_age': -1.1189630855346455,
            'person_gender': 1.0,
            'person_education': 3.0,
        }
        
        df = pd.DataFrame(incomplete_data, index=[0])
        
        try:
            prediction = clf.predict(df)
            print("⚠ Model accepted incomplete data - this might be unexpected")
        except Exception:
            print("✓ Model correctly rejected incomplete data")
            
        return True
        
    except Exception as e:
        print(f"✗ Data validation test failed: {e}")
        return False

if __name__ == '__main__':
    
    #### Chạy tests và thoát ####
    
    exit_code = run_all_tests()
    sys.exit(exit_code)