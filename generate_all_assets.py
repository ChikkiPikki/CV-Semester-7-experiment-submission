import cv2
import numpy as np
import matplotlib.pyplot as plt
from numpy.lib.stride_tricks import sliding_window_view
import os

os.makedirs('report_assets', exist_ok=True)

# 1. Load image
image = cv2.imread('Data/Dog.jpg', cv2.IMREAD_GRAYSCALE)

# Figure 1: Original input image
plt.figure(figsize=(4.8, 2.4), dpi=300)
plt.imshow(image, cmap='gray')
plt.axis('off')
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
plt.savefig('report_assets/fig1_original.png', bbox_inches='tight', pad_inches=0, dpi=300)
plt.close()

# Pascal / Sobel functions
def _pascal_row(n: int) -> np.ndarray:
    row = [1]
    for k in range(n):
        row.append(row[-1] * (n - k) // (k + 1))
    return np.array(row, dtype=np.float64)

def _sobel_smoothing_vector(size: int) -> np.ndarray:
    return _pascal_row(size - 1)

def _sobel_derivative_vector(size: int) -> np.ndarray:
    smaller = _pascal_row(size - 2)
    return -np.convolve(smaller, [1, -1])

def compute_sobel_kernel_x(size: int) -> np.ndarray:
    s = _sobel_smoothing_vector(size)
    d = _sobel_derivative_vector(size)
    return np.outer(s, d)

def compute_sobel_kernel_y(size: int) -> np.ndarray:
    s = _sobel_smoothing_vector(size)
    d = _sobel_derivative_vector(size)
    return np.outer(d, s)

k3_x = compute_sobel_kernel_x(3)
k3_y = compute_sobel_kernel_y(3)

# Figure 2: Kernels heatmap
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.6), dpi=300)
im0 = axes[0].imshow(k3_x, cmap='RdBu_r', vmin=-2, vmax=2)
axes[0].set_title('3×3 Sobel Kernel (X-Direction / Vertical Edges)', fontsize=8.5, fontweight='bold', pad=6)
for i in range(3):
    for j in range(3):
        val = k3_x[i, j]
        axes[0].text(j, i, f'{val:.0f}', ha='center', va='center',
                     color='white' if abs(val) > 1 else 'black', fontsize=10, fontweight='bold')
axes[0].set_xticks(range(3))
axes[0].set_yticks(range(3))
axes[0].set_xticklabels([-1, 0, 1], fontsize=8)
axes[0].set_yticklabels([-1, 0, 1], fontsize=8)
cbar0 = plt.colorbar(im0, ax=axes[0], fraction=0.046, pad=0.04)
cbar0.ax.tick_params(labelsize=7.5)

im1 = axes[1].imshow(k3_y, cmap='RdBu_r', vmin=-2, vmax=2)
axes[1].set_title('3×3 Sobel Kernel (Y-Direction / Horizontal Edges)', fontsize=8.5, fontweight='bold', pad=6)
for i in range(3):
    for j in range(3):
        val = k3_y[i, j]
        axes[1].text(j, i, f'{val:.0f}', ha='center', va='center',
                     color='white' if abs(val) > 1 else 'black', fontsize=10, fontweight='bold')
axes[1].set_xticks(range(3))
axes[1].set_yticks(range(3))
axes[1].set_xticklabels([-1, 0, 1], fontsize=8)
axes[1].set_yticklabels([-1, 0, 1], fontsize=8)
cbar1 = plt.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04)
cbar1.ax.tick_params(labelsize=7.5)

plt.tight_layout()
plt.savefig('report_assets/fig2_kernels.png', bbox_inches='tight', dpi=300)
plt.close()

# Custom Sobel Filter
def apply_sobel_filter(img: np.ndarray, kernel_size: int = 3, stride: int = 1):
    kx = compute_sobel_kernel_x(kernel_size)
    ky = compute_sobel_kernel_y(kernel_size)
    pad_amt = kernel_size // 2
    padded = np.pad(img, pad_amt, mode='reflect')
    windows = sliding_window_view(padded, (kernel_size, kernel_size))[::stride, ::stride]
    gx = (windows * kx).sum(axis=(-1, -2))
    gy = (windows * ky).sum(axis=(-1, -2))
    magnitude = np.hypot(gx, gy)
    edges_x = np.clip(np.abs(gx), 0, 255).astype(np.uint8)
    edges_y = np.clip(np.abs(gy), 0, 255).astype(np.uint8)
    edges_combined = np.clip(magnitude, 0, 255).astype(np.uint8)
    return edges_x, edges_y, edges_combined

edges_x, edges_y, edges_comb = apply_sobel_filter(image, kernel_size=3)

# OpenCV comparison
cv_gx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
cv_gy = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
cv_comb = np.clip(np.hypot(cv_gx, cv_gy), 0, 255).astype(np.uint8)
mae = np.mean(np.abs(cv_comb.astype(np.int32) - edges_comb.astype(np.int32)))

# Figure 3: 3-panel edge maps
fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.2), dpi=300)
axes[0].imshow(edges_x, cmap='gray')
axes[0].set_title('X-Edges (Vertical Contours)', fontsize=9, fontweight='bold', pad=4)
axes[0].axis('off')

axes[1].imshow(edges_y, cmap='gray')
axes[1].set_title('Y-Edges (Horizontal Contours)', fontsize=9, fontweight='bold', pad=4)
axes[1].axis('off')

axes[2].imshow(edges_comb, cmap='gray')
axes[2].set_title(f'Combined Magnitude G (MAE: {mae:.3f})', fontsize=9, fontweight='bold', pad=4)
axes[2].axis('off')

plt.tight_layout(w_pad=1.0)
plt.savefig('report_assets/fig3_edge_results.png', bbox_inches='tight', dpi=300)
plt.close()

# Figure 4: OpenCV benchmark comparison
diff_map = np.abs(cv_comb.astype(np.float32) - edges_comb.astype(np.float32))
fig, axes = plt.subplots(1, 3, figsize=(10.5, 2.9), dpi=300)
axes[0].imshow(cv_comb, cmap='gray')
axes[0].set_title('OpenCV cv2.Sobel Magnitude', fontsize=8.5, fontweight='bold', pad=4)
axes[0].axis('off')

axes[1].imshow(edges_comb, cmap='gray')
axes[1].set_title('Custom Sliding-Window Filter', fontsize=8.5, fontweight='bold', pad=4)
axes[1].axis('off')

im_d = axes[2].imshow(diff_map, cmap='viridis', vmin=0, vmax=1.0)
axes[2].set_title(f'Absolute Difference Heatmap (MAE = {mae:.3f})', fontsize=8.5, fontweight='bold', pad=4)
axes[2].axis('off')
cbar = plt.colorbar(im_d, ax=axes[2], fraction=0.046, pad=0.04)
cbar.ax.tick_params(labelsize=7.5)

plt.tight_layout(w_pad=1.0)
plt.savefig('report_assets/fig4_opencv_comparison.png', bbox_inches='tight', dpi=300)
plt.close()

print('Assets generated successfully!')
