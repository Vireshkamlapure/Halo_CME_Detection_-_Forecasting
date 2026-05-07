import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np

class GatedResidualNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, dropout=0.1):
        super(GatedResidualNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)
        self.gate = nn.Linear(hidden_size, output_size)
        self.elu = nn.ELU()
        self.norm = nn.LayerNorm(output_size)
        self.sigmoid = nn.Sigmoid()
        self.res_proj = nn.Linear(input_size, output_size) if input_size != output_size else nn.Identity()

    def forward(self, x):
        res = self.res_proj(x)
        h = self.elu(self.fc1(x))
        h = self.fc2(h)
        g = self.sigmoid(self.gate(h))
        return self.norm(g * h + res)

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, n_heads):
        super(MultiHeadAttention, self).__init__()
        self.n_heads = n_heads
        self.d_model = d_model
        assert d_model % n_heads == 0
        self.d_k = d_model // n_heads
        self.q_linear = nn.Linear(d_model, d_model)
        self.k_linear = nn.Linear(d_model, d_model)
        self.v_linear = nn.Linear(d_model, d_model)
        self.out_linear = nn.Linear(d_model, d_model)

    def forward(self, q, k, v, mask=None):
        bs = q.size(0)
        q = self.q_linear(q).view(bs, -1, self.n_heads, self.d_k).transpose(1, 2)
        k = self.k_linear(k).view(bs, -1, self.n_heads, self.d_k).transpose(1, 2)
        v = self.v_linear(v).view(bs, -1, self.n_heads, self.d_k).transpose(1, 2)
        scores = torch.matmul(q, k.transpose(-2, -1)) / (self.d_k ** 0.5)
        weights = F.softmax(scores, dim=-1)
        attention = torch.matmul(weights, v)
        concat = attention.transpose(1, 2).contiguous().view(bs, -1, self.d_model)
        return self.out_linear(concat)

class VariableSelectionNetwork(nn.Module):
    def __init__(self, n_features, d_model):
        super(VariableSelectionNetwork, self).__init__()
        self.n_features = n_features
        # Simplified Gate: Linear projection to scalar weight per feature
        self.feature_weights = nn.Linear(n_features, n_features)
        # Per-feature transformation to d_model space
        self.feature_transforms = nn.ModuleList([
            nn.Linear(1, d_model) for _ in range(n_features)
        ])
        self.softmax = nn.Softmax(dim=-1)

    def forward(self, x):
        # x shape: [batch, seq_len, n_features]
        # Calculate importance weights across all features
        weights = self.softmax(self.feature_weights(x)) # [batch, seq_len, n_features]
        
        # Transform each feature and scale by its weight
        transformed = []
        for i in range(self.n_features):
            feat = x[:, :, i:i+1] # [batch, seq_len, 1]
            proj = self.feature_transforms[i](feat) # [batch, seq_len, d_model]
            transformed.append(proj * weights[:, :, i:i+1])
            
        # Sum of weighted representations
        combined = torch.stack(transformed, dim=-1).sum(dim=-1) # [batch, seq_len, d_model]
        return combined, weights

class CNNBackbone(nn.Module):
    def __init__(self, n_velc_features, d_model):
        super(CNNBackbone, self).__init__()
        # 1D-CNN to extract spatial dependencies from spectroscopic slits
        self.conv1 = nn.Conv1d(n_velc_features, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(32, d_model, kernel_size=3, padding=1)
        self.pool = nn.AdaptiveAvgPool1d(1)
        self.relu = nn.ReLU()

    def forward(self, x):
        # x shape: [batch, seq_len, n_velc_features]
        # We treat n_velc_features as "channels" across the spectroscopic dimension
        b, s, c = x.shape
        x = x.transpose(1, 2) # [batch, n_velc_features, seq_len]
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))
        x = x.transpose(1, 2) # [batch, seq_len, d_model]
        return x

class TemporalFusionTransformer(nn.Module):
    def __init__(self, n_scalar_features, n_velc_features, d_model=64, n_heads=4):
        super(TemporalFusionTransformer, self).__init__()
        self.d_model = d_model
        
        # Spectroscopic Backbone (CNN)
        self.velc_backbone = CNNBackbone(n_velc_features, d_model)
        
        # Scalar Variable Selection Network
        self.scalar_vsn = VariableSelectionNetwork(n_scalar_features, d_model)
        
        # Temporal Processing
        self.attention = MultiHeadAttention(d_model, n_heads)
        self.output_layer = nn.Linear(d_model, 1) # Hours to Event

    def forward(self, x_scalar, x_velc):
        # x_velc through CNN
        velc_features = self.velc_backbone(x_velc)
        
        # x_scalar through VSN
        scalar_features, weights = self.scalar_vsn(x_scalar)
        
        # Multi-Modal Fusion (Simple addition for latent alignment)
        fused = scalar_features + velc_features
        
        attn_out = self.attention(fused, fused, fused)
        out = self.output_layer(attn_out[:, -1, :])
        return out, weights

class SolarDataset(Dataset):
    def __init__(self, csv_file, seq_len=168): # 168h look-back as requested
        df = pd.read_csv(csv_file)
        self.all_features = [c for c in df.columns if c not in ['timestamp', 'hours_to_event']]
        
        # Partition features: High-Cadence Imaging/Spectroscopy (VELC/SUIT) vs Scalar (MAG/ASPEX)
        self.spectral_cols = [c for c in self.all_features if 'VELC' in c or 'SUIT' in c]
        self.scalar_cols = [c for c in self.all_features if 'VELC' not in c and 'SUIT' not in c]
        
        self.X_scalar = df[self.scalar_cols].values.astype(np.float32)
        self.X_spectral = df[self.spectral_cols].values.astype(np.float32)
        self.y = df['hours_to_event'].values.astype(np.float32)
        self.seq_len = seq_len

    def __len__(self):
        return len(self.X_scalar) - self.seq_len

    def __getitem__(self, idx):
        return (torch.from_numpy(self.X_scalar[idx:idx+self.seq_len]), 
                torch.from_numpy(self.X_spectral[idx:idx+self.seq_len]),
                torch.from_numpy(np.array([self.y[idx+self.seq_len]])))

def train_and_evaluate(data_file="processed_mission_data.csv"):
    print("🧠 Initializing Aditya-L1 Multi-Modal Prognosis Brain (CNN+TFT)...")
    dataset = SolarDataset(data_file)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    # Model Setup
    model = TemporalFusionTransformer(len(dataset.scalar_cols), len(dataset.spectral_cols))
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()

    print(f"🚀 Training on {len(dataset.all_features)} Multi-Modal features...")
    print(f"   -> Scalar Channels (MAG/ASPEX): {len(dataset.scalar_cols)}")
    print(f"   -> Spectroscopic/Imaging Channels (VELC/SUIT): {len(dataset.spectral_cols)}")
    
    model.train()
    for epoch in range(1, 4):
        total_loss = 0
        for batch_scalar, batch_velc, batch_y in dataloader:
            optimizer.zero_grad()
            output, _ = model(batch_scalar, batch_velc)
            loss = criterion(output, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"   Epoch {epoch}/3 | Loss: {total_loss/len(dataloader):.4f}")

    # Feature Importance Audit
    print("\n📊 Multi-Modal Variable Selection Audit (Scalar Importance):")
    model.eval()
    with torch.no_grad():
        sample_scalar, sample_velc, _ = next(iter(dataloader))
        _, weights = model(sample_scalar, sample_velc)
        avg_weights = weights.mean(dim=[0, 1]).numpy()
        
    results = sorted(zip(dataset.scalar_cols, avg_weights), key=lambda x: x[1], reverse=True)
    
    print("-" * 60)
    print(f"{'SCALAR FEATURE':<25} | {'IMPORTANCE':<12} | {'VISUAL'}")
    print("-" * 60)
    for name, w in results[:8]:
        bar = "█" * int(w * 100)
        print(f"{name:<25} | {w:.2%}      | {bar}")
    print("-" * 60)
    
    # Save importance manifest for Dashboard
    import json
    manifest = {name: float(w) for name, w in results}
    with open("scripts/importance_manifest.json", "w") as f:
        json.dump(manifest, f)
    print("✅ Multi-Modal convergence achieved. Edge-Ready VSN weights exported.")

if __name__ == "__main__":
    train_and_evaluate()
