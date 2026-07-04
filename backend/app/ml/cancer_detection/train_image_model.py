"""
Train a CNN for mammogram image classification.

Two modes:
  A) DEMO mode  — trains on a synthetic/toy dataset so you can test
                  the pipeline immediately without downloading anything.
  B) REAL mode  — fine-tunes EfficientNet-B0 on your mammogram dataset.
                  Point DATA_DIR at a folder with subfolders:
                      data/mammograms/malignant/
                      data/mammograms/benign/

Run from backend/:
    python -m app.ml.cancer_detection.train_image_model          # demo
    python -m app.ml.cancer_detection.train_image_model --real   # real dataset

Requirements:
    pip install torch torchvision Pillow
"""

import sys
import argparse
import json
import numpy as np
from pathlib import Path
from datetime import datetime

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, Dataset, random_split
    from torchvision import models, transforms
    from PIL import Image
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

MODELS_DIR = Path(__file__).parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

IMG_SIZE   = 224
BATCH_SIZE = 16
EPOCHS     = 10
LR         = 1e-4
DEVICE     = "cuda" if (HAS_TORCH and torch.cuda.is_available()) else "cpu"


# ── Transforms ────────────────────────────────────────────────────────────────
train_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

val_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


# ── Demo Dataset (synthetic noise images) ─────────────────────────────────────
class SyntheticMammogramDataset(Dataset):
    """
    Generates fake 'mammogram' images as coloured noise blobs.
    Class 0 = Malignant (brighter blobs), Class 1 = Benign (softer blobs).
    Only for pipeline testing — replace with real data for production.
    """
    def __init__(self, size=400, transform=None):
        self.size      = size
        self.transform = transform
        self.labels    = [i % 2 for i in range(size)]   # alternating 0/1

    def __len__(self):
        return self.size

    def __getitem__(self, idx):
        label = self.labels[idx]
        # Simulate class difference with brightness
        base = 180 if label == 0 else 100
        arr  = np.random.randint(base - 40, base + 40,
                                 (IMG_SIZE, IMG_SIZE, 3), dtype=np.uint8)
        # Add a random circular blob to simulate a mass
        cx, cy = np.random.randint(40, IMG_SIZE - 40, 2)
        r = np.random.randint(20, 60) if label == 0 else np.random.randint(10, 30)
        Y, X = np.ogrid[:IMG_SIZE, :IMG_SIZE]
        mask = (X - cx)**2 + (Y - cy)**2 <= r**2
        arr[mask] = np.clip(arr[mask] + (80 if label == 0 else 40), 0, 255)

        img = Image.fromarray(arr)
        if self.transform:
            img = self.transform(img)
        return img, label


# ── Real Dataset (folder structure) ───────────────────────────────────────────
class MammogramDataset(Dataset):
    CLASS_MAP = {"malignant": 0, "benign": 1}

    def __init__(self, root: Path, transform=None):
        self.transform = transform
        self.samples   = []
        for cls_name, label in self.CLASS_MAP.items():
            folder = root / cls_name
            if not folder.exists():
                raise FileNotFoundError(
                    f"Expected folder: {folder}\n"
                    "Create subfolders: data/mammograms/malignant/ and benign/"
                )
            for ext in ("*.jpg", "*.jpeg", "*.png", "*.bmp"):
                for p in folder.glob(ext):
                    self.samples.append((p, label))
        print(f"Dataset: {len(self.samples)} images found")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        img = Image.open(path).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, label


# ── Model ─────────────────────────────────────────────────────────────────────
def build_model():
    model = models.efficientnet_b0(weights="IMAGENET1K_V1")
    # Freeze backbone, only train classifier
    for param in model.features.parameters():
        param.requires_grad = False
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(in_features, 128),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(128, 2),   # 0=Malignant, 1=Benign
    )
    return model.to(DEVICE)


# ── Training loop ─────────────────────────────────────────────────────────────
def train_loop(model, train_loader, val_loader):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()), lr=LR
    )
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.5)

    best_val_acc = 0.0
    best_state   = None

    for epoch in range(1, EPOCHS + 1):
        # ── Train ──
        model.train()
        train_loss, train_correct, total = 0, 0, 0
        for imgs, labels in train_loader:
            imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            outputs = model(imgs)
            loss    = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            train_loss    += loss.item() * imgs.size(0)
            train_correct += (outputs.argmax(1) == labels).sum().item()
            total         += imgs.size(0)

        # ── Validate ──
        model.eval()
        val_correct, val_total = 0, 0
        with torch.no_grad():
            for imgs, labels in val_loader:
                imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
                outputs     = model(imgs)
                val_correct += (outputs.argmax(1) == labels).sum().item()
                val_total   += imgs.size(0)

        train_acc = train_correct / total
        val_acc   = val_correct   / val_total
        print(f"Epoch {epoch:02d}/{EPOCHS} | "
              f"Loss: {train_loss/total:.4f} | "
              f"Train Acc: {train_acc:.4f} | Val Acc: {val_acc:.4f}")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_state   = {k: v.cpu().clone() for k, v in model.state_dict().items()}

        scheduler.step()

    model.load_state_dict(best_state)
    return model, best_val_acc


def train(real_mode=False, data_dir="data/mammograms"):
    if not HAS_TORCH:
        print("PyTorch not installed. Run: pip install torch torchvision Pillow")
        return

    print("=" * 55)
    print(f"  She Check — Mammogram CNN Training ({'REAL' if real_mode else 'DEMO'} mode)")
    print(f"  Device: {DEVICE}")
    print("=" * 55)

    if real_mode:
        root    = Path(data_dir)
        dataset = MammogramDataset(root, transform=train_transform)
        val_sz  = max(1, int(0.2 * len(dataset)))
        trn_sz  = len(dataset) - val_sz
        train_ds, val_ds = random_split(dataset, [trn_sz, val_sz])
        val_ds.dataset.transform = val_transform
    else:
        print("Running in DEMO mode with synthetic data.")
        print("For real predictions replace with actual mammogram images.\n")
        full     = SyntheticMammogramDataset(size=400, transform=train_transform)
        val_ds   = SyntheticMammogramDataset(size=100, transform=val_transform)
        train_ds = full

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,  num_workers=0)
    val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    model, best_val_acc = train_loop(build_model(), train_loader, val_loader)

    # Save
    out_path = MODELS_DIR / "image_model.pth"
    torch.save({
        "model_state_dict": model.state_dict(),
        "architecture":     "efficientnet_b0",
        "img_size":         IMG_SIZE,
        "classes":          {0: "Malignant", 1: "Benign"},
        "trained_at":       datetime.utcnow().isoformat(),
        "mode":             "real" if real_mode else "demo",
        "best_val_acc":     round(best_val_acc, 4),
    }, out_path)

    report = {
        "trained_at":   datetime.utcnow().isoformat(),
        "mode":         "real" if real_mode else "demo",
        "best_val_acc": round(best_val_acc, 4),
        "architecture": "efficientnet_b0",
        "device":       DEVICE,
        "epochs":       EPOCHS,
    }
    with open(MODELS_DIR / "image_training_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n✅ Model saved to: {out_path}")
    print(f"   Best val accuracy: {best_val_acc:.4f}")
    print("Training complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--real",     action="store_true",      help="Use real mammogram dataset")
    parser.add_argument("--data-dir", default="data/mammograms", help="Path to dataset root")
    args = parser.parse_args()
    train(real_mode=args.real, data_dir=args.data_dir)
