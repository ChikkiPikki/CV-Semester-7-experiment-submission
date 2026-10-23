import sys
import os
import fitz
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

PDF_FILENAME = "CV_Experiment_8_Report.pdf"

PAGE_W, PAGE_H = letter # 612.0, 792.0
LEFT_M = 54.0  # 0.75 in margin (generous margin)
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
CLR_TABLE_BORDER = colors.HexColor("#CBD5E1")
CLR_TABLE_BG = colors.HexColor("#F1F5F9")

class SinglePageReportBuilder:
    def __init__(self, filename):
        self.c = canvas.Canvas(filename, pagesize=letter)

    def to_canvas_y(self, y_top):
        return PAGE_H - y_top

    def draw_header(self):
        self.c.setFont("Helvetica", 7.5)
        self.c.setFillColor(CLR_HEADER_TXT)
        self.c.drawString(LEFT_M, self.to_canvas_y(28.0), "Computer Vision Laboratory — Experiment Report")
        self.c.drawRightString(PAGE_W - RIGHT_M, self.to_canvas_y(28.0), "Page 1 of 1")
        
        self.c.setStrokeColor(CLR_HEADER_LINE)
        self.c.setLineWidth(0.5)
        self.c.line(LEFT_M, self.to_canvas_y(36.0), PAGE_W - RIGHT_M, self.to_canvas_y(36.0))

    def draw_code_box(self, y_top, lines, line_height=7.4, font_size=6.2):
        pad_v = 3.5
        pad_h = 5.0
        box_h = len(lines) * line_height + 2 * pad_v
        
        self.c.setFillColor(CLR_CODE_BG)
        self.c.setStrokeColor(CLR_CODE_BORDER)
        self.c.setLineWidth(0.5)
        self.c.rect(LEFT_M, self.to_canvas_y(y_top + box_h), CONTENT_W, box_h, fill=1, stroke=1)
        
        self.c.setFont("Courier", font_size)
        self.c.setFillColor(CLR_CODE_TXT)
        cur_y = y_top + pad_v + font_size - 0.2
        for line in lines:
            self.c.drawString(LEFT_M + pad_h, self.to_canvas_y(cur_y), line)
            cur_y += line_height
            
        return y_top + box_h

    def draw_image_with_caption(self, y_top, img_path, img_w, img_h, caption):
        img_x = LEFT_M + (CONTENT_W - img_w) / 2.0
        self.c.drawImage(img_path, img_x, self.to_canvas_y(y_top + img_h), width=img_w, height=img_h)
        
        cap_y = y_top + img_h + 7.0
        self.c.setFont("Helvetica", 6.8)
        self.c.setFillColor(CLR_CAPTION)
        cap_w = self.c.stringWidth(caption, "Helvetica", 6.8)
        cap_x = LEFT_M + (CONTENT_W - cap_w) / 2.0
        self.c.drawString(cap_x, self.to_canvas_y(cap_y), caption)
        
        return cap_y + 2.0

    def draw_table(self, y_top):
        row_h = 10.5
        headers = ["Target", "Ground Truth (m, c)", "Cartesian (m, c) Detected", "Polar (r, θ) Detected", "Polar Abs Error (Δm, Δc)"]
        col_widths = [45, 110, 115, 115, 119]
        rows = [
            ["Line 1", "m =  0.37, c =   63.0 px", "m =  0.36, c =   70.0 px", "m =  0.38, c =   62.1 px", "|Δm| = 0.01, |Δc| =  0.9 px"],
            ["Line 2", "m = -1.13, c =  447.0 px", "m = -1.13, c =  450.0 px", "m = -1.13, c =  448.2 px", "|Δm| = 0.00, |Δc| =  1.2 px"],
            ["Line 3", "m =  2.21, c = -190.0 px", "m =  2.17, c = -180.0 px", "m =  2.14, c = -179.8 px", "|Δm| = 0.07, |Δc| = 10.2 px"],
        ]
        
        total_h = (len(rows) + 1) * row_h
        
        self.c.setFillColor(CLR_TABLE_BG)
        self.c.rect(LEFT_M, self.to_canvas_y(y_top + row_h), CONTENT_W, row_h, fill=1, stroke=0)
        
        self.c.setStrokeColor(CLR_TABLE_BORDER)
        self.c.setLineWidth(0.5)
        self.c.rect(LEFT_M, self.to_canvas_y(y_top + total_h), CONTENT_W, total_h, fill=0, stroke=1)
        
        for i in range(1, len(rows) + 1):
            self.c.line(LEFT_M, self.to_canvas_y(y_top + i * row_h), LEFT_M + CONTENT_W, self.to_canvas_y(y_top + i * row_h))
            
        x_acc = LEFT_M
        for w in col_widths[:-1]:
            x_acc += w
            self.c.line(x_acc, self.to_canvas_y(y_top), x_acc, self.to_canvas_y(y_top + total_h))
            
        self.c.setFont("Helvetica-Bold", 6.8)
        self.c.setFillColor(CLR_HEADING)
        x_cur = LEFT_M
        for text, w in zip(headers, col_widths):
            self.c.drawString(x_cur + 4, self.to_canvas_y(y_top + 7.5), text)
            x_cur += w
            
        self.c.setFont("Courier", 6.5)
        self.c.setFillColor(CLR_BODY)
        for r_idx, r_data in enumerate(rows):
            r_y = y_top + (r_idx + 1) * row_h
            x_cur = LEFT_M
            for c_idx, (text, w) in enumerate(zip(r_data, col_widths)):
                if c_idx == 0:
                    self.c.setFont("Helvetica-Bold", 6.5)
                else:
                    self.c.setFont("Courier", 6.2)
                self.c.drawString(x_cur + 4, self.to_canvas_y(r_y + 7.2), text)
                x_cur += w
                
        return y_top + total_h

    def build_report(self):
        self.draw_header()
        
        y = 44.0
        # Title
        self.c.setFont("Helvetica-Bold", 13.5)
        self.c.setFillColor(CLR_TITLE)
        self.c.drawString(LEFT_M, self.to_canvas_y(y + 11.0), "Experiment 8")
        y += 15.0
        
        # Subtitle
        self.c.setFont("Helvetica", 8.2)
        self.c.setFillColor(CLR_SUBTITLE)
        self.c.drawString(LEFT_M, self.to_canvas_y(y + 7.0), "Line Detection via Hough Transformation: Cartesian (m, c) vs. Polar (r, θ) Parameter Spaces")
        y += 13.0
        
        # Section 1: Ground Truth Lines, Random Sampling & Accumulator Grid Discretization
        self.c.setFont("Helvetica-Bold", 8.8)
        self.c.setFillColor(CLR_HEADING)
        self.c.drawString(LEFT_M, self.to_canvas_y(y + 7.5), "1. Ground Truth Setup, Intensity-Weighted Sampling & Accumulator Grids")
        y += 10.0
        
        code1 = [
            "rng = np.random.default_rng(0); H = W = 500",
            "true_lines = [(0.37, 63), (-1.13, 447), (2.21, -190)]  # (m, c) ground-truth parameters",
            "img = np.zeros((H, W), dtype=np.uint8)",
            "for m, c in true_lines: cv2.line(img, (0, round(c)), (W - 1, round(m * (W - 1) + c)), 255, 1)",
            "# Sample 20% pixels at random; weight votes by normalized intensity w in [0, 1]",
            "n = int(0.20 * H * W); k = rng.choice(H * W, n, replace=False); x, y = k % W, k // W; w = img[y, x] / 255.0",
            "# Parameter grids: Cartesian dm matches dc / W; Polar covers [-diag, diag] x [0, 180 deg]",
            "dc = 5; m_vals = np.arange(-5, 5.001, dc / W); c_min, c_max = -2500, 3000; n_c = (c_max - c_min) // dc + 1",
            "diag = int(np.ceil(np.hypot(H, W))); thetas = np.deg2rad(np.arange(0, 180, 0.5)); r_vals = np.arange(-diag, diag + 1)",
        ]
        y = self.draw_code_box(y, code1, line_height=7.2, font_size=6.0)
        y += 9.0
        
        # Section 2: Hough Transform Accumulators, Distance Metrics & Iterative Peeling
        self.c.setFont("Helvetica-Bold", 8.8)
        self.c.setFillColor(CLR_HEADING)
        self.c.drawString(LEFT_M, self.to_canvas_y(y + 7.5), "2. Vectorized Hough Accumulators & Iterative Peeling Algorithm")
        y += 10.0
        
        code2 = [
            "def hough_mc(w):",
            "    acc = np.zeros((len(m_vals), n_c))",
            "    for i, m in enumerate(m_vals):",
            "        idx = np.round((y - m * x - c_min) / dc).astype(int); ok = (idx >= 0) & (idx < n_c)",
            "        acc[i] = np.bincount(idx[ok], weights=w[ok], minlength=n_c)",
            "    return acc",
            "",
            "def hough_rt(w):",
            "    acc = np.zeros((len(thetas), len(r_vals)))",
            "    for i, t in enumerate(thetas):",
            "        idx = np.round(x * np.cos(t) + y * np.sin(t)).astype(int) + diag; ok = (idx >= 0) & (idx < len(r_vals))",
            "        acc[i] = np.bincount(idx[ok], weights=w[ok], minlength=len(r_vals))",
            "    return acc",
            "",
            "def dist_mc(i, j): return np.abs(y - m_vals[i] * x - (c_min + j * dc)) / np.hypot(1, m_vals[i])",
            "def dist_rt(i, j): return np.abs(x * np.cos(thetas[i]) + y * np.sin(thetas[i]) - r_vals[j])",
            "",
            "def peel(hough, dist, min_votes=12, tol=8):",
            "    w_left = w.copy(); acc = hough(w_left); found = []",
            "    while True:",
            "        sm = cv2.boxFilter(acc.astype(np.float32), -1, (3, 3), normalize=False)",
            "        i, j = np.unravel_index(sm.argmax(), sm.shape)",
            "        if sm[i, j] < min_votes: break",
            "        found.append((i, j, sm[i, j])); near = dist(i, j) <= tol",
            "        if w_left[near].sum() == 0: break",
            "        w_left[near] = 0; acc = hough(w_left)  # Invalidate inliers & re-vote without pre-set line count",
            "    return acc, found",
            "",
            "acc_mc, peaks_mc = peel(hough_mc, dist_mc); acc_rt, peaks_rt = peel(hough_rt, dist_rt)",
            "est_mc = [(float(m_vals[i]), float(c_min + j * dc)) for i, j, _ in peaks_mc]",
            "est_rt = [(-np.cos(thetas[i])/np.sin(thetas[i]), r_vals[j]/np.sin(thetas[i])) if np.sin(thetas[i]) > 1e-6 else (np.nan, np.nan) for i, j, _ in peaks_rt]",
        ]
        y = self.draw_code_box(y, code2, line_height=7.0, font_size=5.8)
        y += 9.0
        
        # Section 3: Visual Dashboard Figure
        self.c.setFont("Helvetica-Bold", 8.8)
        self.c.setFillColor(CLR_HEADING)
        self.c.drawString(LEFT_M, self.to_canvas_y(y + 7.5), "3. Experimental Visualizations: Image-Space Detections & Parameter Duals")
        y += 10.0
        
        img_w = 504.0
        img_h = 188.0
        y = self.draw_image_with_caption(y, "Experiment-8/exp8_dashboard_2row.png", img_w, img_h,
            "Figure 1: (a) Ground-truth lines, (b) 20% random sample, (c) Reconstructed lines, (d) Cartesian (m,c) line intersections, (e) Polar (r,θ) sinusoidal crossings.")
        y += 9.0
        
        # Section 4: Quantitative Table
        self.c.setFont("Helvetica-Bold", 8.8)
        self.c.setFillColor(CLR_HEADING)
        self.c.drawString(LEFT_M, self.to_canvas_y(y + 7.5), "4. Quantitative Benchmark: Ground Truth vs. Recovered Parameters")
        y += 10.0
        
        y = self.draw_table(y)
        
        print(f"Report completed: y_top = {y:.1f} pt (Remaining bottom margin: {PAGE_H - y:.1f} pt)")
        self.c.showPage()
        self.c.save()

if __name__ == "__main__":
    builder = SinglePageReportBuilder(PDF_FILENAME)
    builder.build_report()
    print(f"Generated {PDF_FILENAME} successfully!")
