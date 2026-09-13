import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# --------------------------------------------------------
# LOAD DATA
# --------------------------------------------------------

df = pd.read_csv('customer_data.csv')

print("Dataset shape:", df.shape)
print()
print("First 5 rows:")
print(df.head())
print()
print("Data description:")
print(df.describe())

# --------------------------------------------------------
# STEP 1: SCALE THE DATA
# --------------------------------------------------------

features = ['total_spend', 'num_orders', 'avg_order_value',
            'days_since_last_order', 'num_support_tickets']
X = df[features]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print()
print("Data scaled. All features now have mean=0 and standard deviation=1.")

# --------------------------------------------------------
# STEP 2: FIND OPTIMAL K — ELBOW METHOD
# --------------------------------------------------------

print()
print("Running elbow method...")
print()

inertias = []
K_range = range(1, 11)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertias.append(kmeans.inertia_)
    print("K =", k, " Inertia:", round(kmeans.inertia_, 2))

plt.figure(figsize=(10, 5))
plt.plot(K_range, inertias, 'bo-', linewidth=2, markersize=8)
plt.xlabel('Number of Clusters (K)')
plt.ylabel('Inertia')
plt.title('Elbow Method — Find the Optimal Number of Clusters', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.xticks(K_range)
plt.tight_layout()
plt.show()

# --------------------------------------------------------
# STEP 3: RUN K-MEANS
# --------------------------------------------------------

OPTIMAL_K = 4

kmeans = KMeans(n_clusters=OPTIMAL_K, random_state=42, n_init=10)
df['segment'] = kmeans.fit_predict(X_scaled)

print()
print("K-Means complete with", OPTIMAL_K, "clusters")
print()
print("Customers per segment:")
print(df['segment'].value_counts().sort_index())

# --------------------------------------------------------
# STEP 4: VISUALIZE WITH PCA
# --------------------------------------------------------

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

print()
print("PCA explained variance:", pca.explained_variance_ratio_)
print("Total variance captured:", round(sum(pca.explained_variance_ratio_) * 100, 1), "%")

plt.figure(figsize=(10, 6))
colors = ['#E74C3C', '#3498DB', '#2ECC71', '#F39C12']

for i in range(OPTIMAL_K):
    mask = df['segment'] == i
    plt.scatter(X_pca[mask, 0], X_pca[mask, 1], 
                label='Segment ' + str(i), alpha=0.6, c=colors[i])

plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.title('Customer Segments Visualized', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# --------------------------------------------------------
# STEP 5: PROFILE EACH SEGMENT
# --------------------------------------------------------

print()
print("=" * 60)
print("CUSTOMER SEGMENT PROFILES")
print("=" * 60)

for i in range(OPTIMAL_K):
    segment = df[df['segment'] == i]
    
    print()
    print("SEGMENT", i, ":", len(segment), "customers")
    print("-" * 40)
    
    avg_spend = segment['total_spend'].mean()
    avg_orders = segment['num_orders'].mean()
    avg_value = segment['avg_order_value'].mean()
    avg_days = segment['days_since_last_order'].mean()
    avg_tickets = segment['num_support_tickets'].mean()
    
    print("  Average Total Spend:     $" + str(round(avg_spend, 2)))
    print("  Average Num Orders:       " + str(round(avg_orders, 1)))
    print("  Average Order Value:     $" + str(round(avg_value, 2)))
    print("  Avg Days Since Last Order:" + str(round(avg_days, 1)))
    print("  Avg Support Tickets:      " + str(round(avg_tickets, 1)))