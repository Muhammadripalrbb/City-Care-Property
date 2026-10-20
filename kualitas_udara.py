import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error

# 1. GENERATE DUMMY DATA (Simulasi 2 Tahun Data Harian)
np.random.seed(42)
days = 365 * 2 
dates = pd.date_range(start='2024-01-01', periods=days, freq='D')

# Membuat variabel cuaca sintetis
temp = np.random.normal(28, 2, days) + np.sin(np.linspace(0, 4*np.pi, days)) * 2
humidity = np.random.normal(75, 10, days)
wind_speed = np.random.exponential(3, days)

# PM 2.5 berkorelasi dengan suhu & berbanding terbalik dengan angin (ditambah noise)
pm25_base = 20 + (temp - 28)*2 - wind_speed*1.5 + np.random.normal(0, 5, days)
pm25 = np.maximum(pm25_base, 5) # PM 2.5 tidak bisa negatif

df = pd.DataFrame({
    'Date': dates, 'Temperature_C': temp, 'Humidity_percent': humidity,
    'Wind_Speed_ms': wind_speed, 'PM25': pm25
})

# Menambahkan Anomali: Mensimulasikan 5% data hilang karena sensor IoT rusak
missing_idx = np.random.choice(df.index, size=int(0.05*len(df)), replace=False)
df.loc[missing_idx, 'PM25'] = np.nan

# 2. DATA PREPARATION & HANDLING
# Mengatasi Missing Value dengan Interpolasi Linier
df['PM25'] = df['PM25'].interpolate(method='linear')

# Feature Engineering: Membuat Lag Variables (Histori polusi H-1 dan H-2)
df['PM25_Lag1'] = df['PM25'].shift(1)
df['PM25_Lag2'] = df['PM25'].shift(2)
df.dropna(inplace=True) # Hapus 2 baris pertama karena pergeseran lag

# Menyiapkan Variabel X (Fitur) dan Y (Target)
X = df[['Temperature_C', 'Humidity_percent', 'Wind_Speed_ms', 'PM25_Lag1', 'PM25_Lag2']]
y = df['PM25']

# Split Data Tuntun Waktu (80% Train, 20% Test)
split_idx = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

# 3. PEMODELAN AI
model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# 4. EVALUASI METRIK
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae = mean_absolute_error(y_test, y_pred)
print(f"Hasil Evaluasi -> RMSE: {rmse:.2f} | MAE: {mae:.2f}")