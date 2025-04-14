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

class HotelManagementSystem2(tk.Frame):
    def __init__(self, root):
        super().__init__(root)  # 基底クラスの初期化
        self.root = root
        self.root.title("ホテル管理システム")
        self.root.geometry("1000x700")

        # フレームを正しく表示
        self.pack(fill=tk.BOTH, expand=True)

        # 他の初期化処理
        self.quotes_dir = "quotes"
        if not os.path.exists(self.quotes_dir):
            os.makedirs(self.quotes_dir)

        self.load_pricing_data()
        self.show_quote_screen()

        # メール設定を固定値に設定（メール設定画面を削除）
        self.email_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "y.mukaiguchi.sys24@morijyobi.ac.jp",
            "password": "iioy yrtg hxff eknq",
            "sender": "y.mukaiguchi.sys24@morijyobi.ac.jp"
        }
        
    # 料金データの読み込み
    def load_pricing_data(self):
        self.pricing = {
            "room_types": {
                "豪華コース": 21600,
                "雅コース": 18600,
                "錦コース": 15800,
                "椿コース": 21600,
            },
            "meal_plan": {
                "八幡平牛ロースのしゃぶしゃぶ": 4000,
                "大更ホルモン鍋": 1100,
                "岩手県産牛の串焼き": 750,
                "飲み放題": 2800,
            },
            "child_price": 7200,
            "early_booking_discount": {
                60: 0.10,
                90: 0.15,
            },
            "saturday_surcharge": 2000
        }

    def show_quote_screen(self):
        # 現在のウィジェットをすべて削除
        for widget in self.winfo_children():
            widget.destroy()

        # タイトル
        title_label = tk.Label(self, text="宴会見積画面", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)

        # メインフレーム作成（スクロール可能なコンテンツ用）
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=300, pady=20)

        # Canvas作成
        self.canvas = tk.Canvas(main_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        

        # スクロールバーの作成と設定
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # CanvasとScrollbarを連動
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # スクロール可能なフレームをCanvas内に作成
        content_frame = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=content_frame, anchor="n", width=self.canvas.winfo_width())

        # Canvasのサイズが変更されたときにウィンドウサイズも調整
        def _configure_canvas(event):
            if content_frame.winfo_reqheight() > event.height:
                # コンテンツが縦に大きい場合はスクロール領域を設定
                self.canvas.itemconfigure(self.canvas_window, width=event.width - 5)
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            else:
                # コンテンツが小さい場合はスクロールバーを表示しない
                self.canvas.itemconfigure(self.canvas_window, width=event.width - 5)
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.canvas.bind('<Configure>', _configure_canvas)

        # マウスホイールでスクロール
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        
        # お客様情報フレーム
        customer_frame = tk.LabelFrame(content_frame, text="お客様情報", padx=10, pady=10)
        customer_frame.pack(fill=tk.X, pady=10)

        # グリッドレイアウトのお客様情報
        customer_grid = tk.Frame(customer_frame)
        customer_grid.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(customer_grid, text="お名前:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.customer_name = tk.Entry(customer_grid, width=30)
        self.customer_name.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        tk.Label(customer_grid, text="電話番号:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.customer_phone = tk.Entry(customer_grid, width=30)
        self.customer_phone.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        tk.Label(customer_grid, text="メール:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.customer_email = tk.Entry(customer_grid, width=30)
        self.customer_email.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)

        # 予約詳細フレーム
        res_frame = tk.LabelFrame(content_frame, text="予約詳細", padx=10, pady=10)
        res_frame.pack(fill=tk.X, pady=10)

        # 予約内容のグリッド
        res_grid = tk.Frame(res_frame)
        res_grid.pack(fill=tk.X, padx=5, pady=5)

        # チェックイン/チェックアウト日
        date_frame = tk.Frame(res_grid)
        date_frame.grid(row=0, column=0, columnspan=4, sticky=tk.W, padx=5, pady=5)

        tk.Label(date_frame, text="チェックイン日:").grid(row=0, column=0, padx=5, pady=5)
        self.checkin_date = tk.Entry(date_frame, width=15)
        self.checkin_date.grid(row=0, column=1, padx=5, pady=5)
        self.checkin_date.insert(0, datetime.datetime.now().strftime("%Y/%m/%d"))


        # 部屋タイプ
        room_frame = tk.Frame(res_grid)
        room_frame.grid(row=1, column=0, columnspan=4, sticky=tk.W, padx=5, pady=5)

        tk.Label(room_frame, text="宴会コース:").grid(row=0, column=0, padx=5, pady=5)
        self.room_type = tk.StringVar()
        room_type_combo = ttk.Combobox(room_frame, textvariable=self.room_type, width=15)
        room_type_combo["values"] = list(self.pricing["room_types"].keys())
        room_type_combo.grid(row=0, column=1, padx=5, pady=5)
        room_type_combo.current(0)

        # 食事プラン
        meal_frame = tk.Frame(res_grid)
        meal_frame.grid(row=2, column=0, columnspan=4, sticky=tk.W, padx=5, pady=5)

        tk.Label(meal_frame, text="追加料金:").grid(row=0, column=0, padx=5, pady=5)
        self.meal_options = list(self.pricing["meal_plan"].keys())
        self.meal_vars = [tk.BooleanVar() for _ in self.meal_options]
        
        # 食事プランのチェックボックスを2列に配置
        for i, meal in enumerate(self.meal_options):
            row = i // 2  # 2列に分ける
            col = i % 2 + 1  # 1列目はラベル用なので+1
            tk.Checkbutton(meal_frame, text=meal, variable=self.meal_vars[i]).grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)

        # 人数
        people_frame = tk.Frame(res_grid)
        people_frame.grid(row=3, column=0, columnspan=4, sticky=tk.W, padx=5, pady=5)

        tk.Label(people_frame, text="大人:").grid(row=0, column=0, padx=5, pady=5)
        self.num_adults = ttk.Spinbox(people_frame, from_=1, to=10, width=5)
        self.num_adults.set(2)
        self.num_adults.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(people_frame, text="子供:").grid(row=0, column=2, padx=5, pady=5)
        self.num_children = ttk.Spinbox(people_frame, from_=0, to=10, width=5)
        self.num_children.set(0)
        self.num_children.grid(row=0, column=3, padx=5, pady=5)

        # 計算ボタン
        calculate_btn = tk.Button(content_frame, text="料金計算", command=self.calculate_quote, bg="#4CAF50", fg="white", width=20, height=2)
        calculate_btn.pack(pady=10)

        # 結果表示
        results_frame = tk.LabelFrame(content_frame, text="見積結果", padx=10, pady=10)
        results_frame.pack(fill=tk.X, pady=10)

        self.results_text = tk.Text(results_frame, height=10, width=80, state="disabled")
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
        try:
            room_type = self.room_type.get()
            num_adults = int(self.num_adults.get())
            num_children = int(self.num_children.get())
            checkin = datetime.datetime.strptime(self.checkin_date.get(), "%Y/%m/%d")

            base_cost_per_adult = self.pricing["room_types"][room_type]
            child_cost = self.pricing["child_price"]

            meal_plan_cost = sum(
                self.pricing["meal_plan"][meal] for i, meal in enumerate(self.meal_options) if self.meal_vars[i].get()
            )

            today = datetime.datetime.today()
            days_until_checkin = (checkin - today).days
            discount_rate = 0
            if days_until_checkin >= 90:
                discount_rate = self.pricing["early_booking_discount"][90]
            elif days_until_checkin >= 60:
                discount_rate = self.pricing["early_booking_discount"][60]


            while True:
                try:
                    today_str = self.checkin_date.get()  # 文字列型の日付を取得
                    print(f"入力された日付（文字列）: {today_str}")  # デバッグ用出力

                    # 文字列型を datetime.date 型に変換
                    today = datetime.datetime.strptime(today_str, "%Y/%m/%d").date()
                    print(f"今日の日付: {today}, 曜日: {today.weekday()}")  # 日付と曜日を表示

                    # 土曜日判定
                    if today.weekday() == 5:  # 土曜日の場合
                        saturday_surcharge = 2000
                        print("土曜日料金: 2000円")
                    else:
                        saturday_surcharge = 0
                        print("土曜日料金: 0円")

                    # 正常に処理が完了したらループ終了
                    break
                except ValueError:
                    # 日付形式が正しくない場合
                    print("正しい日付形式（YYYY/MM/DD）で入力してください。")
                    break


            adult_cost = (base_cost_per_adult + meal_plan_cost) * num_adults
            children_cost = child_cost * num_children
            total_before_discount = adult_cost + children_cost + saturday_surcharge
            discount_amount = total_before_discount * discount_rate
            total_after_discount = total_before_discount - discount_amount
            



            result = f"見積詳細:\n\n部屋タイプ: {room_type}\n"
            result += f"大人: {num_adults}人 × ({base_cost_per_adult:,}円 + 追加料金 {meal_plan_cost:,}円)\n"
            if num_children > 0:
                result += f"子供: {num_children}人 × {child_cost:,}円\n"
            if saturday_surcharge > 0:
                result += f"土曜日追加料金: {saturday_surcharge:,}円\n"

            result += f"\n小計: {total_before_discount:,}円\n"

            if discount_rate > 0:
                result += f"早期予約割引 ({discount_rate*100:.0f}%): -{discount_amount:,}円\n"

            result += f"\n合計: {total_after_discount:,}円 (税込)"

            # 結果をテキストウィジェットに表示
            self.results_text.configure(state="normal")
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, result)
            self.results_text.configure(state="disabled")
            
            self.quote_result = result
            
            self.quote_details = {
                "customer": {
                    "name": self.customer_name.get(),
                    "email": self.customer_email.get(),
                    "phone": self.customer_phone.get()
                },
                "reservation": {
                    "room_type": room_type,
                    "meal_plan": meal_plan_cost,
                    "checkin": checkin.strftime("%Y-%m-%d"),
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
            msg['Subject'] = f"【ホテル予約】{self.customer_name.get()} 様 宴会見積"
              
            # メール本文の作成
            body = f"""
{self.customer_name.get()} 様

この度はお問い合わせいただき、誠にありがとうございます。
ご希望の宴会プランの見積をお送りいたします。

====================
{self.quote_result}
====================

ご予約やご質問がございましたら、お気軽にお問い合わせください。
お客様のご来館を心よりお待ちしております。

--
八幡平ハイツ
TEL: 0195-78-2121
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
        for widget in self.winfo_children():
            widget.destroy()
            
        # 確認画面の作成
        conf_frame = tk.Frame(self, padx=20, pady=20)
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
        for widget in self.winfo_children():
            widget.destroy()
        Menu(self.root)

# メニュークラスが不明な場合に備えて簡易実装
class SimpleMenu(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.pack(fill=tk.BOTH, expand=True)
        tk.Label(self, text="メニュー画面", font=("Helvetica", 16, "bold")).pack(pady=20)
        tk.Button(self, text="見積作成に戻る", command=self.return_to_quote).pack(pady=10)
    
    def return_to_quote(self):
        for widget in self.winfo_children():
            widget.destroy()
        HotelManagementSystem2(self.root)
        
if __name__ == "__main__":
    root = tk.Tk()  # 親ウィジェットを作成
    app = HotelManagementSystem2(root)  # 親ウィジェットを渡して初期化
    root.mainloop()  # メインループを開始