import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.impute import SimpleImputer

# 1. Pembuatan Dummy Data (1000 Aset Pohon)
np.random.seed(42)
n_samples = 1000

data = {
    'Tree_ID': range(1, n_samples + 1),
    'Latitude': np.random.uniform(-3.8, -3.9, n_samples),
    'Longitude': np.random.uniform(102.2, 102.3, n_samples),
    'Tree_Age_Years': np.random.randint(5, 50, n_samples),
    'Last_Pruned_Months': np.random.randint(1, 60, n_samples),
    'Citizen_Reports_Count': np.random.poisson(lam=1.5, size=n_samples),
    'Soil_Erosion_Index': np.random.uniform(0.1, 1.0, n_samples)
}
df = pd.DataFrame(data)

# 2. Penanganan Anomali/Kebocoran Data (Simulasi Data Antar Dinas Tidak Sinkron)
# Sengaja membuat 100 data history pemeliharaan menjadi NaN
df.loc[np.random.choice(df.index, 100, replace=False), 'Last_Pruned_Months'] = np.nan

# Pembuatan Target Risk_Level (Skenario Fiktif Aturan Bisnis)
risk_score = (df['Tree_Age_Years']/50 * 0.2 + 
              df['Last_Pruned_Months'].fillna(60)/60 * 0.3 + 
              df['Citizen_Reports_Count']/5 * 0.3 + 
              df['Soil_Erosion_Index'] * 0.2)
df['Risk_Level'] = np.where(risk_score > 0.45, 1, 0) # 1: Bahaya, 0: Aman

# 3. Preprocessing
# Mengatasi Missing Value dengan teknik Imputasi Median
imputer = SimpleImputer(strategy='median')
df['Last_Pruned_Months'] = imputer.fit_transform(df[['Last_Pruned_Months']])

# Memilih Fitur Predictor
X = df[['Tree_Age_Years', 'Last_Pruned_Months', 'Citizen_Reports_Count', 'Soil_Erosion_Index']]
y = df['Risk_Level']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Modeling menggunakan Random Forest
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# 5. Prediksi dan Metrik
y_pred = rf.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}\n")
print("Classification Report:\n", classification_report(y_test, y_pred))

print("\nFeature Importances:")
for name, imp in zip(X.columns, rf.feature_importances_):
    print(f"- {name}: {imp:.4f}")