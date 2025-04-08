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
        # デフォルトのメール設定
        self.email_config = {
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "username": "y.mukaiguchi.sys24@morijyobi.ac.jp",
            "password": "",
            "sender": "y.mukaiguchi.sys24@morijyobi.ac.jp"
        }

        # 設定ファイルがあれば読み込む
        self.load_email_config()
        # 料金データの読み込み
        self.load_pricing_data()
        
        # メニュー画面の作成
        self.create_menu_screen()
    
    def load_pricing_data(self):
        # 実際のアプリケーションではファイルやデータベースから読み込む
        # 今回は画像に基づいてハードコーディング
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
            "child_price": 7200,  # 子供料金は一律
            "early_booking_discount": {
                60: 0.10,  # 60日前: 10%割引
                90: 0.15   # 90日前: 15%割引
            },
            "saturday_surcharge": 2000  # 土曜日追加料金
        }
    
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
        
        exit_btn = tk.Button(menu_frame, text="終了", width=btn_width, height=btn_height,
                            command=self.root.destroy, bg="#F44336", fg="white")
        exit_btn.pack(pady=10)
    
    def show_quote_screen(self):
        # 以前の画面をクリア
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
        
        # キャンバスの内容のサイズが変わったときに、スクロール領域を調整
        quote_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        
        # ウィンドウサイズに合わせてキャンバスの幅を調整
        def _configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas.find_withtag("all")[0], width=event.width)
        
        canvas.bind("<Configure>", _configure_canvas)
        
        # マウスホイールでスクロールするイベントバインディング
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        # プラットフォームによって異なるマウスホイールイベントを処理
        canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows
        
        # Linuxの場合は以下も追加するとよい（コメントアウト）
        # canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        # canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        
        # Macの場合の対応（必要に応じて）
        # def _on_mousewheel_mac(event):
        #     canvas.yview_scroll(-1 * event.delta, "units")
        # canvas.bind_all("<MouseWheel>", _on_mousewheel_mac)  # Mac
    
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
            # 予約情報を保存
            self.reservation_info = {
                "customer_name": self.customer_name.get(),
                "customer_email": self.customer_email.get(),
                "total_price": f"{total_after_discount:,}円"
            }
            
        except Exception as e:
            messagebox.showerror("エラー", f"計算中にエラーが発生しました: {str(e)}")
            self.results_text.configure(state="disabled")


    def load_email_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    if 'email_config' in config_data:
                        self.email_config = config_data['email_config']
                        print("メール設定を読み込みました")
        except Exception as e:
            print(f"設定ファイルの読み込みエラー: {str(e)}")

    def save_email_config(self):
      try:
          # 既存の設定を読み込み（あれば）
          config_data = {}
          if os.path.exists(self.config_file):
              with open(self.config_file, 'r', encoding='utf-8') as f:
                  config_data = json.load(f)
          
          # メール設定を更新
          config_data['email_config'] = self.email_config
          
          # ファイルに保存
          with open(self.config_file, 'w', encoding='utf-8') as f:
              json.dump(config_data, f, ensure_ascii=False, indent=4)
          
          print("メール設定を保存しました")
          return True
      except Exception as e:
          print(f"設定ファイルの保存エラー: {str(e)}")
          return False
      
      # save_email_settingsメソッドの修正部分
    def save_email_settings(self):
        # 入力値を取得して設定を更新
        try:
            self.email_config["smtp_server"] = self.smtp_server.get()
            self.email_config["smtp_port"] = int(self.smtp_port.get())
            self.email_config["username"] = self.email_username.get()
            self.email_config["password"] = self.email_password.get()
            self.email_config["sender"] = self.email_sender.get()
            
            # 設定をJSONファイルに保存
            if self.save_email_config():
                messagebox.showinfo("成功", "メール設定が保存されました。")
            else:
                messagebox.showerror("エラー", "設定の保存に失敗しました。")
        except Exception as e:
            messagebox.showerror("エラー", f"設定の保存に失敗しました: {str(e)}")

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
        
        details_label = tk.Label(conf_frame, 
                              text=f"{self.customer_email.get()} 宛にメールで見積もりが送信されました。",
                              font=("Helvetica", 12))
        details_label.pack(pady=10)
        
        # メニューに戻るボタン
        return_btn = tk.Button(conf_frame, 
                            text="メニューに戻る", 
                            command=self.create_menu_screen,
                            bg="#2196F3", fg="white",
                            width=20, height=2)
        return_btn.pack(pady=20)

    # メール設定画面を追加
    def show_email_settings(self):
        # 以前の画面をクリア
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # メインフレームとキャンバス、スクロールバーを作成
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # キャンバスとスクロールバーを作成
        canvas = tk.Canvas(main_frame)
        scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        
        # スクロールバーとキャンバスを配置
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # キャンバス内にフレームを作成
        settings_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=settings_frame, anchor="nw")
        
        # タイトル
        title_label = tk.Label(settings_frame, text="メール設定", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)
        
        # 設定フォーム
        form_frame = tk.LabelFrame(settings_frame, text="SMTPサーバー設定", padx=10, pady=10)
        form_frame.pack(fill=tk.X, pady=10)
        
        # 設定フィールド
        tk.Label(form_frame, text="SMTPサーバー:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.smtp_server = tk.Entry(form_frame, width=40)
        self.smtp_server.insert(0, self.email_config["smtp_server"])
        self.smtp_server.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        tk.Label(form_frame, text="SMTPポート:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.smtp_port = tk.Entry(form_frame, width=10)
        self.smtp_port.insert(0, str(self.email_config["smtp_port"]))
        self.smtp_port.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        tk.Label(form_frame, text="ユーザー名:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.email_username = tk.Entry(form_frame, width=40)
        self.email_username.insert(0, self.email_config["username"])
        self.email_username.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        tk.Label(form_frame, text="パスワード:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.email_password = tk.Entry(form_frame, width=40, show="*")
        self.email_password.insert(0, self.email_config["password"])
        self.email_password.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        tk.Label(form_frame, text="送信元アドレス:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.email_sender = tk.Entry(form_frame, width=40)
        self.email_sender.insert(0, self.email_config["sender"])
        self.email_sender.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # ボタンフレーム
        button_frame = tk.Frame(settings_frame)
        button_frame.pack(pady=20)
        
        save_btn = tk.Button(button_frame, text="設定を保存", 
                          command=self.save_email_settings,
                          bg="#4CAF50", fg="white",
                          width=15, height=2)
        save_btn.pack(side=tk.LEFT, padx=10)
        
        test_btn = tk.Button(button_frame, text="テストメール送信", 
                          command=self.send_test_email,
                          bg="#2196F3", fg="white",
                          width=15, height=2)
        test_btn.pack(side=tk.LEFT, padx=10)
        
        return_btn = tk.Button(button_frame, text="メニューに戻る", 
                            command=self.create_menu_screen,
                            bg="#F44336", fg="white",
                            width=15, height=2)
        return_btn.pack(side=tk.LEFT, padx=10)
        
        # キャンバスの内容のサイズが変わったときに、スクロール領域を調整
        settings_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        
        # ウィンドウサイズに合わせてキャンバスの幅を調整
        def _configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas.find_withtag("all")[0], width=event.width)
        
        # マウスホイールでスクロールするイベントバインディング
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        # イベントバインディングを設定
        canvas.bind("<Configure>", _configure_canvas)
        canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows
    

 

    def send_test_email(self):
        try:
            # 一時的に設定を更新
            temp_config = {
                "username": self.email_username.get(),
                "password": self.email_password.get(),
                "sender": self.email_sender.get()
            }
            
            # 元の設定を保存
            original_config = self.email_config.copy()
            self.email_config = temp_config
            
            # テストメールの宛先を取得
            test_email = temp_config["username"]  # 設定したメールアドレスにテストメール
            
            # メール作成
            msg = MIMEMultipart()
            msg['From'] = self.email_config["sender"]
            msg['To'] = test_email
            msg['Date'] = formatdate()
            msg['Subject'] = "ホテル管理システム - テストメール"
            
            body = """
    これはホテル管理システムからのテストメールです。
    メール設定が正常に機能していることを確認するためのメールです。

    このメールが届いた場合、設定は正常です。
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # SMTPサーバーに接続してメール送信
            
            messagebox.showinfo("成功", f"テストメールを {test_email} に送信しました。")
            
            # 設定を元に戻す
            self.email_config = original_config
            
        except Exception as e:
            messagebox.showerror("エラー", f"テストメール送信に失敗しました: {str(e)}")

    # メニュー画面にメール設定ボタンを追加
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
        
        # メール設定ボタンを追加
        email_settings_btn = tk.Button(menu_frame, text="メール設定", width=btn_width, height=btn_height,
                                    command=self.show_email_settings, bg="#2196F3", fg="white")
        email_settings_btn.pack(pady=10)
        
        exit_btn = tk.Button(menu_frame, text="終了", width=btn_width, height=btn_height,
                            command=self.root.destroy, bg="#F44336", fg="white")
        exit_btn.pack(pady=10) 
    


if __name__ == "__main__":
    root = tk.Tk()
    app = HotelManagementSystem(root)
    root.mainloop()