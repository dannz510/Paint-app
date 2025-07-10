import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, simpledialog, ttk
from PIL import Image, ImageDraw, ImageTk, ImageGrab
import io
import os
import math
import json

class PaintApp:
    def __init__(self, master):
        self.master = master
        master.title("Modern Paint Studio")
        master.geometry("1280x900")
        master.resizable(True, True)  # Allow resizing
        
        # --- Drawing Variables ---
        self.current_color = "black"
        self.fill_color = None
        self.brush_size = 5
        self.brush_type = "round"
        self.last_x, self.last_y = None, None
        self.start_x, self.start_y = None, None
        self.current_tool = "brush"
        self.current_shape = None
        self.active_item = None
        self.zoom_level = 1.0
        self.history = []
        self.redo_stack = []
        self.clipboard = None
        self.font_name = "Inter"
        self.font_size = 14
        self.show_grid = False
        self.show_ruler = False
        self.canvas_modified = False

        # --- Modern Theme with Enhanced Styles ---
        self.current_theme = "modern_dark"
        self.themes = {
            "modern_dark": {
                "bg": "#1e1e2f",
                "control_frame_bg": "#2a2a3d",
                "canvas_bg": "#25253a",
                "text_color": "#e0e0ff",
                "button_bg": "#3a3a52",
                "button_fg": "#e0e0ff",
                "button_active_bg": "#4a4a6a",
                "button_active_fg": "#ffffff",
                "label_bg": "#2a2a3d",
                "slider_bg": "#2a2a3d",
                "slider_trough": "#4a4a6a",
                "status_bar_bg": "#2a2a3d",
                "status_bar_fg": "#e0e0ff",
                "active_tool_bg": "#5a5a8a",
                "active_tool_fg": "#ffffff",
                "border_color": "#1a1a2a",
                "shadow": "#0a0a1a"
            }
        }
        
        # --- Load Settings ---
        self.settings = {
            "theme": "modern_dark",
            "default_brush_size": 5,
            "canvas_bg": "#25253a",
            "show_grid": False,
            "show_ruler": False
        }
        self.load_settings()
        
        # --- Load Icons ---
        self.icons = {}
        self._load_icons()
        if self.icons.get("app_icon"):
            self.master.iconphoto(True, self.icons["app_icon"])

        # Canvas dimensions
        self.canvas_width = 960
        self.canvas_height = 720

        # --- UI Elements with Scrollbar ---
        self.main_frame = ttk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.control_frame = ttk.Frame(self.main_frame, relief="flat", padding=10)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.canvas_frame = ttk.Frame(self.main_frame)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.status_bar = tk.Label(self.main_frame, text="Ready to create!", bd=1, relief=tk.FLAT, bg=self.themes[self.current_theme]["status_bar_bg"], fg=self.themes[self.current_theme]["status_bar_fg"], anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.create_widgets()
        self.bind_events()
        
        # Bind the window close event
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Apply initial theme and settings
        self.apply_theme(self.current_theme)
        self.size_slider.set(self.brush_size)
        self.fill_var.set(self.fill_color is not None)
        self.toggle_fill()
        self.grid_var.set(self.show_grid)
        self.ruler_var.set(self.show_ruler)
        self.update_gridlines()
        self.update_rulers()

    def load_settings(self):
        try:
            if os.path.exists("paint_settings.json"):
                with open("paint_settings.json", "r") as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
                if self.settings.get("theme") == "dark":
                    self.settings["theme"] = "modern_dark"
            self.current_theme = self.settings.get("theme", "modern_dark")
            self.brush_size = self.settings.get("default_brush_size", 5)
            self.show_grid = self.settings.get("show_grid", False)
            self.show_ruler = self.settings.get("show_ruler", False)
            self.themes["modern_dark"]["canvas_bg"] = self.settings.get("canvas_bg", "#25253a")
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.current_theme = "modern_dark"

    def save_settings(self):
        try:
            self.settings["theme"] = self.current_theme
            self.settings["default_brush_size"] = self.brush_size
            self.settings["canvas_bg"] = self.themes[self.current_theme]["canvas_bg"]
            self.settings["show_grid"] = self.show_grid
            self.settings["show_ruler"] = self.show_ruler
            with open("paint_settings.json", "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def apply_theme(self, theme_name):
        theme = self.themes[theme_name]
        self.master.configure(bg=theme["bg"])
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=theme["control_frame_bg"], relief="flat", borderwidth=2)
        style.configure("TLabelFrame", background=theme["label_bg"], foreground=theme["text_color"], font=("Inter", 10, "bold"), relief="raised", borderwidth=2)
        style.configure("TLabel", background=theme["label_bg"], foreground=theme["text_color"])
        style.configure("TScale", background=theme["slider_bg"], troughcolor=theme["slider_trough"], foreground=theme["text_color"])
        style.configure("TButton", background=theme["button_bg"], foreground=theme["button_fg"], relief="raised", borderwidth=2, padding=6)
        style.map("TButton", background=[("active", theme["button_active_bg"])], foreground=[("active", theme["button_active_fg"])])
        style.configure("TRadiobutton", background=theme["label_bg"], foreground=theme["text_color"], indicatorcolor=theme["active_tool_bg"], relief="flat")
        style.map("TRadiobutton", background=[("active", theme["button_active_bg"])], foreground=[("active", theme["button_active_fg"])])
        style.configure("TCheckbutton", background=theme["label_bg"], foreground=theme["text_color"], indicatorcolor=theme["active_tool_bg"], relief="flat")
        style.map("TCheckbutton", background=[("active", theme["button_active_bg"])], foreground=[("active", theme["button_active_fg"])])
        style.configure("TCombobox", fieldbackground=theme["control_frame_bg"], background=theme["button_bg"], foreground=theme["text_color"], selectbackground=theme["button_active_bg"], selectforeground=theme["button_active_fg"], arrowcolor=theme["text_color"])
        style.map("TCombobox", fieldbackground=[("readonly", theme["control_frame_bg"])], background=[("readonly", theme["button_bg"])])

        if hasattr(self, 'control_frame'):
            self.canvas.configure(bg=theme["canvas_bg"])
            self.status_bar.configure(bg=theme["status_bar_bg"], fg=theme["status_bar_fg"])
            self.ruler_top.configure(bg=theme["control_frame_bg"])
            self.ruler_left.configure(bg=theme["control_frame_bg"])
            self.update_active_tool_button()

        self.current_theme = theme_name
        self.settings["theme"] = theme_name
        self.save_settings()

    def create_widgets(self):
        self.control_frame = ttk.Frame(self.main_frame, relief="flat", padding=10)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        # --- Tabs with Modern Layout ---
        notebook = ttk.Notebook(self.control_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # File Tab (Horizontal Button Layout)
        file_frame = ttk.LabelFrame(notebook, text="File", padding=5)
        notebook.add(file_frame, text="File")
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(fill=tk.X)
        ttk.Button(button_frame, text="New", command=self.clear_canvas, image=self.icons.get("clear_icon"), compound=tk.LEFT).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(button_frame, text="Open", command=self.import_image, image=self.icons.get("image_icon"), compound=tk.LEFT).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(button_frame, text="Save", command=self.save_canvas, image=self.icons.get("save_icon"), compound=tk.LEFT).pack(side=tk.LEFT, padx=2, pady=2)

        # Edit Tab
        edit_frame = ttk.LabelFrame(notebook, text="Edit", padding=5)
        notebook.add(edit_frame, text="Edit")
        ttk.Button(edit_frame, text="Undo", command=self.undo).pack(pady=5)
        ttk.Button(edit_frame, text="Redo", command=self.redo).pack(pady=5)

        # Tools Tab
        tools_frame = ttk.LabelFrame(notebook, text="Tools", padding=5)
        notebook.add(tools_frame, text="Tools")
        self.tool_var = tk.StringVar(value=self.current_tool)
        self.tool_buttons = {}
        tool_definitions = [
            ("brush", "Brush", self.icons.get("brush_icon")),
            ("eraser", "Eraser", self.icons.get("eraser_icon")),
            ("pencil", "Pencil", self.icons.get("pencil_icon")),
            ("fill", "Fill", self.icons.get("fill_icon")),
            ("text", "Text", self.icons.get("text_icon")),
            ("pipette", "Color Picker", self.icons.get("pipette_icon")),
            ("zoom", "Zoom", self.icons.get("zoom_icon")),
        ]
        for tool_name, text, icon in tool_definitions:
            btn = ttk.Radiobutton(tools_frame, text=text, image=icon, compound=tk.TOP,
                               variable=self.tool_var, value=tool_name,
                               command=lambda t=tool_name: self.select_tool(t))
            btn.pack(side=tk.LEFT, padx=5, pady=5)
            self.tool_buttons[tool_name] = btn

        # Brush Options Tab
        brush_frame = ttk.LabelFrame(notebook, text="Brush", padding=5)
        notebook.add(brush_frame, text="Brush")
        self.size_slider = ttk.Scale(brush_frame, from_=1, to=50, orient=tk.HORIZONTAL,
                                  command=self.change_brush_size, length=200)
        self.size_slider.set(self.brush_size)
        self.size_slider.pack(pady=5)
        self.brush_type_var = tk.StringVar(value="round")
        brush_types = ["round", "square", "airbrush"]
        brush_type_menu = ttk.Combobox(brush_frame, textvariable=self.brush_type_var, values=brush_types,
                                     state="readonly", width=10)
        brush_type_menu.pack(pady=5)
        brush_type_menu.bind("<<ComboboxSelected>>", lambda e: self.change_brush_type())

        # Shapes Tab
        shapes_frame = ttk.LabelFrame(notebook, text="Shapes", padding=5)
        notebook.add(shapes_frame, text="Shapes")
        self.shape_var = tk.StringVar(value="")
        self.shape_buttons = {}
        shape_definitions = [
            ("line", "Line", self.icons.get("line_shape_icon")),
            ("rectangle", "Rect", self.icons.get("rectangle_shape_icon")),
            ("circle", "Circle", self.icons.get("circle_shape_icon")),
            ("triangle", "Tri", self.icons.get("triangle_shape_icon")),
            ("star", "Star", self.icons.get("star_shape_icon")),
        ]
        for shape_name, text, icon in shape_definitions:
            btn = ttk.Radiobutton(shapes_frame, text=text, image=icon, compound=tk.TOP,
                               variable=self.shape_var, value=shape_name,
                               command=lambda s=shape_name: self.select_shape(s))
            btn.pack(side=tk.LEFT, padx=5, pady=5)
            self.shape_buttons[shape_name] = btn
        self.fill_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(shapes_frame, text="Fill", variable=self.fill_var,
                      command=self.toggle_fill).pack(pady=5)

        # Colors Tab
        colors_frame = ttk.LabelFrame(notebook, text="Colors", padding=5)
        notebook.add(colors_frame, text="Colors")
        self.current_color_display = tk.Label(colors_frame, bg=self.current_color, width=4, height=2, relief="ridge", bd=2)
        self.current_color_display.pack(pady=5)
        ttk.Button(colors_frame, text="Pick Color", command=self.choose_color,
                   image=self.icons.get("color_icon"), compound=tk.TOP).pack(pady=5)
        palette_frame = ttk.Frame(colors_frame)
        palette_frame.pack(pady=5)
        self.palette_colors = [
            "#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF",
            "#800000", "#008000", "#000080", "#808000", "#800080", "#008080", "#808080", "#C0C0C0"
        ]
        for i, color_hex in enumerate(self.palette_colors):
            btn = tk.Button(palette_frame, bg=color_hex, width=2, height=1,
                          command=lambda c=color_hex: self.set_current_color(c),
                          relief="flat", bd=1, activebackground=color_hex)
            btn.grid(row=i // 8, column=i % 8, padx=2, pady=2)

        # Image Tab
        image_frame = ttk.LabelFrame(notebook, text="Image", padding=5)
        notebook.add(image_frame, text="Image")
        ttk.Button(image_frame, text="Import", command=self.import_image,
                   image=self.icons.get("image_icon"), compound=tk.TOP).pack(pady=5)
        rotate_menu_btn = ttk.Menubutton(image_frame, text="Transform")
        rotate_menu_btn.menu = tk.Menu(rotate_menu_btn, tearoff=0)
        rotate_menu_btn["menu"] = rotate_menu_btn.menu
        rotate_menu_btn.menu.add_command(label="Rotate 90°", command=lambda: self.rotate_canvas(90))
        rotate_menu_btn.menu.add_command(label="Rotate 180°", command=lambda: self.rotate_canvas(180))
        rotate_menu_btn.menu.add_command(label="Rotate 270°", command=lambda: self.rotate_canvas(270))
        rotate_menu_btn.menu.add_separator()
        rotate_menu_btn.menu.add_command(label="Flip Horizontal", command=lambda: self.flip_canvas("horizontal"))
        rotate_menu_btn.menu.add_command(label="Flip Vertical", command=lambda: self.flip_canvas("vertical"))
        rotate_menu_btn.pack(pady=5)

        # View Tab (Updated Zoom Levels)
        view_frame = ttk.LabelFrame(notebook, text="View", padding=5)
        notebook.add(view_frame, text="View")
        zoom_levels = ["0%", "25%", "50%", "100%", "200%", "300%", "400%", "500%"]
        self.zoom_var = tk.StringVar(value="100%")
        zoom_menu = ttk.Combobox(view_frame, textvariable=self.zoom_var, values=zoom_levels,
                               state="readonly", width=8)
        zoom_menu.pack(pady=5)
        zoom_menu.bind("<<ComboboxSelected>>", lambda e: self.set_zoom_level())
        self.grid_var = tk.BooleanVar(value=self.show_grid)
        ttk.Checkbutton(view_frame, text="Gridlines", variable=self.grid_var,
                      command=self.toggle_gridlines).pack(pady=5)
        self.ruler_var = tk.BooleanVar(value=self.show_ruler)
        ttk.Checkbutton(view_frame, text="Rulers", variable=self.ruler_var,
                      command=self.toggle_rulers).pack(pady=5)
        ttk.Button(view_frame, text="Fit to Screen", command=self.fit_to_screen).pack(pady=5)

        # Settings Tab
        settings_frame = ttk.LabelFrame(notebook, text="Settings", padding=5)
        notebook.add(settings_frame, text="Settings")
        ttk.Button(settings_frame, text="Canvas Size", command=self.resize_canvas).pack(pady=5)
        ttk.Button(settings_frame, text="Canvas Color", command=self.set_canvas_bg).pack(pady=5)

        # Rulers
        self.ruler_top = tk.Canvas(self.main_frame, height=20, bg=self.themes[self.current_theme]["control_frame_bg"], highlightthickness=0)
        self.ruler_left = tk.Canvas(self.main_frame, width=20, bg=self.themes[self.current_theme]["control_frame_bg"], highlightthickness=0)
        self.ruler_top.pack(side=tk.TOP, fill=tk.X)
        self.ruler_left.pack(side=tk.LEFT, fill=tk.Y)

        # Drawing Canvas with Scrollbar
        self.canvas = tk.Canvas(self.canvas_frame, width=self.canvas_width, height=self.canvas_height, bd=2, relief="sunken", highlightbackground=self.themes[self.current_theme]["border_color"], highlightthickness=2, yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.configure(bg=self.themes[self.current_theme]["canvas_bg"])
        self.scrollbar.config(command=self.canvas.yview)

    def bind_events(self):
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Button-2>", self.on_middle_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Motion>", self.update_status_bar)
        self.canvas.bind("<MouseWheel>", self.zoom_wheel)
        self.master.bind("<Control-MouseWheel>", self.zoom_wheel)

    def _load_icons(self):
        icon_names = ["app_icon", "color_icon", "brush_icon", "eraser_icon", "clear_icon", "save_icon",
                      "image_icon", "pencil_icon", "fill_icon", "text_icon", "pipette_icon", "zoom_icon",
                      "line_shape_icon", "rectangle_shape_icon", "circle_shape_icon", "triangle_shape_icon",
                      "star_shape_icon"]
        icons_dir = "icons"
        
        if not os.path.exists(icons_dir):
            messagebox.showerror("Icon Error", f"The 'icons' directory was not found at '{icons_dir}'. Please run 'generate_icons.py' first.")
            return

        for name in icon_names:
            path = os.path.join(icons_dir, f"{name}.png")
            try:
                img = Image.open(path)
                if name != "app_icon":
                    img = img.resize((32, 32), Image.Resampling.LANCZOS)
                self.icons[name] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Error loading icon {name}: {e}")
                self.icons[name] = None
                messagebox.showwarning("Icon Missing", f"Could not load icon: {name}.png. Please ensure 'generate_icons.py' ran successfully.")

    def select_tool(self, tool_name):
        self.current_tool = tool_name
        self.current_shape = None
        self.shape_var.set("")
        self.status_bar_message(f"Tool selected: {tool_name.replace('_', ' ').title()}")
        self.update_active_tool_button()

    def select_shape(self, shape_name):
        self.current_tool = "shape"
        self.current_shape = shape_name
        self.tool_var.set("shape")
        self.status_bar_message(f"Shape selected: {shape_name.replace('_', ' ').title()}")
        self.update_active_tool_button()

    def update_active_tool_button(self):
        theme = self.themes[self.current_theme]
        for tool_name, btn in self.tool_buttons.items():
            btn.config(style="TRadiobutton")
        if self.current_tool in self.tool_buttons:
            self.tool_buttons[self.current_tool].config(style="Active.TRadiobutton")
        for shape_name, btn in self.shape_buttons.items():
            btn.config(style="TRadiobutton")
        if self.current_tool == "shape" and self.current_shape in self.shape_buttons:
            self.shape_buttons[self.current_shape].config(style="Active.TRadiobutton")
        style = ttk.Style()
        style.configure("Active.TRadiobutton", background=theme["active_tool_bg"], foreground=theme["active_tool_fg"])

    def set_current_color(self, color_hex):
        self.current_color = color_hex
        self.current_color_display.config(bg=self.current_color)
        if self.fill_var.get():
            self.fill_color = self.current_color
        self.status_bar_message(f"Color set to: {self.current_color}")
        self.canvas_modified = True  # Mark as modified when color changes

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Choose Color", initialcolor=self.current_color)
        if color_code[1]:
            self.set_current_color(color_code[1])

    def change_brush_size(self, new_size):
        self.brush_size = int(float(new_size))
        self.settings["default_brush_size"] = self.brush_size
        self.save_settings()
        self.status_bar_message(f"Brush size: {self.brush_size}")
        self.canvas_modified = True  # Mark as modified when brush size changes

    def change_brush_type(self):
        self.brush_type = self.brush_type_var.get()
        self.status_bar_message(f"Brush type: {self.brush_type}")
        self.canvas_modified = True  # Mark as modified when brush type changes

    def toggle_fill(self):
        if self.fill_var.get():
            self.fill_color = self.current_color
        else:
            self.fill_color = None
        self.status_bar_message(f"Fill {'enabled' if self.fill_var.get() else 'disabled'}")
        self.canvas_modified = True  # Mark as modified when fill state changes

    def clear_canvas(self):
        if messagebox.askyesno("Clear Canvas", "Are you sure you want to clear the canvas?"):
            self.history.append(self.get_canvas_image_data())
            self.redo_stack.clear()
            self.canvas.delete("all")
            self.canvas_modified = True
            self.status_bar_message("Canvas cleared.")
            self.set_current_color("black")
            self.size_slider.set(5)
            self.canvas.configure(bg=self.themes[self.current_theme]["canvas_bg"])

    def get_canvas_image_data(self):
        self.master.update_idletasks()
        if self.canvas_width <= 0 or self.canvas_height <= 0:
            return Image.new("RGB", (self.canvas_width or 800, self.canvas_height or 600), self.canvas.cget("bg"))

        x = self.canvas.winfo_rootx()
        y = self.canvas.winfo_rooty()
        try:
            img = ImageGrab.grab(bbox=(x, y, x + self.canvas_width, y + self.canvas_height))
            return img.convert("RGB")
        except Exception as e:
            print(f"Warning: Screenshot failed: {e}. Using blank image.")
            return Image.new("RGB", (self.canvas_width, self.canvas_height), self.canvas.cget("bg"))

    def save_canvas(self):
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")], initialfile="my_artwork.png")
            if not file_path:
                self.status_bar_message("Save cancelled.")
                return
            img = self.get_canvas_image_data()
            if file_path.lower().endswith(('.jpg', '.jpeg')):
                img = img.convert('RGB')
            img.save(file_path)
            self.status_bar_message(f"Saved to {os.path.basename(file_path)}")
            self.canvas_modified = False  # Reset modified flag after save
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving: {e}")

    def import_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"), ("All files", "*.*")])
        if not file_path:
            self.status_bar_message("Import cancelled.")
            return
        try:
            self.history.append(self.get_canvas_image_data())
            self.redo_stack.clear()
            self.canvas_modified = True
            pil_image = Image.open(file_path)
            pil_image.thumbnail((self.canvas_width * 0.8, self.canvas_height * 0.8), Image.Resampling.LANCZOS)
            self.imported_tk_image = ImageTk.PhotoImage(pil_image)
            x = (self.canvas_width - pil_image.width) / 2
            y = (self.canvas_height - pil_image.height) / 2
            if hasattr(self, '_current_imported_canvas_item'):
                self.canvas.delete(self._current_imported_canvas_item)
            self._current_imported_canvas_item = self.canvas.create_image(x, y, image=self.imported_tk_image, anchor=tk.NW, tags="imported_image")
            self.status_bar_message(f"Imported {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import: {e}")

    def undo(self):
        if self.history:
            self.redo_stack.append(self.get_canvas_image_data())
            last_state_img = self.history.pop()
            self.canvas.delete("all")
            self._display_image_on_canvas(last_state_img)
            self.canvas_modified = True
            self.status_bar_message("Undo performed.")
        else:
            self.status_bar_message("Nothing to undo.")

    def redo(self):
        if self.redo_stack:
            self.history.append(self.get_canvas_image_data())
            last_state_img = self.redo_stack.pop()
            self.canvas.delete("all")
            self._display_image_on_canvas(last_state_img)
            self.canvas_modified = True
            self.status_bar_message("Redo performed.")
        else:
            self.status_bar_message("Nothing to redo.")

    def _display_image_on_canvas(self, pil_image):
        self.canvas.delete("all")
        self.canvas.config(width=self.canvas_width, height=self.canvas_height)
        self.canvas_photo_image = ImageTk.PhotoImage(pil_image.resize((self.canvas_width, self.canvas_height), Image.Resampling.LANCZOS))
        self.canvas.create_image(0, 0, image=self.canvas_photo_image, anchor=tk.NW)
        self.update_gridlines()
        self.update_rulers()

    def rotate_canvas(self, angle):
        self.history.append(self.get_canvas_image_data())
        self.redo_stack.clear()
        self.canvas_modified = True
        current_img = self.get_canvas_image_data()
        rotated_img = current_img.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
        self.canvas.delete("all")
        self._display_image_on_canvas(rotated_img)
        self.status_bar_message(f"Rotated {angle}°")

    def flip_canvas(self, direction):
        self.history.append(self.get_canvas_image_data())
        self.redo_stack.clear()
        self.canvas_modified = True
        current_img = self.get_canvas_image_data()
        flipped_img = current_img.transpose(Image.FLIP_LEFT_RIGHT if direction == "horizontal" else Image.FLIP_TOP_BOTTOM)
        self.canvas.delete("all")
        self._display_image_on_canvas(flipped_img)
        self.status_bar_message(f"Flipped {direction}")

    def resize_canvas(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Resize Canvas")
        dialog.transient(self.master)
        dialog.grab_set()
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="Width:").grid(row=0, column=0, padx=5, pady=5)
        width_entry = ttk.Entry(frame)
        width_entry.insert(0, str(self.canvas_width))
        width_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(frame, text="Height:").grid(row=1, column=0, padx=5, pady=5)
        height_entry = ttk.Entry(frame)
        height_entry.insert(0, str(self.canvas_height))
        height_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Resize", command=lambda: self._resize_canvas_confirm(width_entry.get(), height_entry.get(), dialog)).grid(row=2, column=0, columnspan=2, pady=10)
        dialog.wait_window(dialog)

    def _resize_canvas_confirm(self, width, height, dialog):
        try:
            new_width, new_height = int(width), int(height)
            if new_width <= 0 or new_height <= 0:
                messagebox.showerror("Error", "Invalid dimensions.")
                return
            self.history.append(self.get_canvas_image_data())
            self.redo_stack.clear()
            self.canvas_modified = True
            current_img = self.get_canvas_image_data()
            resized_img = current_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.canvas_width, self.canvas_height = new_width, new_height
            self.canvas.config(width=new_width, height=new_height)
            self._display_image_on_canvas(resized_img)
            dialog.destroy()
            self.status_bar_message(f"Resized to {new_width}x{new_height}")
        except ValueError:
            messagebox.showerror("Error", "Enter valid numbers.")

    def set_canvas_bg(self):
        color_code = colorchooser.askcolor(title="Choose Canvas Color", initialcolor=self.canvas.cget("bg"))
        if color_code[1]:
            self.themes["modern_dark"]["canvas_bg"] = color_code[1]
            self.canvas.config(bg=color_code[1])
            self.settings["canvas_bg"] = color_code[1]
            self.save_settings()
            self.canvas_modified = True
            self.status_bar_message(f"Background set to {color_code[1]}")

    def toggle_gridlines(self):
        self.show_grid = self.grid_var.get()
        self.settings["show_grid"] = self.show_grid
        self.save_settings()
        self.update_gridlines()
        self.status_bar_message(f"Gridlines {'enabled' if self.show_grid else 'disabled'}")
        self.canvas_modified = True  # Mark as modified when gridlines toggle

    def toggle_rulers(self):
        self.show_ruler = self.ruler_var.get()
        self.settings["show_ruler"] = self.show_ruler
        self.save_settings()
        self.update_rulers()
        self.status_bar_message(f"Rulers {'enabled' if self.show_ruler else 'disabled'}")
        self.canvas_modified = True  # Mark as modified when rulers toggle

    def update_gridlines(self):
        self.canvas.delete("grid")
        if self.show_grid:
            grid_spacing = 20
            for x in range(0, self.canvas_width, grid_spacing):
                self.canvas.create_line(x, 0, x, self.canvas_height, fill="#555577", dash=(2, 2), tags="grid")
            for y in range(0, self.canvas_height, grid_spacing):
                self.canvas.create_line(0, y, self.canvas_width, y, fill="#555577", dash=(2, 2), tags="grid")

    def update_rulers(self):
        self.ruler_top.delete("all")
        self.ruler_left.delete("all")
        if self.show_ruler:
            for x_coord in range(0, self.canvas_width + 50, 50):
                self.ruler_top.create_line(x_coord, 0, x_coord, 20, fill="#e0e0ff")
                self.ruler_top.create_text(x_coord + 5, 10, text=str(x_coord), anchor="w", font=("Inter", 8))
            for y_coord in range(0, self.canvas_height + 50, 50):
                self.ruler_left.create_line(0, y_coord, 20, y_coord, fill="#e0e0ff")
                self.ruler_left.create_text(10, y_coord + 5, text=str(y_coord), anchor="n", font=("Inter", 8))

    def set_zoom_level(self):
        level_str = self.zoom_var.get()
        if level_str:
            target_level = max(0.0, float(level_str.rstrip('%')) / 100)  # Allow 0% as minimum
            factor = target_level / self.zoom_level if target_level > 0 else 0.01  # Prevent division by zero
            self.apply_zoom(factor)
            self.status_bar_message(f"Zoom: {self.zoom_level*100:.0f}%")
            self.canvas_modified = True  # Mark as modified when zoom changes

    def zoom_wheel(self, event):
        if self.current_tool == "zoom" or (event.state & 0x4) or (event.state & 0x8):
            factor = 1.1 if event.delta > 0 else 1/1.1
            self.apply_zoom(factor)
            self.zoom_var.set(f"{self.zoom_level*100:.0f}%")
            self.status_bar_message(f"Zoom: {self.zoom_level*100:.0f}%")
            self.canvas_modified = True  # Mark as modified when zoom changes via wheel

    def apply_zoom(self, factor):
        center_x = self.canvas_width / 2
        center_y = self.canvas_height / 2
        self.canvas.scale("all", center_x, center_y, factor, factor)
        self.zoom_level = max(0.0, self.zoom_level * factor)  # Ensure zoom_level doesn't go negative
        self.update_gridlines()
        self.update_rulers()

    def fit_to_screen(self):
        self.master.update_idletasks()  # Ensure all widgets are rendered
        control_frame_height = self.control_frame.winfo_height() or 150
        status_bar_height = self.status_bar.winfo_height() or 20
        ruler_height = self.ruler_top.winfo_height() or 20
        ruler_width = self.ruler_left.winfo_width() or 20
        padding = 30

        new_width = max(100, self.master.winfo_width() - ruler_width - padding)
        new_height = max(100, self.master.winfo_height() - control_frame_height - status_bar_height - ruler_height - padding)

        if new_width > 0 and new_height > 0:
            self.history.append(self.get_canvas_image_data())
            self.redo_stack.clear()
            self.canvas_modified = True
            current_img = self.get_canvas_image_data()
            resized_img = current_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.canvas_width, self.canvas_height = new_width, new_height
            self.canvas.config(width=new_width, height=new_height)
            self._display_image_on_canvas(resized_img)
            self.status_bar_message(f"Fitted to screen: {new_width}x{new_height}")
        else:
            self.status_bar_message("Unable to fit to screen.")

    def on_mouse_down(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.last_x, self.last_y = event.x, event.y
        self.active_item = None
        
        if self.current_tool not in ["zoom", "pipette"]:
            self.history.append(self.get_canvas_image_data())
            self.redo_stack.clear()
            self.canvas_modified = True

        if self.current_tool == "text":
            self.create_text_input(event.x, event.y)
        elif self.current_tool == "pipette":
            self.pick_color_from_canvas(event.x, event.y)
        elif self.current_tool == "fill" and self.fill_color:
            self.fill_area(event.x, event.y)  # Ensure fill_color is set
        elif self.current_tool == "image":
            item = self.canvas.find_closest(event.x, event.y)
            if item and "imported_image" in self.canvas.gettags(item[0]):
                self.active_item = item[0]
                self.status_bar_message("Moving imported image.")
        
        self.update_status_bar(event)

    def on_mouse_drag(self, event):
        if self.last_x is None or self.last_y is None:
            return

        if self.current_tool in ["brush", "pencil", "eraser"]:
            style = tk.ROUND if self.brush_type == "round" else tk.BUTT
            width = self.brush_size if self.current_tool != "pencil" else 1
            color = self.current_color if self.current_tool != "eraser" else self.canvas.cget("bg")
            self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                  width=width, fill=color, capstyle=style, smooth=tk.TRUE)
            self.canvas_modified = True  # Mark as modified when drawing
        elif self.current_tool == "shape" and self.current_shape:
            self.canvas.delete("temp_shape_preview")
            self.canvas.delete("temp_fill_preview")
            x1, y1 = self.start_x, self.start_y
            x2, y2 = event.x, event.y
            outline_color = self.current_color
            fill_color_preview = self.fill_color if self.fill_var.get() else ""
            if self.current_shape == "line":
                self.canvas.create_line(x1, y1, x2, y2, width=self.brush_size, fill=outline_color, dash=(2, 2), tags="temp_shape_preview")
            elif self.current_shape == "rectangle":
                self.canvas.create_rectangle(x1, y1, x2, y2, outline=outline_color, width=self.brush_size, dash=(2, 2), tags="temp_shape_preview")
                if fill_color_preview:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color_preview, outline="", tags="temp_fill_preview")
            elif self.current_shape == "circle":
                self.canvas.create_oval(x1, y1, x2, y2, outline=outline_color, width=self.brush_size, dash=(2, 2), tags="temp_shape_preview")
                if fill_color_preview:
                    self.canvas.create_oval(x1, y1, x2, y2, fill=fill_color_preview, outline="", tags="temp_fill_preview")
            elif self.current_shape == "triangle":
                mid_x = (x1 + x2) / 2
                points = [x1, y2, x2, y2, mid_x, y1]
                self.canvas.create_polygon(points, outline=outline_color, width=self.brush_size, dash=(2, 2), tags="temp_shape_preview")
                if fill_color_preview:
                    self.canvas.create_polygon(points, fill=fill_color_preview, outline="", tags="temp_fill_preview")
            elif self.current_shape == "star":
                points = self.calculate_star_points(x1, y1, x2, y2)
                self.canvas.create_polygon(points, outline=outline_color, width=self.brush_size, dash=(2, 2), tags="temp_shape_preview")
                if fill_color_preview:
                    self.canvas.create_polygon(points, fill=fill_color_preview, outline="", tags="temp_fill_preview")
        elif self.current_tool == "image" and self.active_item:
            dx = event.x - self.last_x
            dy = event.y - self.last_y
            self.canvas.move(self.active_item, dx, dy)
            self.canvas_modified = True  # Mark as modified when moving image

        self.last_x, self.last_y = event.x, event.y
        self.update_status_bar(event)

    def on_mouse_up(self, event):
        self.canvas.delete("temp_shape_preview")
        self.canvas.delete("temp_fill_preview")
        if self.current_tool == "shape" and self.current_shape:
            x1, y1 = self.start_x, self.start_y
            x2, y2 = event.x, event.y
            outline_color = self.current_color
            fill_color_final = self.fill_color if self.fill_var.get() else ""
            if self.current_shape == "line":
                self.canvas.create_line(x1, y1, x2, y2, width=self.brush_size, fill=outline_color, capstyle=tk.ROUND)
            elif self.current_shape == "rectangle":
                self.canvas.create_rectangle(x1, y1, x2, y2, outline=outline_color, width=self.brush_size, fill=fill_color_final)
            elif self.current_shape == "circle":
                self.canvas.create_oval(x1, y1, x2, y2, outline=outline_color, width=self.brush_size, fill=fill_color_final)
            elif self.current_shape == "triangle":
                mid_x = (x1 + x2) / 2
                points = [x1, y2, x2, y2, mid_x, y1]
                self.canvas.create_polygon(points, outline=outline_color, width=self.brush_size, fill=fill_color_final)
            elif self.current_shape == "star":
                points = self.calculate_star_points(x1, y1, x2, y2)
                self.canvas.create_polygon(points, outline=outline_color, width=self.brush_size, fill=fill_color_final)
            self.canvas_modified = True  # Mark as modified when shape is drawn
        self.last_x, self.last_y = None, None
        self.active_item = None
        self.update_status_bar(event)

    def on_right_click(self, event):
        if self.current_tool == "zoom":
            self.apply_zoom(1/1.2)
        else:
            self.copy_to_clipboard(event.x, event.y)
            self.status_bar_message("Copied to clipboard")
            self.canvas_modified = True  # Mark as modified when copying

    def on_middle_click(self, event):
        self.paste_from_clipboard(event.x, event.y)
        self.status_bar_message("Pasted from clipboard")
        self.canvas_modified = True  # Mark as modified when pasting

    def copy_to_clipboard(self, x, y):
        self.clipboard = self.get_canvas_image_data()
        self.history.append(self.get_canvas_image_data())
        self.redo_stack.clear()
        self.canvas_modified = True

    def paste_from_clipboard(self, x, y):
        if self.clipboard:
            self.history.append(self.get_canvas_image_data())
            self.redo_stack.clear()
            self.canvas_modified = True
            pasted_img = self.clipboard.copy()
            pasted_tk_image = ImageTk.PhotoImage(pasted_img)
            self.canvas.create_image(x, y, image=pasted_tk_image, anchor=tk.NW)
            self.status_bar_message("Pasted image")

    def create_text_input(self, x, y):
        text_input = simpledialog.askstring("Text Input", "Enter text:")
        if text_input:
            font_dialog = tk.Toplevel(self.master)
            font_dialog.title("Font Settings")
            frame = ttk.Frame(font_dialog, padding=10)
            frame.pack(fill=tk.BOTH, expand=True)
            ttk.Label(frame, text="Font Size:").grid(row=0, column=0, padx=5, pady=5)
            size_entry = ttk.Entry(frame)
            size_entry.insert(0, str(self.font_size))
            size_entry.grid(row=0, column=1, padx=5, pady=5)
            ttk.Button(frame, text="Apply", command=lambda: self._apply_text(x, y, text_input, int(size_entry.get()), font_dialog)).grid(row=1, column=0, columnspan=2, pady=10)
            font_dialog.wait_window(font_dialog)
        else:
            self.status_bar_message("Text input cancelled.")

    def _apply_text(self, x, y, text, size, dialog):
        self.font_size = size
        self.canvas.create_text(x, y, text=text, fill=self.current_color,
                              font=(self.font_name, self.font_size, "bold"), anchor=tk.NW)
        dialog.destroy()
        self.canvas_modified = True
        self.status_bar_message(f"Text added at ({x}, {y})")

    def pick_color_from_canvas(self, x, y):
        try:
            img = self.get_canvas_image_data().convert("RGB")
            img_x = int(x / self.zoom_level)
            img_y = int(y / self.zoom_level)
            if 0 <= img_x < img.width and 0 <= img_y < img.height:
                rgb_color = img.getpixel((img_x, img_y))
                hex_color = '#%02x%02x%02x' % rgb_color
                self.set_current_color(hex_color)
            else:
                self.status_bar_message("Out of bounds")
        except Exception as e:
            self.status_bar_message(f"Color pick failed: {e}")

    def fill_area(self, start_x, start_y):
        if not self.fill_color:
            self.status_bar_message("Enable 'Fill' to use this tool.")
            return
        self.history.append(self.get_canvas_image_data())
        self.redo_stack.clear()
        self.canvas_modified = True
        img = self.get_canvas_image_data().convert("RGB")
        pixels = img.load()
        start_pixel_x = int(start_x / self.zoom_level)
        start_pixel_y = int(start_y / self.zoom_level)
        if not (0 <= start_pixel_x < img.width and 0 <= start_pixel_y < img.height):
            self.status_bar_message("Click inside canvas.")
            return
        target_color = pixels[start_pixel_x, start_pixel_y]
        replacement_color_rgb = tuple(int(self.fill_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        if target_color == replacement_color_rgb:
            self.status_bar_message("Already filled with this color.")
            return
        q = [(start_pixel_x, start_pixel_y)]
        visited = set()
        while q:
            x, y = q.pop(0)
            if (x, y) in visited or not (0 <= x < img.width and 0 <= y < img.height):
                continue
            visited.add((x, y))
            if pixels[x, y] == target_color:
                pixels[x, y] = replacement_color_rgb
                q.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
        self.canvas.delete("all")
        self._display_image_on_canvas(img)
        self.status_bar_message("Area filled.")

    def calculate_star_points(self, x1, y1, x2, y2, num_points=5):
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        outer_radius = max(abs(x2 - x1), abs(y2 - y1)) / 2 or 5
        inner_radius = outer_radius * 0.4
        points = []
        for i in range(num_points * 2):
            radius = outer_radius if i % 2 == 0 else inner_radius
            angle = math.pi / num_points * i - math.pi / 2
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            points.append(x)
            points.append(y)
        return points

    def update_status_bar(self, event):
        x, y = (event.x, event.y) if event else (self.last_x or 0, self.last_y or 0)
        display_x = int(x / self.zoom_level)
        display_y = int(y / self.zoom_level)
        self.status_bar.config(text=f"X: {display_x}, Y: {display_y} | Zoom: {self.zoom_level*100:.0f}%")

    def status_bar_message(self, message):
        self.status_bar.config(text=message)
        self.master.after(2000, lambda: self.update_status_bar(None))

    def on_closing(self):
        if self.canvas_modified:
            response = messagebox.askyesnocancel("Save Changes?", "Unsaved changes. Save?")
            if response is True:
                self.save_canvas()
                if not self.canvas_modified:
                    self.master.destroy()
            elif response is False:
                self.master.destroy()
        else:
            self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()