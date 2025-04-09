from menu import Menu
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import locale
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate


# 日本語の日付フォーマット用にロケールを設定
try:
    locale.setlocale(locale.LC_ALL, 'ja_JP.UTF-8')
except:
    pass

class HotelManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("ホテル管理システム")
        self.root.geometry("1000x700")
        self.config_file = "hotel_config.json"
        
         # 見積書保存用のディレクトリ
        self.quotes_dir = "quotes"
        if not os.path.exists(self.quotes_dir):
            os.makedirs(self.quotes_dir)
        
        # メール設定を固定値に設定（メール設定画面を削除）
        self.email_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "y.mukaiguchi.sys24@morijyobi.ac.jp",
            "password": "iioy yrtg hxff eknq",
            "sender": "y.mukaiguchi.sys24@morijyobi.ac.jp"
        }
        
        # 料金データの読み込み
        self.load_pricing_data()
        
        self.show_quote_screen()
        
    def load_pricing_data(self):
        self.pricing = {
            "room_types": {
                "1-2_和室": {"八幡ポーク": 12400, "岩手県産": 15400, "前沢牛": 18400, "素泊まり": 8500},
                "2_西館和室": {"八幡ポーク": 12400, "岩手県産": 15400, "前沢牛": 18400, "素泊まり": None},
                "2-5_岩手山側和室": {"八幡ポーク": 12400, "岩手県産": 15400, "前沢牛": 18400, "素泊まり": None},
                "2-5_岩手山側露天風呂付き和室": {"八幡ポーク": 14400, "岩手県産": 17400, "前沢牛": 20400, "素泊まり": None},
                "2-6_西館和室10畳": {"八幡ポーク": 12400, "岩手県産": 15400, "前沢牛": 21400, "素泊まり": None},
                "2-6_1F露天風呂付き和室": {"八幡ポーク": 15400, "岩手県産": 18400, "前沢牛": 21400, "素泊まり": None},
                "2-6_1F西館和室": {"八幡ポーク": 12400, "岩手県産": 15400, "前沢牛": 21400, "素泊まり": None},
                "2-6_西館和室20畳": {"八幡ポーク": 12400, "岩手県産": 15400, "前沢牛": 21400, "素泊まり": None},
            },
            "child_price": 7200,  
            "early_booking_discount": {
                60: 0.10,  # 60日前: 10%割引
                90: 0.15   # 90日前: 15%割引
            },
            "saturday_surcharge": 2000  # 土曜日追加料金
        }
    
    
    def show_quote_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        # メインフレーム
        quote_frame = tk.Frame(self.root, padx=20, pady=20)
        quote_frame.pack(fill=tk.BOTH, expand=True)

        # Canvasの作成
        canvas = tk.Canvas(quote_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # スクロールバーの作成
        scrollbar = tk.Scrollbar(quote_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)

        # コンテンツフレームをCanvas内に作成
        content_frame = tk.Frame(canvas)
        window_id = canvas.create_window((0, 0), window=content_frame, anchor="n")

        # スクロール範囲を更新
        def update_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        content_frame.bind("<Configure>", update_scroll_region)
        
        def on_mouse_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.root.bind_all("<MouseWheel>", on_mouse_wheel)  
        def center_content_frame():
            canvas_width = canvas.winfo_width()
            content_width = content_frame.winfo_reqwidth()
            x_position = (canvas_width - content_width) / 2
            canvas.coords(window_id, x_position, 0)

        canvas.bind("<Configure>", lambda event: center_content_frame())

        # タイトル
        title_label = tk.Label(content_frame, text="宿泊見積作成", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)

        # お客様情報フレーム
        customer_frame = tk.LabelFrame(content_frame, text="お客様情報", padx=10, pady=10)
        customer_frame.pack(fill=tk.X, pady=10)

        # お客様情報のグリッド
        customer_grid = tk.Frame(customer_frame)
        customer_grid.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(customer_grid, text="お名前:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.customer_name = tk.Entry(customer_grid, width=30)
        self.customer_name.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        tk.Label(customer_grid, text="電話番号:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.customer_phone = tk.Entry(customer_grid, width=20)
        self.customer_phone.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)

        tk.Label(customer_grid, text="メール:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.customer_email = tk.Entry(customer_grid, width=30)
        self.customer_email.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)


        # 予約詳細フレーム
        res_frame = tk.LabelFrame(content_frame, text="予約詳細", padx=10, pady=10)
        res_frame.pack(fill=tk.X, pady=10)

        res_grid = tk.Frame(res_frame)
        res_grid.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(res_grid, text="チェックイン日:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.checkin_date = tk.Entry(res_grid, width=15)
        self.checkin_date.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.checkin_date.insert(0, datetime.datetime.now().strftime("%Y/%m/%d"))

        tk.Label(res_grid, text="チェックアウト日:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.checkout_date = tk.Entry(res_grid, width=15)
        self.checkout_date.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)

        tk.Label(res_grid, text="部屋タイプ:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.room_type = ttk.Combobox(res_grid, width=25, state="readonly")
        self.room_type["values"] = list(self.pricing["room_types"].keys())
        self.room_type.current(0)
        self.room_type.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        tk.Label(res_grid, text="食事プラン:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.meal_plan = ttk.Combobox(res_grid, width=15, state="readonly")
        self.meal_plan["values"] = ["八幡ポーク", "岩手県産", "前沢牛", "素泊まり"]
        self.meal_plan.current(0)
        self.meal_plan.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)

        tk.Label(res_grid, text="大人人数:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.num_adults = ttk.Spinbox(res_grid, from_=1, to=10, width=5)
        self.num_adults.set(2)
        self.num_adults.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        tk.Label(res_grid, text="子供人数:").grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        self.num_children = ttk.Spinbox(res_grid, from_=0, to=10, width=5)
        self.num_children.set(0)
        self.num_children.grid(row=2, column=3, sticky=tk.W, padx=5, pady=5)

        # 計算ボタン
        calculate_btn = tk.Button(content_frame, text="見積計算", command=self.calculate_quote, bg="#4CAF50", fg="white", width=20, height=2)
        calculate_btn.pack(pady=10)

        # 結果フレーム
        results_frame = tk.LabelFrame(content_frame, text="見積結果", padx=10, pady=10)
        results_frame.pack(fill=tk.X, pady=10)

        self.results_text = tk.Text(results_frame, height=10, width=80)
        self.results_text.pack(padx=10, pady=10)
        self.results_text.configure(state="disabled")
        

        # ボタンフレーム
        buttons_frame = tk.Frame(content_frame)
        buttons_frame.pack(fill=tk.X, pady=10)

        send_quote_btn = tk.Button(buttons_frame, text="見積送信", command=self.show_quote_sent, bg="#2196F3", fg="white", width=15, height=2)
        send_quote_btn.pack(side=tk.LEFT, padx=10)

        return_btn = tk.Button(buttons_frame, text="メニューに戻る", command=self.create_menu_screen, bg="#F44336", fg="white", width=15, height=2)
        return_btn.pack(side=tk.RIGHT, padx=10)

    
    def calculate_quote(self):
        self.results_text.configure(state="normal")
        try:
            # 選択された値を取得
            room_type = self.room_type.get()
            meal_plan = self.meal_plan.get()
            num_adults = int(self.num_adults.get())
            num_children = int(self.num_children.get())
            
            # 日付の取得
            checkin = datetime.datetime.strptime(self.checkin_date.get(), "%Y/%m/%d")
            checkout = datetime.datetime.strptime(self.checkout_date.get(), "%Y/%m/%d") if self.checkout_date.get() else checkin + datetime.timedelta(days=1)
            
            # 宿泊日数の計算
            nights = (checkout - checkin).days
            if nights <= 0:
                messagebox.showerror("エラー", "チェックアウト日はチェックイン日より後である必要があります。")
                return
            
            # 基本料金の計算

            base_cost_per_adult = self.pricing["room_types"][room_type][meal_plan]
            child_cost = self.pricing["child_price"]
            
            # 早期予約割引のチェック
            today = datetime.datetime.today()
            days_until_checkin = (checkin - today).days
            
            discount_rate = 0
            if days_until_checkin >= 90:
                discount_rate = self.pricing["early_booking_discount"][90]
            elif days_until_checkin >= 60:
                discount_rate = self.pricing["early_booking_discount"][60]
            
            # 土曜日追加料金のチェック
            saturday_surcharge = 0
            current_date = checkin
            for _ in range(nights):
                if current_date.weekday() == 5:  # 土曜日は5
                    saturday_surcharge += self.pricing["saturday_surcharge"] * (num_adults + num_children)
                current_date += datetime.timedelta(days=1)
            
            # 合計料金の計算
            adult_cost = base_cost_per_adult * num_adults * nights
            children_cost = child_cost * num_children * nights
            total_before_discount = adult_cost + children_cost + saturday_surcharge
            discount_amount = total_before_discount * discount_rate
            total_after_discount = total_before_discount - discount_amount
            
            # 結果の表示
            result = f"見積詳細:\n\n"
            result += f"部屋タイプ: {room_type}\n"
            result += f"食事プラン: {meal_plan}\n"
            result += f"滞在期間: {checkin.strftime('%Y年%m月%d日')} から {checkout.strftime('%Y年%m月%d日')} ({nights}泊)\n"
            result += f"大人: {num_adults}人 × {base_cost_per_adult:,}円 × {nights}泊 = {adult_cost:,}円\n"
            
            if num_children > 0:
                result += f"子供: {num_children}人 × {child_cost:,}円 × {nights}泊 = {children_cost:,}円\n"
            
            if saturday_surcharge > 0:
                result += f"土曜日追加料金: {saturday_surcharge:,}円\n"
            
            result += f"\n小計: {total_before_discount:,}円\n"
            
            if discount_rate > 0:
                result += f"早期予約割引 ({discount_rate*100:.0f}%): -{discount_amount:,}円\n"
            
            result += f"\n合計: {total_after_discount:,}円 (税込)"
            
            # 結果テキストウィジェットの更新
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, result)
            self.results_text.configure(state="disabled")
            
            # 見積結果を保存（メール送信時に使用）
            self.quote_result = result
            
            # JSONに保存するための詳細情報を保存
            self.quote_details = {
                "customer": {
                    "name": self.customer_name.get(),
                    "email": self.customer_email.get(),
                    "phone": self.customer_phone.get()
                },
                "reservation": {
                    "room_type": room_type,
                    "meal_plan": meal_plan,
                    "checkin": checkin.strftime("%Y-%m-%d"),
                    "checkout": checkout.strftime("%Y-%m-%d"),
                    "nights": nights,
                    "adults": num_adults,
                    "children": num_children
                },
                "pricing": {
                    "adult_rate": base_cost_per_adult,
                    "child_rate": child_cost,
                    "adult_total": adult_cost,
                    "children_total": children_cost,
                    "saturday_surcharge": saturday_surcharge,
                    "discount_rate": discount_rate,
                    "discount_amount": discount_amount,
                    "subtotal": total_before_discount,
                    "total": total_after_discount
                },
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 予約情報を保存（簡易表示用）
            self.reservation_info = {
                "customer_name": self.customer_name.get(),
                "customer_email": self.customer_email.get(),
                "total_price": f"{total_after_discount:,}円"
            }
            
        except Exception as e:
            messagebox.showerror("エラー", f"計算中にエラーが発生しました: {str(e)}")
            self.results_text.configure(state="disabled")
    # 設定ファイル関連のメソッドは残すが、簡略化する
    def load_email_config(self):
        # メール設定は固定のため、設定ファイルからの読み込みは行わない
        pass

    def save_email_config(self):
        # メール設定は固定のため、設定ファイルへの保存は行わない
        return True
    
    # 新しく追加: 見積書をJSONファイルに保存する関数
    def save_quote_to_json(self):
        if not hasattr(self, 'quote_details'):
            return False
        
        try:
            # ファイル名を生成 (顧客名_日付_時間.json)
            customer_name = self.quote_details["customer"]["name"]
            # 空白やファイル名に使えない文字を置換
            safe_name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in customer_name)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_name}_{timestamp}.json"
            filepath = os.path.join(self.quotes_dir, filename)
            
            # JSONファイルに保存
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.quote_details, f, ensure_ascii=False, indent=4)
            
            return filepath
        
        except Exception as e:
            print(f"見積書保存エラー: {str(e)}")
            return False

    def send_email_quote(self):
        # メールアドレスが入力されているか確認
        customer_email = self.customer_email.get().strip()
        if not customer_email:
            messagebox.showerror("エラー", "メールアドレスを入力してください。")
            return False
          
        # 見積が計算されているか確認
        if not hasattr(self, 'quote_result'):
            messagebox.showerror("エラー", "先に見積計算を行ってください。")
            return False
          
        try:
            # メール作成
            msg = MIMEMultipart()
            msg['From'] = self.email_config["sender"]
            msg['To'] = customer_email
            msg['Date'] = formatdate()
            msg['Subject'] = f"【ホテル予約】{self.customer_name.get()} 様 宿泊見積"
              
            # メール本文の作成
            body = f"""
{self.customer_name.get()} 様

この度はお問い合わせいただき、誠にありがとうございます。
ご希望の宿泊プランの見積をお送りいたします。

====================
{self.quote_result}
====================

ご予約やご質問がございましたら、お気軽にお問い合わせください。
お客様のご来館を心よりお待ちしております。

--
ホテル〇〇
TEL: 000-000-0000
Email: {self.email_config["sender"]}
            """
              
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
              
            # SMTPサーバーに接続してメール送信
            with smtplib.SMTP(self.email_config["smtp_server"], self.email_config["smtp_port"]) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.email_config["username"], self.email_config["password"])
                server.send_message(msg)
            
            # 送信先メールアドレスを保存（画面遷移後に使用するため）
            self.sent_email = customer_email
              
            return True
              
        except Exception as e:
            messagebox.showerror("エラー", f"メール送信中にエラーが発生しました: {str(e)}")
            return False

            
    def show_quote_sent(self):
        # メール送信を試みる
        if hasattr(self, 'quote_result'):
            success = self.send_email_quote()
            if not success:
                # メール送信に失敗した場合は、関数を終了
                return
            
            # メール送信成功後、見積書をJSONファイルに保存
            json_filepath = self.save_quote_to_json()
        else:
            messagebox.showerror("エラー", "先に見積計算を行ってください。")
            return
        
        # 以前の画面をクリア
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # 確認画面の作成
        conf_frame = tk.Frame(self.root, padx=20, pady=20)
        conf_frame.pack(fill=tk.BOTH, expand=True)
        
        # 成功メッセージ
        success_label = tk.Label(conf_frame, 
                              text="見積もり送信完了！", 
                              font=("Helvetica", 18, "bold"),
                              fg="#4CAF50")
        success_label.pack(pady=20)
        
        # メール送信成功メッセージ
        details_label = tk.Label(conf_frame, 
                              text=f"{self.sent_email} 宛にメールで見積もりが送信されました。",
                              font=("Helvetica", 12))
        details_label.pack(pady=10)
        
        # JSONファイル保存成功メッセージ
        if json_filepath:
            json_label = tk.Label(conf_frame,
                               text=f"見積書データが {os.path.basename(json_filepath)} に保存されました。",
                               font=("Helvetica", 12))
            json_label.pack(pady=10)
        
        # メニューに戻るボタン
        return_btn = tk.Button(conf_frame, 
                            text="メニューに戻る", 
                            command=self.create_menu_screen,
                            bg="#2196F3", fg="white",
                            width=20, height=2)
        return_btn.pack(pady=20)
        
    def create_menu_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        Menu(self.root)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = HotelManagementSystem(root)
    root.mainloop()





















