import sys
import os
import fitz
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

PDF_FILENAME = "CV_Experiment_5_Report.pdf"

PAGE_W, PAGE_H = letter # 612.0, 792.0
LEFT_M = 54.0  # 0.75 in (more margin than Exp 4's 0.55 in / 39.6 pt)
RIGHT_M = 54.0
CONTENT_W = PAGE_W - LEFT_M - RIGHT_M # 504.0 pt

CLR_HEADER_TXT = colors.HexColor("#4B5563")
CLR_HEADER_LINE = colors.HexColor("#D1D5DB")
CLR_TITLE = colors.HexColor("#111827")
CLR_SUBTITLE = colors.HexColor("#4B5563")
CLR_HEADING = colors.HexColor("#1F2937")
CLR_BODY = colors.HexColor("#374151")
CLR_CODE_TXT = colors.HexColor("#1E293B")
CLR_CODE_BG = colors.HexColor("#F8FAFC")
CLR_CODE_BORDER = colors.HexColor("#E2E8F0")
CLR_CAPTION = colors.HexColor("#4B5563")
CLR_SUMMARY = colors.HexColor("#1F2937")

class ReportBuilder:
    def __init__(self, filename):
        self.c = canvas.Canvas(filename, pagesize=letter)
        self.total_pages = 2

    def to_canvas_y(self, y_top):
        return PAGE_H - y_top

    def draw_header(self, page_num):
        self.c.setFont("Helvetica", 7.5)
        self.c.setFillColor(CLR_HEADER_TXT)
        self.c.drawString(LEFT_M, self.to_canvas_y(32.0), "Computer Vision Laboratory — Experiment Report")
        self.c.drawRightString(PAGE_W - RIGHT_M, self.to_canvas_y(32.0), f"Page {page_num} of {self.total_pages}")
        
        self.c.setStrokeColor(CLR_HEADER_LINE)
        self.c.setLineWidth(0.5)
        self.c.line(LEFT_M, self.to_canvas_y(41.0), PAGE_W - RIGHT_M, self.to_canvas_y(41.0))

    def draw_code_box(self, y_top, lines):
        line_height = 8.6
        pad_v = 4.5
        pad_h = 5.0
        box_h = len(lines) * line_height + 2 * pad_v
        
        self.c.setFillColor(CLR_CODE_BG)
        self.c.setStrokeColor(CLR_CODE_BORDER)
        self.c.setLineWidth(0.5)
        self.c.rect(LEFT_M, self.to_canvas_y(y_top + box_h), CONTENT_W, box_h, fill=1, stroke=1)
        
        self.c.setFont("Courier", 6.8)
        self.c.setFillColor(CLR_CODE_TXT)
        cur_y = y_top + pad_v + 6.8
        for line in lines:
            self.c.drawString(LEFT_M + pad_h, self.to_canvas_y(cur_y), line)
            cur_y += line_height
            
        return y_top + box_h

    def draw_body_paragraph(self, y_top, text, line_height=10.5, font_size=8.0, bold=False):
        self.c.setFont("Helvetica-Bold" if bold else "Helvetica", font_size)
        self.c.setFillColor(CLR_BODY)
        
        words = text.split(" ")
        lines = []
        cur_line = []
        for w in words:
            test_line = " ".join(cur_line + [w])
            if self.c.stringWidth(test_line, "Helvetica-Bold" if bold else "Helvetica", font_size) <= CONTENT_W - 2:
                cur_line.append(w)
            else:
                lines.append(" ".join(cur_line))
                cur_line = [w]
        if cur_line:
            lines.append(" ".join(cur_line))
            
        cur_y = y_top + font_size
        for line in lines:
            self.c.drawString(LEFT_M, self.to_canvas_y(cur_y), line)
            cur_y += line_height
            
        return cur_y - line_height + 2.0

    def draw_summary(self, y_top, label, text, line_height=10.2, font_size=7.9):
        full_text = label + " " + text
        words = full_text.split(" ")
        lines = []
        cur_line = []
        for w in words:
            test_line = " ".join(cur_line + [w])
            if self.c.stringWidth(test_line, "Helvetica", font_size) <= CONTENT_W - 2:
                cur_line.append(w)
            else:
                lines.append(" ".join(cur_line))
                cur_line = [w]
        if cur_line:
            lines.append(" ".join(cur_line))
            
        cur_y = y_top + font_size
        for idx, line in enumerate(lines):
            if idx == 0 and line.startswith(label):
                self.c.setFont("Helvetica-Bold", font_size)
                self.c.setFillColor(CLR_SUMMARY)
                self.c.drawString(LEFT_M, self.to_canvas_y(cur_y), label)
                lbl_w = self.c.stringWidth(label + " ", "Helvetica-Bold", font_size)
                self.c.setFont("Helvetica", font_size)
                self.c.drawString(LEFT_M + lbl_w, self.to_canvas_y(cur_y), line[len(label)+1:])
            else:
                self.c.setFont("Helvetica", font_size)
                self.c.setFillColor(CLR_SUMMARY)
                self.c.drawString(LEFT_M, self.to_canvas_y(cur_y), line)
            cur_y += line_height
            
        return cur_y - line_height + 2.0

    def draw_image_with_caption(self, y_top, img_path, img_w, img_h, caption):
        img_x = LEFT_M + (CONTENT_W - img_w) / 2.0
        self.c.drawImage(img_path, img_x, self.to_canvas_y(y_top + img_h), width=img_w, height=img_h)
        
        cap_y = y_top + img_h + 8.5
        self.c.setFont("Helvetica", 7.2)
        self.c.setFillColor(CLR_CAPTION)
        cap_w = self.c.stringWidth(caption, "Helvetica", 7.2)
        cap_x = LEFT_M + (CONTENT_W - cap_w) / 2.0
        self.c.drawString(cap_x, self.to_canvas_y(cap_y), caption)
        
        return cap_y + 3.0

    def build_page_1(self):
        self.draw_header(1)
        
        y = 56.0
        self.c.setFont("Helvetica-Bold", 15.5)
        self.c.setFillColor(CLR_TITLE)
        self.c.drawString(LEFT_M, self.to_canvas_y(y + 13.0), "Experiment 5")
        y += 20.0
        
        self.c.setFont("Helvetica", 9.0)
        self.c.setFillColor(CLR_SUBTITLE)
        self.c.drawString(LEFT_M, self.to_canvas_y(y + 8.0), "Discrete Sobel Gradient Operator and 2D Spatial Edge Detection")
        y += 18.0
        
        self.c.setFont("Helvetica-Bold", 10.0)
        self.c.setFillColor(CLR_HEADING)
        self.c.drawString(LEFT_M, self.to_canvas_y(y + 9.0), "1. Library Imports & Input Image Ingestion")
        y += 14.0
        
        code1 = [
            "import cv2",
            "import numpy as np",
            "import matplotlib.pyplot as plt",
            "from numpy.lib.stride_tricks import sliding_window_view",
            "image = cv2.imread(\"../Data/Dog.jpg\", cv2.IMREAD_GRAYSCALE)",
            "print(\"Image Dimensions:\", image.shape)  # Loaded grayscale: (602, 1200) | dtype: uint8",
        ]
        y = self.draw_code_box(y, code1)
        y += 9.0
        
        y = self.draw_image_with_caption(y, "report_assets/fig1_original.png", 210.0, 105.0, "Original input grayscale image (1200x602)")
        y += 15.0
        
        self.c.setFont("Helvetica-Bold", 10.0)
        self.c.setFillColor(CLR_HEADING)
        self.c.drawString(LEFT_M, self.to_canvas_y(y + 9.0), "2. Mathematical Formulation & Binomial Kernel Derivation")
        y += 14.0
        
        theory_txt = (
            "The Sobel operator is a discrete first-order gradient operator that computes an approximation of the image "
            "intensity gradient. To provide resilience against high-frequency noise, the operator factors into an outer "
            "product of a 1D binomial smoothing filter s = [1, 2, 1]^T (derived from Pascal's triangle coefficients) and a "
            "1D central difference derivative filter d = [-1, 0, 1]^T. The horizontal kernel Kx = s * d^T computes the "
            "gradient along x (isolating vertical edges), while the vertical kernel Ky = d * s^T computes the gradient along y "
            "(isolating horizontal edges). The total gradient magnitude is synthesized as G = sqrt(Gx^2 + Gy^2)."
        )
        y = self.draw_body_paragraph(y, theory_txt, line_height=10.5, font_size=8.0)
        y += 15.0
        
        self.c.setFont("Helvetica-Bold", 10.0)
        self.c.setFillColor(CLR_HEADING)
        self.c.drawString(LEFT_M, self.to_canvas_y(y + 9.0), "3. Vectorized Sobel Kernel Builder (Pascal / Binomial)")
        y += 14.0
        
        code2 = [
            "def _pascal_row(n: int) -> np.ndarray:  # Row n of Pascal's triangle (length n+1)",
            "    row = [1]",
            "    for k in range(n): row.append(row[-1] * (n - k) // (k + 1))",
            "    return np.array(row, dtype=np.float64)",
            "def compute_sobel_kernel_x(size: int) -> np.ndarray:",
            "    s = _pascal_row(size - 1); d = -np.convolve(_pascal_row(size - 2), [1, -1])",
            "    return np.outer(s, d)  # Binomial smoothing along Y, differentiation along X",
            "def compute_sobel_kernel_y(size: int) -> np.ndarray:",
            "    s = _pascal_row(size - 1); d = -np.convolve(_pascal_row(size - 2), [1, -1])",
            "    return np.outer(d, s)  # Differentiation along Y, binomial smoothing along X",
        ]
        y = self.draw_code_box(y, code2)
        y += 9.0
        
        y = self.draw_image_with_caption(y, "report_assets/fig2_kernels.png", 360.0, 134.0, "Discrete 3x3 Sobel convolution kernels: X-gradient (left) and Y-gradient (right).")
        print(f"Page 1 ends at y_top = {y:.1f} (remaining: {PAGE_H - y:.1f} pt)")
        
        self.c.showPage()

    def build_page_2(self):
        self.draw_header(2)
        
        y = 52.0
        self.c.setFont("Helvetica", 9.0)
        self.c.setFillColor(CLR_SUBTITLE)
        self.c.drawString(LEFT_M, self.to_canvas_y(y + 8.0), "Experiment 5 (continued)")
        y += 15.0
        
        self.c.setFont("Helvetica-Bold", 10.0)
        self.c.setFillColor(CLR_HEADING)
        self.c.drawString(LEFT_M, self.to_canvas_y(y + 9.0), "4. Sliding-Window 2D Spatial Convolution Pipeline")
        y += 13.0
        
        s4_txt = (
            "To avoid slow nested Python iteration, overlapping 2D spatial patches are extracted using "
            "numpy.lib.stride_tricks.sliding_window_view after reflective boundary padding (pad = k // 2). "
            "Vectorized tensor contraction against Kx and Ky produces directional gradient planes Gx and Gy, "
            "followed by Euclidean magnitude fusion G = sqrt(Gx^2 + Gy^2) and 8-bit saturation clipping."
        )
        y = self.draw_body_paragraph(y, s4_txt, line_height=10.0, font_size=8.0)
        y += 6.0
        
        code3 = [
            "def apply_sobel_filter(img: np.ndarray, kernel_size: int = 3, stride: int = 1):",
            "    kx, ky = compute_sobel_kernel_x(kernel_size), compute_sobel_kernel_y(kernel_size)",
            "    pad_amt = kernel_size // 2",
            "    padded = np.pad(img, pad_amt, mode=\"reflect\")",
            "    windows = sliding_window_view(padded, (kernel_size, kernel_size))[::stride, ::stride]",
            "    gx = (windows * kx).sum(axis=(-1, -2)); gy = (windows * ky).sum(axis=(-1, -2))",
            "    magnitude = np.hypot(gx, gy)",
            "    return np.clip(np.abs(gx), 0, 255).astype(np.uint8), \\",
            "           np.clip(np.abs(gy), 0, 255).astype(np.uint8), \\",
            "           np.clip(magnitude, 0, 255).astype(np.uint8)",
        ]
        y = self.draw_code_box(y, code3)
        y += 10.0
        
        self.c.setFont("Helvetica-Bold", 10.0)
        self.c.setFillColor(CLR_HEADING)
        self.c.drawString(LEFT_M, self.to_canvas_y(y + 9.0), "5. Benchmark Verification: Custom Implementation vs. OpenCV cv2.Sobel")
        y += 13.0
        
        code4 = [
            "k_size = 3",
            "cv_gx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=k_size)",
            "cv_gy = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=k_size)",
            "cv_combined = np.clip(np.hypot(cv_gx, cv_gy), 0, 255).astype(np.uint8)",
            "custom_edges_x, custom_edges_y, custom_combined = apply_sobel_filter(image, kernel_size=k_size)",
            "diff_map = np.abs(cv_combined.astype(np.int32) - custom_combined.astype(np.int32))",
            "mean_abs_diff = np.mean(diff_map)  # Computed MAE: 0.000 (Exact numerical equivalence)",
        ]
        y = self.draw_code_box(y, code4)
        y += 10.0
        
        self.c.setFont("Helvetica-Bold", 10.0)
        self.c.setFillColor(CLR_HEADING)
        self.c.drawString(LEFT_M, self.to_canvas_y(y + 9.0), "6. Directional Edge Detection & OpenCV Benchmark Results")
        y += 11.0
        
        y = self.draw_image_with_caption(y, "report_assets/fig3_edge_results.png", 504.0, 140.0,
            "Sobel edge detection results (k=3x3): Vertical contours Gx (left), horizontal contours Gy (center), and combined magnitude G (right).")
        y += 8.0
        
        y = self.draw_image_with_caption(y, "report_assets/fig4_opencv_comparison.png", 504.0, 128.0,
            "Verification: OpenCV cv2.Sobel vs Custom Vectorized Filter (k=3x3) | Absolute Difference Heatmap (MAE = 0.000).")
        y += 10.0
        
        summary_txt = (
            "Implemented an end-to-end discrete Sobel edge detection pipeline featuring binomial kernel derivation, "
            "reflective boundary padding, and vectorized sliding-window tensor convolution. Directional gradient analysis demonstrates "
            "that the horizontal kernel Kx isolates vertical object boundaries, while the vertical kernel Ky isolates horizontal boundaries. "
            "Combining gradients via Euclidean norm G = sqrt(Gx^2 + Gy^2) forms a complete, orientation-invariant edge representation. "
            "Cross-validation against OpenCV cv2.Sobel confirmed exact mathematical and numerical equivalence with a Mean Absolute Error "
            "(MAE) of 0.000, verifying the correctness of custom discrete spatial convolution and boundary handling."
        )
        y = self.draw_summary(y, "Summary:", summary_txt, line_height=9.8, font_size=7.8)
        print(f"Page 2 ends at y_top = {y:.1f} (remaining: {PAGE_H - y:.1f} pt)")
        
        self.c.showPage()

    def save(self):
        self.c.save()

if __name__ == "__main__":
    builder = ReportBuilder(PDF_FILENAME)
    builder.build_page_1()
    builder.build_page_2()
    builder.save()
    print(f"Updated {PDF_FILENAME} successfully!")
