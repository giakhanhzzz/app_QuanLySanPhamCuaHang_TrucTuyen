import json
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import requests
from PIL import Image, ImageTk
from io import BytesIO

# Cấu hình giao diện
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role

class Product:
    def __init__(self, name, price, stock, image, description=""):
        self.name = name
        self.price = price
        self.stock = stock
        self.image = image
        self.description = description

class GUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Quản Lý Danh Sách Sản Phẩm Trong Cửa Hàng Trực Tuyến")
        self.root.geometry("800x500")
        self.users = self.load_users()
        self.products = self.load_products()
        self.current_user = None
        self.image_cache = {}  # Cache để lưu ảnh
        if not self.products:
            self.fetch_products_from_api()
        self.create_login_widgets()

    def load_users(self):
        try:
            with open("users.json", "r", encoding="utf-8") as file:
                return [User(u["username"], u["password"], u["role"]) for u in json.load(file)]
        except (FileNotFoundError, json.JSONDecodeError):
            messagebox.showerror("Lỗi", "Không tìm thấy file users.json hoặc file bị lỗi!")
            return []

    def save_users(self):
        users_data = [{"username": user.username, "password": user.password, "role": user.role} for user in self.users]
        with open("users.json", "w", encoding="utf-8") as file:
            json.dump(users_data, file, indent=4, ensure_ascii=False)

    def load_products(self):
        try:
            with open("products.json", "r", encoding="utf-8") as file:
                return [Product(p["name"], p["price"], p["stock"], p["image"], p.get("description", "")) for p in json.load(file)]
        except (FileNotFoundError, json.JSONDecodeError):
            messagebox.showerror("Lỗi", "Không tìm thấy file products.json hoặc file bị lỗi!")
            return []

    def save_products(self):
        products_data = [{"name": p.name, "price": p.price, "stock": p.stock, "image": p.image, "description": p.description} for p in self.products]
        with open("products.json", "w", encoding="utf-8") as file:
            json.dump(products_data, file, indent=4, ensure_ascii=False)

    def fetch_products_from_api(self):
        try:
            response = requests.get("https://fakestoreapi.com/products")
            products = response.json()[:20]  # Lấy 20 sản phẩm
            self.products = [Product(
                name=prod["title"],
                price=prod["price"],
                stock=10,
                image=prod["image"],
                description=prod.get("description", "")
            ) for prod in products]
            self.save_products()
            messagebox.showinfo("Thành công", "Đã lấy dữ liệu sản phẩm từ API!")
            self.create_main_widgets()
        except:
            messagebox.showerror("Lỗi", "Không thể lấy dữ liệu từ API!")

    def load_image(self, url, size=(100, 100)):
        if url in self.image_cache and size in self.image_cache[url]:
            return self.image_cache[url][size]
        try:
            response = requests.get(url)
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            img = img.resize(size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            if url not in self.image_cache:
                self.image_cache[url] = {}
            self.image_cache[url][size] = photo
            return photo
        except:
            return None

    def create_login_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        frame = ctk.CTkFrame(self.root)
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(frame, text="Đăng Nhập", font=("Arial", 20)).pack(pady=10)
        ctk.CTkLabel(frame, text="Tên người dùng").pack()
        username_entry = ctk.CTkEntry(frame)
        username_entry.pack()
        ctk.CTkLabel(frame, text="Mật khẩu").pack()
        password_entry = ctk.CTkEntry(frame, show="*")
        password_entry.pack()
        def login():
            username = username_entry.get()
            password = password_entry.get()
            user = next((u for u in self.users if u.username == username and u.password == password), None)
            if user:
                self.current_user = user
                self.create_main_widgets()
            else:
                messagebox.showerror("Lỗi", "Sai tên người dùng hoặc mật khẩu!")
        ctk.CTkButton(frame, text="Đăng nhập", command=login).pack(pady=10)
        # Nút đăng ký
        def register():
            window = ctk.CTkToplevel(self.root)
            window.title("Đăng Ký")
            window.geometry("300x250")
            ctk.CTkLabel(window, text="Đăng Ký Người Dùng", font=("Arial", 16, "bold")).pack(pady=10)
            ctk.CTkLabel(window, text="Tên người dùng").pack()
            reg_username = ctk.CTkEntry(window)
            reg_username.pack()
            ctk.CTkLabel(window, text="Mật khẩu").pack()
            reg_password = ctk.CTkEntry(window, show="*")
            reg_password.pack()
            ctk.CTkLabel(window, text="Vai trò (admin/user)").pack()
            reg_role = ctk.CTkEntry(window)
            reg_role.pack()
            def submit():
                username = reg_username.get()
                password = reg_password.get()
                role = reg_role.get().lower()
                if username and password and role in ["admin", "user"]:
                    if not any(u.username == username for u in self.users):
                        self.users.append(User(username, password, role))
                        self.save_users()
                        messagebox.showinfo("Thành công", "Đăng ký thành công!")
                        window.destroy()
                    else:
                        messagebox.showerror("Lỗi", "Tên người dùng đã tồn tại!")
                else:
                    messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ và hợp lệ!")
            ctk.CTkButton(window, text="Đăng ký", command=submit).pack(pady=10)
        ctk.CTkButton(frame, text="Đăng ký", command=register).pack(pady=5)

    def create_main_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.main_frame = ctk.CTkFrame(self.root, fg_color="#B0B0B0")
        self.main_frame.pack(expand=True, fill="both", padx=10, pady=10)
        nav_frame = ctk.CTkFrame(self.main_frame, fg_color="#808080", height=50)
        nav_frame.pack(fill="x", pady=(0, 10))
        nav_frame.pack_propagate(False)
        ctk.CTkLabel(nav_frame, text="CỬA HÀNG TRỰC TUYẾN", font=("Arial", 16, "bold")).pack(side="left", padx=10)
        ctk.CTkButton(nav_frame, text="Danh Sách", command=self.create_main_widgets).pack(side="left", padx=5)
        if self.current_user and self.current_user.role == "admin":
            ctk.CTkButton(nav_frame, text="Thêm Sản Phẩm", command=self.add_product).pack(side="left", padx=5)
            ctk.CTkButton(nav_frame, text="Quản Lý Người Dùng", command=self.manage_users).pack(side="left", padx=5)
            ctk.CTkButton(nav_frame, text="Tải từ API", command=self.fetch_products_from_api).pack(side="left", padx=5)
        ctk.CTkButton(nav_frame, text="Đăng Xuất", command=self.create_login_widgets).pack(side="right", padx=10)

        search_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(search_frame, text="Tìm kiếm sản phẩm:", font=("Arial", 14)).pack(side="left")
        self.search_entry = ctk.CTkEntry(search_frame, width=200)
        self.search_entry.pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Tìm kiếm", command=self.search_products).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Load lại", command=self.create_main_widgets).pack(side="left", padx=5)

        ctk.CTkLabel(self.main_frame, text="Danh Sách Sản Phẩm", font=("Arial", 20)).pack(pady=10)
        product_grid = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        product_grid.pack(expand=True, fill="both")
        self.scrollable_frame = ctk.CTkScrollableFrame(product_grid, fg_color="transparent")
        self.scrollable_frame.pack(expand=True, fill="both")
        self.display_products(self.products)

    def display_products(self, products):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        for i in range(len(products)):
            self.scrollable_frame.grid_columnconfigure(i % 2, weight=1)
            self.scrollable_frame.grid_rowconfigure(i // 2, weight=1)
        for i, product in enumerate(products):
            card = ctk.CTkFrame(self.scrollable_frame, fg_color="#E8E8E8", corner_radius=5, border_width=2, border_color="#A0A0A0", width=300, height=270)
            card.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="nsew")
            card.grid_propagate(False)
            photo = self.load_image(product.image, size=(100, 100))
            if photo:
                image_label = ctk.CTkLabel(card, image=photo, text="")
                image_label.image = photo
                image_label.pack(pady=5)
            else:
                ctk.CTkLabel(card, text="Không có ảnh", font=("Arial", 14)).pack(pady=5)
            ctk.CTkLabel(card, text=product.name, font=("Arial", 16, "bold"), wraplength=250).pack(pady=5)
            ctk.CTkLabel(card, text=f"Giá: {product.price} USD", font=("Arial", 14)).pack(pady=5)
            ctk.CTkLabel(card, text=f"Tồn kho: {product.stock}", font=("Arial", 14)).pack(pady=5)
            if self.current_user and self.current_user.role == "user":
                ctk.CTkButton(card, text="Xem chi tiết", width=100, fg_color="#1E90FF", hover_color="#104E8B", command=lambda idx=i: self.view_product_details(idx, products)).place(relx=0.5, rely=0.9, anchor="center")
            elif self.current_user and self.current_user.role == "admin":
                ctk.CTkButton(card, text="Sửa", width=80, command=lambda idx=i: self.edit_product(idx)).place(relx=0.35, rely=0.9, anchor="center")
                ctk.CTkButton(card, text="Xóa", width=80, command=lambda idx=i: self.delete_product(idx)).place(relx=0.65, rely=0.9, anchor="center")

    def search_products(self):
        keyword = self.search_entry.get().lower().strip()
        if not keyword:
            self.display_products(self.products)
        else:
            filtered_products = [p for p in self.products if keyword in p.name.lower() or keyword in p.description.lower()]
            self.display_products(filtered_products)

    def view_product_details(self, index, products):
        details_window = ctk.CTkToplevel(self.root)
        details_window.title("Chi Tiết Sản Phẩm")
        details_window.geometry("400x450")
        product = products[index]
        ctk.CTkLabel(details_window, text="Chi Tiết Sản Phẩm", font=("Arial", 18, "bold")).pack(pady=10)
        photo = self.load_image(product.image, size=(150, 150))
        if photo:
            image_label = ctk.CTkLabel(details_window, image=photo, text="")
            image_label.image = photo
            image_label.pack(pady=5)
        else:
            ctk.CTkLabel(details_window, text="Không có ảnh", font=("Arial", 14)).pack(pady=5)
        ctk.CTkLabel(details_window, text=f"Tên: {product.name}", font=("Arial", 16), wraplength=350).pack(pady=5)
        ctk.CTkLabel(details_window, text=f"Giá: {product.price} USD", font=("Arial", 16)).pack(pady=5)
        ctk.CTkLabel(details_window, text=f"Tồn kho: {product.stock}", font=("Arial", 16)).pack(pady=5)
        ctk.CTkLabel(details_window, text=f"Mô tả: {product.description}", font=("Arial", 14), wraplength=350).pack(pady=5)
        ctk.CTkButton(details_window, text="Đóng", width=100, command=details_window.destroy).pack(pady=10)

    def manage_users(self):
        manage_window = ctk.CTkToplevel(self.root)
        manage_window.title("Quản Lý Người Dùng")
        manage_window.geometry("600x400")
        ctk.CTkLabel(manage_window, text="Danh Sách Người Dùng", font=("Arial", 20)).pack(pady=10)
        # Nút thêm người dùng
        ctk.CTkButton(manage_window, text="Thêm Người Dùng", command=self.add_user_form).pack(pady=5)
        # Danh sách người dùng
        user_grid = ctk.CTkFrame(manage_window, fg_color="transparent")
        user_grid.pack(expand=True, fill="both")
        scrollable_frame = ctk.CTkScrollableFrame(user_grid, fg_color="transparent")
        scrollable_frame.pack(expand=True, fill="both")
        for i in range(len(self.users)):
            scrollable_frame.grid_columnconfigure(i % 2, weight=1)
            scrollable_frame.grid_rowconfigure(i // 2, weight=1)
        for i, user in enumerate(self.users):
            card = ctk.CTkFrame(scrollable_frame, fg_color="#E8E8E8", corner_radius=5, border_width=2, border_color="#A0A0A0", width=250, height=100)
            card.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="nsew")
            card.grid_propagate(False)
            ctk.CTkLabel(card, text=f"Tên: {user.username}", font=("Arial", 14)).pack(pady=5)
            ctk.CTkLabel(card, text=f"Vai trò: {user.role}", font=("Arial", 14)).pack(pady=5)
            ctk.CTkButton(card, text="Sửa", width=80, command=lambda idx=i: self.edit_user_form(idx)).place(relx=0.35, rely=0.8, anchor="center")
            ctk.CTkButton(card, text="Xóa", width=80, command=lambda idx=i: self.delete_user(idx, manage_window)).place(relx=0.65, rely=0.8, anchor="center")

    def add_user_form(self):
        window = ctk.CTkToplevel(self.root)
        window.title("Thêm Người Dùng")
        window.geometry("300x250")
        ctk.CTkLabel(window, text="Thêm Người Dùng Mới", font=("Arial", 16, "bold")).pack(pady=10)
        ctk.CTkLabel(window, text="Tên người dùng").pack()
        username_entry = ctk.CTkEntry(window)
        username_entry.pack()
        ctk.CTkLabel(window, text="Mật khẩu").pack()
        password_entry = ctk.CTkEntry(window, show="*")
        password_entry.pack()
        ctk.CTkLabel(window, text="Vai trò (admin/user)").pack()
        role_entry = ctk.CTkEntry(window)
        role_entry.pack()
        def submit():
            username = username_entry.get()
            password = password_entry.get()
            role = role_entry.get().lower()
            if username and password and role in ["admin", "user"]:
                if not any(u.username == username for u in self.users):
                    self.users.append(User(username, password, role))
                    self.save_users()
                    messagebox.showinfo("Thành công", "Đã thêm người dùng mới!")
                    window.destroy()
                    self.manage_users()  # Làm mới danh sách
                else:
                    messagebox.showerror("Lỗi", "Tên người dùng đã tồn tại!")
            else:
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ và hợp lệ!")
        ctk.CTkButton(window, text="Thêm", command=submit).pack(pady=10)

    def edit_user_form(self, index):
        window = ctk.CTkToplevel(self.root)
        window.title("Sửa Người Dùng")
        window.geometry("300x250")
        user = self.users[index]
        ctk.CTkLabel(window, text="Sửa Người Dùng", font=("Arial", 16, "bold")).pack(pady=10)
        ctk.CTkLabel(window, text="Tên người dùng").pack()
        username_entry = ctk.CTkEntry(window)
        username_entry.insert(0, user.username)
        username_entry.pack()
        ctk.CTkLabel(window, text="Mật khẩu").pack()
        password_entry = ctk.CTkEntry(window, show="*")
        password_entry.insert(0, user.password)
        password_entry.pack()
        ctk.CTkLabel(window, text="Vai trò (admin/user)").pack()
        role_entry = ctk.CTkEntry(window)
        role_entry.insert(0, user.role)
        role_entry.pack()
        def submit():
            username = username_entry.get()
            password = password_entry.get()
            role = role_entry.get().lower()
            if username and password and role in ["admin", "user"]:
                if username == user.username or not any(u.username == username for u in self.users):
                    self.users[index] = User(username, password, role)
                    self.save_users()
                    messagebox.showinfo("Thành công", "Đã cập nhật người dùng!")
                    window.destroy()
                    self.manage_users()  # Làm mới danh sách
                else:
                    messagebox.showerror("Lỗi", "Tên người dùng đã tồn tại!")
            else:
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ và hợp lệ!")
        ctk.CTkButton(window, text="Cập nhật", command=submit).pack(pady=10)

    def delete_user(self, index, manage_window):
        self.users.pop(index)
        self.save_users()
        manage_window.destroy()
        self.manage_users()  # Làm mới danh sách

    def product_form(self, title, submit_callback, default_values=None):
        window = ctk.CTkToplevel(self.root)
        window.title(title)
        window.geometry("300x300")
        ctk.CTkLabel(window, text="Tên sản phẩm").pack()
        name_entry = ctk.CTkEntry(window)
        name_entry.pack()
        ctk.CTkLabel(window, text="Giá (USD)").pack()
        price_entry = ctk.CTkEntry(window)
        price_entry.pack()
        ctk.CTkLabel(window, text="Số lượng tồn kho").pack()
        stock_entry = ctk.CTkEntry(window)
        stock_entry.pack()
        ctk.CTkLabel(window, text="URL ảnh").pack()
        image_entry = ctk.CTkEntry(window)
        image_entry.pack()
        ctk.CTkLabel(window, text="Mô tả").pack()
        description_entry = ctk.CTkEntry(window)
        description_entry.pack()
        if default_values:
            name_entry.insert(0, default_values["name"])
            price_entry.insert(0, default_values["price"])
            stock_entry.insert(0, default_values["stock"])
            image_entry.insert(0, default_values["image"])
            description_entry.insert(0, default_values["description"])
        def submit():
            name = name_entry.get()
            try:
                price = float(price_entry.get())
                stock = int(stock_entry.get())
                image = image_entry.get()
                description = description_entry.get()
                if name and price >= 0 and stock >= 0 and image:
                    submit_callback(name, price, stock, image, description)
                    self.save_products()
                    self.create_main_widgets()
                    window.destroy()
                else:
                    messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ và hợp lệ!")
            except ValueError:
                messagebox.showerror("Lỗi", "Giá và số lượng phải là số hợp lệ!")
        ctk.CTkButton(window, text="Xác nhận", command=submit).pack(pady=10)

    def add_product(self):
        def submit_callback(name, price, stock, image, description):
            self.products.append(Product(name, price, stock, image, description))
        self.product_form("Thêm Sản Phẩm", submit_callback)

    def edit_product(self, index):
        def submit_callback(name, price, stock, image, description):
            self.products[index] = Product(name, price, stock, image, description)
        self.product_form("Sửa Sản Phẩm", submit_callback, {
            "name": self.products[index].name,
            "price": self.products[index].price,
            "stock": self.products[index].stock,
            "image": self.products[index].image,
            "description": self.products[index].description
        })

    def delete_product(self, index):
        self.products.pop(index)
        self.save_products()
        self.create_main_widgets()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = GUI()
    app.run()