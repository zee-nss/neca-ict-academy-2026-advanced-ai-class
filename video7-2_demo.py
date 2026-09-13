import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# --------------------------------------------------------
# LOAD AND PREPARE DATA
# --------------------------------------------------------

df = pd.read_csv('transactions.csv')

print("Dataset shape:", df.shape)
print()
print("First 5 rows:")
print(df.head())
print()
print("Missing values:")
print(df.isnull().sum())

# --------------------------------------------------------
# PREPROCESSING
# --------------------------------------------------------

numerical_cols = ['amount', 'frequency', 'time_of_day', 'account_age']
X = df[numerical_cols].copy()
X = X.fillna(X.median())

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print()
print("Data preprocessed and scaled.")

# --------------------------------------------------------
# ANOMALY DETECTION
# --------------------------------------------------------

iso_forest = IsolationForest(
    contamination=0.05,
    random_state=42
)

predictions = iso_forest.fit_predict(X_scaled)
df['is_anomaly'] = predictions == -1

n_anomalies = df['is_anomaly'].sum()
n_normal = len(df) - n_anomalies

print()
print("ANOMALY DETECTION RESULTS")
print("=" * 40)
print("Total transactions:", len(df))
print("Normal transactions:", n_normal)
print("Anomalies detected:", n_anomalies)
print("Anomaly rate:", round(n_anomalies / len(df) * 100, 1), "%")

# --------------------------------------------------------
# COMPARE PROFILES
# --------------------------------------------------------

print()
print("PROFILE COMPARISON")
print("=" * 40)

print()
print("NORMAL TRANSACTIONS (average):")
normal_avg = df[~df['is_anomaly']][numerical_cols].mean()
for col in numerical_cols:
    print("  ", col, ":", round(normal_avg[col], 2))

print()
print("ANOMALOUS TRANSACTIONS (average):")
anomaly_avg = df[df['is_anomaly']][numerical_cols].mean()
for col in numerical_cols:
    print("  ", col, ":", round(anomaly_avg[col], 2))

print()
print("DIFFERENCE (anomaly minus normal):")
for col in numerical_cols:
    diff = anomaly_avg[col] - normal_avg[col]
    print("  ", col, ":", round(diff, 2))

# --------------------------------------------------------
# PCA DEEP DIVE
# --------------------------------------------------------

pca_full = PCA()
pca_full.fit(X_scaled)

print()
print("PCA VARIANCE EXPLAINED")
print("=" * 40)

cumulative = 0
for i, var in enumerate(pca_full.explained_variance_ratio_):
    cumulative += var
    print("Component", i+1, ":", round(var * 100, 1), "%",
          "(Cumulative:", round(cumulative * 100, 1), "%)")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.plot(range(1, len(pca_full.explained_variance_ratio_) + 1),
         np.cumsum(pca_full.explained_variance_ratio_), 'bo-')
ax1.set_xlabel('Number of Components')
ax1.set_ylabel('Cumulative Explained Variance')
ax1.set_title('How Many Components to Keep?')
ax1.axhline(y=0.95, color='r', linestyle='--', label='95% threshold')
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2.bar(range(1, len(pca_full.explained_variance_ratio_) + 1),
        pca_full.explained_variance_ratio_)
ax2.set_xlabel('Principal Component')
ax2.set_ylabel('Explained Variance Ratio')
ax2.set_title('Variance Explained by Each Component')

plt.tight_layout()
plt.show()

# --------------------------------------------------------
# VISUALIZE ANOMALIES WITH PCA
# --------------------------------------------------------

pca_2d = PCA(n_components=2)
X_pca = pca_2d.fit_transform(X_scaled)

plt.figure(figsize=(10, 6))

normal_mask = ~df['is_anomaly']
plt.scatter(X_pca[normal_mask, 0], X_pca[normal_mask, 1],
            c='blue', label='Normal', alpha=0.4, s=20)

anomaly_mask = df['is_anomaly']
plt.scatter(X_pca[anomaly_mask, 0], X_pca[anomaly_mask, 1],
            c='red', label='Anomaly', alpha=0.9, s=60, edgecolors='black')

pc1_var = round(pca_2d.explained_variance_ratio_[0] * 100, 1)
pc2_var = round(pca_2d.explained_variance_ratio_[1] * 100, 1)

plt.xlabel('Principal Component 1 (' + str(pc1_var) + '%)')
plt.ylabel('Principal Component 2 (' + str(pc2_var) + '%)')
plt.title('Anomalies Visualized with PCA', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# --------------------------------------------------------
# EXPERIMENT WITH CONTAMINATION
# --------------------------------------------------------

print()
print("EXPERIMENTING WITH CONTAMINATION VALUES")
print("=" * 40)

for contamination in [0.02, 0.05, 0.10, 0.15]:
    iso = IsolationForest(contamination=contamination, random_state=42)
    preds = iso.fit_predict(X_scaled)
    n_anom = (preds == -1).sum()
    pct = n_anom / len(df) * 100
    
    print("Contamination =", contamination, ": Found", n_anom, 
          "anomalies (" + str(round(pct, 1)) + "%)")