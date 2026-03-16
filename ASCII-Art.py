import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont, ImageGrab
from tkinter import filedialog, messagebox
import tempfile
import os

class AsciiConverter(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ASCII Art bykleorr")
        self.geometry("1100x850")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.chars = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

        # Панель управления
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        self.btn_open = ctk.CTkButton(self.top_frame, text="Выбрать картинку", command=self.open_image)
        self.btn_open.pack(side="left", padx=10)

        self.width_slider = ctk.CTkSlider(self.top_frame, from_=50, to=250, command=self.update_ascii)
        self.width_slider.set(100)
        self.width_slider.pack(side="left", padx=10)

        self.btn_copy = ctk.CTkButton(self.top_frame, text="Скопировать для Telegram/Discord", fg_color="#b85c00", hover_color="#8f4700", command=self.copy_to_clipboard)
        self.btn_copy.pack(side="left", padx=5)

        self.btn_save_png = ctk.CTkButton(self.top_frame, text="Сохранить .PNG", fg_color="darkgreen", command=self.save_as_png)
        self.btn_save_png.pack(side="left", padx=5)

        self.text_area = ctk.CTkTextbox(self, font=("Consolas", 7), wrap="none")
        self.text_area.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        self.current_path = None
        self.ascii_result = ""

        # --- ИСПРАВЛЕННЫЙ БИНДИНГ ---
        self.bind("<Control-v>", self.paste_from_clipboard)
        self.text_area.bind("<Control-v>", self.paste_from_clipboard)
        self.bind("<Control-V>", self.paste_from_clipboard) # На всякий случай для CapsLock
        self.text_area.bind("<Control-V>", self.paste_from_clipboard)

    def open_image(self):
        self.current_path = filedialog.askopenfilename(filetypes=[("Изображения", "*.jpg *.png *.jpeg")])
        if self.current_path:
            self.update_ascii()

    # --- ИСПРАВЛЕННАЯ ФУНКЦИЯ ВСТАВКИ ---
    def paste_from_clipboard(self, event=None):
        try:
            img = ImageGrab.grabclipboard()
            
            # Случай 1: В буфере сама картинка (скриншот)
            if isinstance(img, Image.Image):
                temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                img.save(temp.name)
                self.current_path = temp.name
                self.update_ascii()
                return "break" # Блокируем стандартную вставку текста
                
            # Случай 2: В буфере скопированный файл
            elif isinstance(img, list) or isinstance(img, tuple):
                if len(img) > 0 and isinstance(img[0], str):
                    if img[0].lower().endswith(('.png', '.jpg', '.jpeg')):
                        self.current_path = img[0]
                        self.update_ascii()
                        return "break"
        except:
            pass 
        return None

    def update_ascii(self, *args):
        if self.current_path:
            width = int(self.width_slider.get())
            self.ascii_result = self.convert_to_ascii(self.current_path, width)
            self.text_area.delete("1.0", "end")
            self.text_area.insert("1.0", self.ascii_result)

    def convert_to_ascii(self, path, width):
        img = Image.open(path)
        aspect_ratio = img.height / img.width
        new_height = int(aspect_ratio * width * 0.55)
        img = img.resize((width, new_height)).convert("L")
        
        pixels = img.getdata()
        new_pixels = [self.chars[pixel // 25] for pixel in pixels]
        
        lines = []
        for i in range(0, len(new_pixels), width):
            lines.append("".join(new_pixels[i:i+width]))
        return "\n".join(lines)

    def copy_to_clipboard(self):
        if not self.ascii_result:
            return
        formatted_text = f"```text\n{self.ascii_result}\n```"
        self.clipboard_clear()
        self.clipboard_append(formatted_text)
        self.update() 
        messagebox.showinfo("Скопировано", "Текст скопирован для Discord/Telegram! максимка не поддерживается xd")

    def save_as_png(self):
        if not self.ascii_result:
            return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG file", "*.png")])
        if path:
            lines = self.ascii_result.split("\n")
            font_size = 24 
            try:
                font = ImageFont.truetype("consola.ttf", font_size)
            except:
                font = ImageFont.load_default()

            left, top, right, bottom = font.getbbox("A")
            char_width = right - left
            char_height = int(char_width / 0.55) 
            
            img_w = char_width * len(lines[0]) + 40 
            img_h = char_height * len(lines) + 40
            
            output_img = Image.new("RGB", (img_w, img_h), color="#2b2b2b")
            draw = ImageDraw.Draw(output_img)
            
            for i, line in enumerate(lines):
                draw.text((20, 20 + i * char_height), line, fill="#dce4ee", font=font)
            
            output_img.save(path)
            messagebox.showinfo("Готово", "PNG сохранен!")

if __name__ == "__main__":
    app = AsciiConverter()
    app.mainloop()
