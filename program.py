import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PolygonClipperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Polygon Clipper")

        self.create_widgets()
    
    def create_widgets(self):
        self.poly_label = tk.Label(self.root, text="Координаты вершин многоугольника (через запятую):")
        self.poly_label.pack()
        
        self.poly_entry = tk.Entry(self.root, width=50)
        self.poly_entry.pack()
        self.poly_entry.insert(0, "50,100,450,450,200,1000")

        self.clip_label = tk.Label(self.root, text="Координаты вершин окна (через запятую):")
        self.clip_label.pack()
        
        self.clip_entry = tk.Entry(self.root, width=50)
        self.clip_entry.pack()
        self.clip_entry.insert(0, "100,200,600,50,700,600,90,600")
        
        self.clip_button = tk.Button(self.root, text="Отсечение", command=self.clip_polygon)
        self.clip_button.pack()

        self.save_button = tk.Button(self.root, text="Сохранить", command=self.save_image)
        self.save_button.pack()

        self.canvas_frame = tk.Frame(self.root, width=800, height=800, bg='black')
        self.canvas_frame.pack()
    
    def clip_polygon(self):
        poly_coords = list(map(int, self.poly_entry.get().split(',')))
        clip_coords = list(map(int, self.clip_entry.get().split(',')))

        polygon = np.array(poly_coords).reshape(-1, 2)
        clipping_window = np.array(clip_coords).reshape(-1, 2)
        
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_xlim(0, 800)
        ax.set_ylim(0, 800)
        ax.set_facecolor('black')

        # Рисуем окно отсечения (белый четырехугольник)
        clip_path = Polygon(clipping_window, closed=True, fill=True, edgecolor='white', facecolor='white')
        ax.add_patch(clip_path)

        # Отсекаем многоугольник по окну отсечения
        clipped_polygon = self.sutherland_hodgman(polygon, clipping_window)
        if clipped_polygon.size > 0:  # Проверяем, что результат не пустой
            poly_patch = Polygon(clipped_polygon, closed=True, color='red')
            ax.add_patch(poly_patch)

        self.canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

    def sutherland_hodgman(self, subjectPolygon, clipPolygon):
        def inside(p, cp1, cp2):
            return (cp2[0] - cp1[0]) * (p[1] - cp1[1]) > (cp2[1] - cp1[1]) * (p[0] - cp1[0])
        
        def intersection(cp1, cp2, s, e):
            dc = [cp1[0] - cp2[0], cp1[1] - cp2[1]]
            dp = [s[0] - e[0], s[1] - e[1]]
            n1 = cp1[0] * cp2[1] - cp1[1] * cp2[0]
            n2 = s[0] * e[1] - s[1] * e[0]
            n3 = 1.0 / (dc[0] * dp[1] - dc[1] * dp[0])
            return [(n1 * dp[0] - n2 * dc[0]) * n3, (n1 * dp[1] - n2 * dc[1]) * n3]
        
        outputList = subjectPolygon
        cp1 = clipPolygon[-1]
        
        for cp2 in clipPolygon:
            inputList = outputList
            outputList = []
            if len(inputList) == 0:
                break
            s = inputList[-1]
            
            for e in inputList:
                if inside(e, cp1, cp2):
                    if not inside(s, cp1, cp2):
                        outputList.append(intersection(cp1, cp2, s, e))
                    outputList.append(e)
                elif inside(s, cp1, cp2):
                    outputList.append(intersection(cp1, cp2, s, e))
                s = e
            cp1 = cp2
        return np.array(outputList)

    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            self.canvas.print_png(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = PolygonClipperApp(root)
    root.mainloop()
