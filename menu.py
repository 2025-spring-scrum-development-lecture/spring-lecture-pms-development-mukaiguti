import tkinter as tk
import os

class Menu:
    def __init__(self, root):
        self.root = root
        self.root.title("ホテル管理システム")
        self.root.geometry("1000x700")
        
        # メニュー画面の作成
        self.create_menu_screen()
    
    def create_menu_screen(self):
        # 以前の画面をクリア
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # メインメニューフレームの作成
        menu_frame = tk.Frame(self.root, padx=20, pady=20)
        menu_frame.pack(fill=tk.BOTH, expand=True)
        
        # タイトル
        title_label = tk.Label(menu_frame, text="ホテル管理システム", font=("Helvetica", 18, "bold"))
        title_label.pack(pady=20)
        
        # メニューボタン
        btn_width = 30
        btn_height = 2
        
        create_quote_btn = tk.Button(menu_frame, text="宿泊見積作成", width=btn_width, height=btn_height,
                                    command=self.show_quote_screen, bg="#4CAF50", fg="white")
        create_quote_btn.pack(pady=10)
        
        create_quote_btn = tk.Button(menu_frame, text="宴会見積作成", width=btn_width, height=btn_height,
                                    command=self.show_enkai_screen, bg="skyblue", fg="white")
        create_quote_btn.pack(pady=10)
        
        exit_btn = tk.Button(menu_frame, text="終了", width=btn_width, height=btn_height,command=self.root.destroy,
                             bg="#F44336", fg="white")
        exit_btn.pack(pady=10)
        
    def show_quote_screen(self):
        from app import HotelManagementSystem
        for widget in self.root.winfo_children():
            widget.destroy()
        HotelManagementSystem(self.root)
    
    def show_enkai_screen(self):
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = Menu(root)
    root.mainloop()





















