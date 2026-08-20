from querys import get_company_name
from querys import get_stock_history_with_ticker
import tkinter
from tkinter import messagebox

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox
from setup_database import * 
from querys import *
from otp_management import *
from login import *
from add_in_a_ticker import *
from assess_sentiment_with_news import *
from stock_data_pulling import *
from attempt_at_password_hashing import *

def build_candelstick_dataframe(rows):
        df = pd.DataFrame(
            rows,
            columns=["Date", "Open", "High", "Low", "Close", "Volume"],
        )

        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)
        df.index = pd.DatetimeIndex(df.index)

        df = df.astype(
            {
                "Open": float,
                "High": float,
                "Low": float,
                "Close": float,
                "Volume": float,
            }
        )

        return df.sort_index()

class App(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stock Alert System")
        self.geometry("1280x720")
        self.resizable(False, False)
        
        self.current_user = None
        
        self.frames = {}
        
        container = tkinter.Frame(self)
        container.pack(fill="both", expand=True)

        for F in (StartMenu, LoginPage, RegisterPage, ForgotPasswordPage1, ForgotPasswordPage2, ForgotPasswordPage3, OTPPage, MenuPage, ViewStockDataPage, AddTickerPage, StockSentimentPage, ViewWatchlistPage):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("StartMenu")
    
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()

class StartMenu(tkinter.Frame):
    def __init__(self, parent, app: App):
        setup_database_main()

        super().__init__(parent)
        
        tkinter.Label(self, text="Stock Alert System", font=("Arial", 24, "bold")).pack(pady=20)
        tkinter.Label(self, text="Welcome to the Stock Alert System", font=("Arial", 16)).pack(pady=10)
    
        btns = tkinter.Frame(self)
        btns.pack(pady=15)
        
        tkinter.Button(btns, text="Log In", width=18, command=lambda: app.show_frame("LoginPage")).grid(row=0, column=0, padx=8, pady=8)
        tkinter.Button(btns, text="Register", width=18, command=lambda: app.show_frame("RegisterPage")).grid(row=1, column=0, padx=8, pady=8)
        tkinter.Button(btns, text="Forgot Password", width = 18, command=lambda: app.show_frame("ForgotPasswordPage1")).grid(row=2, column=0, padx=8, pady=8)
        tkinter.Button(btns, text="Exit", width=18, command=app.quit).grid(row=3, column=0, padx=8, pady=8)

class LoginPage(tkinter.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent)

        tkinter.Label(self, text="Log In", font=("Arial", 24, "bold")).pack(pady=20)
        
        form = tkinter.Frame(self)
        form.pack(pady=8, padx=8)

        tkinter.Label(form, text="Email").grid(row=0, column=0, sticky="e", padx=8, pady=6)
        tkinter.Label(form, text="Password:").grid(row=1, column=0, sticky="e", padx=8, pady=6)

        self.email_var = tkinter.StringVar()
        self.pw_var = tkinter.StringVar()
        
        email_entry = tkinter.Entry(form, textvariable=self.email_var, width=28)
        pw_entry = tkinter.Entry(form, textvariable=self.pw_var, show="*", width=28)
        
        email_entry.grid(row=0, column=1, padx=8, pady=6)
        pw_entry.grid(row=1, column=1, padx=8, pady=6)
        
        btns = tkinter.Frame(self)
        btns.pack(pady=15)
        
        tkinter.Button(btns, text="Back", width=18, command=lambda: app.show_frame("StartMenu")).grid(row=0, column=0, padx=8, pady=6)
        tkinter.Button(btns, text="Log In", width=18, command=self.do_login).grid(row=0, column=1, padx=8, pady=6)

    def do_login(self):
        raw_email = self.email_var.get()
        raw_password = self.pw_var.get()

        ok = sql_login(raw_email, raw_password)
        if ok:
            messagebox.showinfo("Success", "Login successful")
            self.email_var.set("")
            self.pw_var.set("")
            app.current_user = raw_email
            print(f"self.key_var is {app.current_user}")
            # Access OTPPage instance and send OTP
            otp_page = app.frames["OTPPage"]
            otp_page.send_otp()
            app.show_frame("OTPPage")
        else:
            messagebox.showerror("Error", "Invalid email or password")

class RegisterPage(tkinter.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent)

        tkinter.Label(self, text="Register", font=("Arial", 24, "bold")).pack(pady=20)
        
        form = tkinter.Frame(self)
        form.pack(pady=8, padx=8)

        tkinter.Label(form, text="Email").grid(row=0, column=0, sticky="e", padx=8, pady=6)
        tkinter.Label(form, text="Password:").grid(row=1, column=0, sticky="e", padx=8, pady=6)

        self.email_var = tkinter.StringVar()
        self.pw_var = tkinter.StringVar()

        email_entry = tkinter.Entry(form, textvariable=self.email_var, width=28)
        pw_entry = tkinter.Entry(form, textvariable=self.pw_var, show="*", width=28)
        
        email_entry.grid(row=0, column=1, padx=8, pady=6)
        pw_entry.grid(row=1, column=1, padx=8, pady=6)
        
        btns = tkinter.Frame(self)
        btns.pack(pady=15)
        
        tkinter.Button(btns, text="Back", width=18, command=lambda: app.show_frame("StartMenu")).grid(row=0, column=0, padx=8, pady=6)
        tkinter.Button(btns, text="Register", width=18, command=self.do_register).grid(row=0, column=1, padx=8, pady=6)

    def do_register(self):
        raw_email = self.email_var.get()
        raw_password = self.pw_var.get()

        app.current_user = self.email_var.get()

        if check_if_user_registered(raw_email):
            messagebox.showerror("Error", "User already registered")
            self.email_var.set("")
            self.pw_var.set("")
            app.show_frame("LoginPage")
            return
        
        password_hash = hash_password(raw_password) #[salt, hashed_password]
        salt = password_hash[0]
        hashed_password = password_hash[1]

        ok = sql_register(raw_email, hashed_password, salt)
        if ok:
            messagebox.showinfo("Success", "Registration successful")
            app.current_user = raw_email
            self.email_var.set("")
            self.pw_var.set("")
            app.show_frame("OTPPage")
            otp_page = app.frames["OTPPage"]
            otp_page.send_otp()
        else:
            messagebox.showerror("Error", "Registration failed")

class ForgotPasswordPage1(tkinter.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent)
        
        self.app = app
        self.app.current_user = None

        tkinter.Label(self, text="Forgot Password", font=("Arial", 24, "bold")).pack(pady=20)

        form = tkinter.Frame(self)
        form.pack(pady=8, padx=8)

        tkinter.Label(form, text="Email").grid(row=0, column=0, sticky="e", padx=8, pady=6)

        self.user_email_var = tkinter.StringVar()


        user_email_entry = tkinter.Entry(form, textvariable=self.user_email_var, width=28)
        user_email_entry.grid(row=0, column=1, padx=8, pady=6)
        
        btns = tkinter.Frame(self)
        btns.pack(pady=15)
        
        tkinter.Button(btns, text="Back", width=18, command=lambda: app.show_frame("StartMenu")).grid(row=0, column=0, padx=8, pady=6)
        tkinter.Button(btns, text="Next", width=18, command=self.do_submit_email).grid(row=0, column=1, padx=8, pady=6)
        
    def do_submit_email(self):
        email = self.user_email_var.get()
        if not email:
            messagebox.showerror("Error", "Please enter an email address")
            return
            
        if not check_if_user_registered(email):
            messagebox.showerror("Error", "Email not found")
            return

        page2 = self.app.frames["ForgotPasswordPage2"]
        page2.current_email = email
        self.app.show_frame("ForgotPasswordPage2")

class ForgotPasswordPage2(tkinter.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent)
        self.app = app
        self.current_email = None
        self.generated_otp = None

        tkinter.Label(self, text="Forgot Password", font=("Arial", 24, "bold")).pack(pady=20)
        
        tkinter.Label(self, text="Enter OTP Code").pack(pady=6)

        self.otp_code_entry_var = tkinter.StringVar()
        otp_code_entry = tkinter.Entry(self, textvariable=self.otp_code_entry_var, width=28)
        otp_code_entry.pack(pady=6)

        btns = tkinter.Frame(self)
        btns.pack(pady=15)
        
        tkinter.Button(btns, text="Back", width=18, command=lambda: app.show_frame("ForgotPasswordPage1")).grid(row=0, column=0, padx=8, pady=6)
        tkinter.Button(btns, text="Verify", width=18, command=self.do_check_otp).grid(row=0, column=1, padx=8, pady=6)
        
    def on_show(self):
        if self.current_email:
            self.generated_otp = generate_otp(self.current_email)
            messagebox.showinfo("OTP Sent", f"An OTP has been sent to {self.current_email}")
        else:
            messagebox.showerror("Error", "No email provided. Returning to start.")
            self.app.show_frame("StartMenu")

    def do_check_otp(self):
        user_otp = self.otp_code_entry_var.get()
        if validate_otp(user_otp, self.generated_otp, self.current_email):
            page3 = self.app.frames["ForgotPasswordPage3"]
            page3.current_email = self.current_email
            self.app.show_frame("ForgotPasswordPage3")
        else:
            messagebox.showerror("Error", "Invalid OTP")

class ForgotPasswordPage3(tkinter.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent)
        self.app = app
        self.current_email = None

        tkinter.Label(self, text="Reset Password", font=("Arial", 24, "bold")).pack(pady=20)
        
        tkinter.Label(self, text="New Password").pack(pady=6)

        self.new_password_var = tkinter.StringVar()
        new_password_entry = tkinter.Entry(self, textvariable=self.new_password_var, show="*", width=28)
        new_password_entry.pack(pady=6)

        tkinter.Label(self, text="Confirm New Password").pack(pady=6)

        self.confirm_new_password_var = tkinter.StringVar()
        confirm_new_password_entry = tkinter.Entry(self, textvariable=self.confirm_new_password_var, show="*", width=28)
        confirm_new_password_entry.pack(pady=6)

        btns = tkinter.Frame(self)
        btns.pack(pady=15)
        
        tkinter.Button(btns, text="Back", width=18, command=lambda: app.show_frame("ForgotPasswordPage2")).grid(row=0, column=0, padx=8, pady=6)
        tkinter.Button(btns, text="Reset Password", width=18, command=self.do_reset_password).grid(row=0, column=1, padx=8, pady=6)
        
    def do_reset_password(self):
        new_pass = self.new_password_var.get()
        confirm_pass = self.confirm_new_password_var.get()
        
        if not new_pass or not confirm_pass:
            messagebox.showerror("Error", "Please fill in all fields")
            return
            
        if new_pass != confirm_pass:
            messagebox.showerror("Error", "Passwords do not match")
            return
            
        password_hash = hash_password(new_pass)
        salt = password_hash[0]
        hashed_password = password_hash[1]
        
        if update_password(self.current_email, hashed_password, salt):
            messagebox.showinfo("Success", "Password updated successfully!")
            self.new_password_var.set("")
            self.confirm_new_password_var.set("")
            self.app.show_frame("StartMenu")
        else:
            messagebox.showerror("Error", "Failed to update password in database")

class OTPPage(tkinter.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent)
        self.app = app
        self.generated_otp = None 
        self.key_var = None # Initialize key_var to store email

        tkinter.Label(self, text="OTP Page", font=("Arial", 24, "bold")).pack(pady=20)

        form = tkinter.Frame(self)
        form.pack(pady=8, padx=8)

        tkinter.Label(form, text="OTP").grid(row=0, column=0, sticky="e", padx=8, pady=6)

        self.otp_var = tkinter.StringVar()
        
        otp_entry = tkinter.Entry(form, textvariable=self.otp_var, width=28)
        otp_entry.grid(row=0, column=1, padx=8, pady=6)

        btns = tkinter.Frame(self)
        btns.pack(pady=15)
        
        tkinter.Button(btns, text="Back", width=18, command=lambda: app.show_frame("LoginPage")).grid(row=0, column=0, padx=8, pady=6)
        tkinter.Button(btns, text="Verify", width=18, command=self.do_otp).grid(row=0, column=1, padx=8, pady=6)
        tkinter.Button(btns, text="Resend OTP", width=18, command=lambda: self.send_otp(app.current_user)).grid(row=0, column=2, padx=8, pady=6)

    def send_otp(self):
        #print("function send_otp")
        #print(f"self.app.current_user is {self.app.current_user}")
        self.generated_otp = generate_otp(self.app.current_user)

    def do_otp(self):
        #print("function do_otp")
        #print(f"self.app.current_user is {self.app.current_user}")
        users_otp = self.otp_var.get()
        if validate_otp(users_otp, self.generated_otp, self.app.current_user):
            messagebox.showinfo("Success", "OTP Verified")
            self.otp_var.set("")
            self.app.show_frame("MenuPage") 
        else:
            messagebox.showerror("Error", "Invalid OTP")
        
class MenuPage(tkinter.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent)
        
        tkinter.Label(self, text="Menu Page", font=("Arial", 24, "bold")).pack(pady=20)
        
        tkinter.Label(self, text="Welcome to the Stock Alert System", font=("Arial", 16)).pack(pady=10)
        
        btns = tkinter.Frame(self)
        btns.pack(pady=15)
        
        tkinter.Button(btns, text="View the price of the stocks in your watchlist", width=30, command=lambda: app.show_frame("ViewStockDataPage")).grid(row=0, column=0, padx=8, pady=8)
        tkinter.Button(btns, text="View your watchlist", width=30, command=lambda: app.show_frame("ViewWatchlistPage")).grid(row=1, column=0, padx=8, pady=8)
        tkinter.Button(btns, text="Add a Ticker to your watchlist", width=30, command=lambda: app.show_frame("AddTickerPage")).grid(row=2, column=0, padx=8, pady=8)
        tkinter.Button(btns, text="Assess the sentiment of a stock", width=30, command=lambda: app.show_frame("StockSentimentPage")).grid(row=3, column=0, padx=8, pady=8)
        tkinter.Button(btns, text="Exit", width=30, command=app.quit).grid(row=4, column=0, padx=8, pady=8)

class ViewStockDataPage(tkinter.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent)
        self.app = app

        tkinter.Label(self, text="View Stock Data", font=("Arial", 24, "bold")).pack(pady=20)

        self.ticker_var = tkinter.StringVar()

        ticker_entry = tkinter.Entry(self, textvariable=self.ticker_var, width=28)
        ticker_entry.pack(pady=6)

        btns = tkinter.Frame(self)
        btns.pack(pady=15)
        
        tkinter.Button(btns, text="Back", width=18, command=lambda: app.show_frame("MenuPage")).grid(row=0, column=0, padx=8, pady=6)
        tkinter.Button(btns, text="View Stock Data", width=18, command=self.do_view_stock_data).grid(row=0, column=1, padx=8, pady=6)


    def do_view_stock_data(self):
        fetch_stock_data()

        ticker = self.ticker_var.get().strip().upper()

        if not ticker:
            messagebox.showerror("Error", "Please enter a valid ticker.")
            return
        
        rows = get_stock_history_with_ticker(
            ticker,
            self.app.current_user,
            limit=60
        )

        if not rows:
            messagebox.showerror(
                "Error",
                (
                    "No historical data found for this ticker, or it is not in "
                    "your watchlist."
                )
            )
            return

        try:
            df = build_candelstick_dataframe(rows)
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to prepare chart data:\n{e}",
            )

        popup = tkinter.Toplevel(self)
        popup.title(f"Candelstick Chart for {ticker}")
        popup.geometry("1000x700")
        popup.resizable(True, True)

        company_name = get_company_name(ticker) or "Unknown Company"

        tkinter.Label(
            popup,
            text=f"{ticker} - {company_name}",
            font=("Arial", 18, "bold")
        ).pack(pady=10)

        try:
            fig, _ = mpf.plot(
                df,
                type="candle",
                style="yahoo",
                volume=True,
                mav=(5, 10, 20),
                ylabel="Price",
                ylabel_lower="Volume",
                datetime_format="%d %b %Y",
                xrotation=15,
                returnfig=True,
            )
        except Exception as e:
            popup.destroy()
            messagebox.showerror(
                "Error",
                f"Failed to create candlestick chart:\n{e}"
            )
            return

        canvas = FigureCanvasTkAgg(fig, master=popup)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        def close_chart():
            plt.close(fig)
            popup.destroy()

        popup.protocol("WM_DELETE_WINDOW", close_chart)

        tkinter.Button(
            popup,
            text="Close",
            command=close_chart,
            width=12
        ).pack(pady=10)

class AddTickerPage(tkinter.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent)
        self.app = app
        # self.key_var is no longer needed from parent, we use app.current_user

        tkinter.Label(self, text="Add Ticker", font=("Arial", 24, "bold")).pack(pady=20)
        
        tkinter.Label(self, text="Ticker:").pack(pady=6)
        
        self.ticker_var = tkinter.StringVar()
        
        ticker_entry = tkinter.Entry(self, textvariable=self.ticker_var, width=28)
        ticker_entry.pack(pady=6)
        
        btns = tkinter.Frame(self)
        btns.pack(pady=15)
        
        tkinter.Button(btns, text="Back", width=18, command=lambda: app.show_frame("MenuPage")).grid(row=0, column=0, padx=8, pady=6)
        tkinter.Button(btns, text="Add", width=18, command=self.do_add_ticker).grid(row=0, column=1, padx=8, pady=6)

    def do_add_ticker(self):
        ticker = self.ticker_var.get().upper()
        email = self.app.current_user
        
        if not email:
            messagebox.showerror("Error", "User not logged in or session expired.")
            return

        if ticker:
            # First ensure ticker exists in symbol table
            add_ticker(ticker) 
            # Then link to user
            success = link_user_to_ticker(email, ticker)
            
            if success:
                self.ticker_var.set("")
                messagebox.showinfo(f"Success", f"Ticker {ticker} added successfully to your watchlist")
            else:
                messagebox.showerror("Error", f"Failed to add {ticker} to watchlist.")
        else:
            messagebox.showerror("Error", "Please enter a valid ticker")

class StockSentimentPage(tkinter.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent)

        tkinter.Label(self, text="Stock Sentiment", font=("Arial", 24, "bold")).pack(pady=20)
        
        tkinter.Label(self, text="Ticker:").pack(pady=6)
        
        self.ticker_var = tkinter.StringVar()
        
        ticker_entry = tkinter.Entry(self, textvariable=self.ticker_var, width=28)
        ticker_entry.pack(pady=6)
        
        btns = tkinter.Frame(self)
        btns.pack(pady=15)
        
        tkinter.Button(btns, text="Back", width=18, command=lambda: app.show_frame("MenuPage")).grid(row=0, column=0, padx=8, pady=6)
        tkinter.Button(btns, text="Assess", width=18, command=self.do_assess_sentiment).grid(row=0, column=1, padx=8, pady=6)

    def do_assess_sentiment(self):
        ticker = self.ticker_var.get().upper()
        if ticker:
            result = assess_sentiment(ticker)
            sentiment_score = result[0]
            sentiment_label = result[1]
            news_list = result[2]
            
            self.ticker_var.set("")
            
            popup = tkinter.Toplevel(self)
            popup.title(f"Sentiment Assessment for {ticker}")
            popup.geometry("600x600")
            
            tkinter.Label(popup, text=f"Sentiment Assessment for {ticker}", font=("Arial", 22, "bold")).pack(pady=10)
            
            company_name = get_company_name(ticker)
            tkinter.Label(popup, text=company_name, font=("Arial", 14, "italic")).pack(pady=0)
            
            sentiment_frame = tkinter.Frame(popup)
            sentiment_frame.pack(pady=15)
            
            tkinter.Label(sentiment_frame, text=f"Sentiment Score: {sentiment_score:.2f}", font=("Arial", 14)).pack(anchor="w")
            tkinter.Label(sentiment_frame, text=f"Sentiment: {sentiment_label}", font=("Arial", 14, "bold")).pack(anchor="w")

            tkinter.Label(popup, text="Latest News:", font=("Arial", 12, "bold")).pack(pady=(10, 5), anchor="w", padx=20)
            
            from tkinter.scrolledtext import ScrolledText
            news_text = ScrolledText(popup, width=70, height=20, font=("Arial", 10))
            news_text.pack(pady=5, padx=20, fill="both", expand=True)
            
            if news_list:
                for item in news_list:
                    # item structure: {'title':..., 'publisher':..., 'publish_date':..., 'link':...}
                    title = item.get('title', 'No Title')
                    publisher = item.get('publisher', 'Unknown')
                    date = item.get('publish_date', 'Unknown Date')
                    link = item.get('link', 'No Link')
                    
                    news_text.insert(tkinter.END, f"â¢ {title}\n")
                    news_text.insert(tkinter.END, f"  Source: {publisher} | Date: {date}\n")
                    news_text.insert(tkinter.END, f"  Link: {link}\n")
                    news_text.insert(tkinter.END, "-"*120 + "\n\n")
            else:
                news_text.insert(tkinter.END, "No recent news found.\n")
                
            news_text.configure(state='disabled')
            
            btn = tkinter.Button(popup, text="OK", command=popup.destroy, width=10)
            btn.pack(pady=10)        
        else:
            messagebox.showerror("Error", "Please enter a valid ticker")

class ViewWatchlistPage(tkinter.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent)
        self.app = app
        
        tkinter.Label(self, text="My Watchlist", font=("Arial", 24, "bold")).pack(pady=20)
        
        self.list_container = tkinter.Frame(self)
        self.list_container.pack(fill="both", expand=True, padx=20, pady=10)

        btns = tkinter.Frame(self)
        btns.pack(pady=15, side="bottom")
    
        tkinter.Button(btns, text="Back", width=18, command=lambda: app.show_frame("MenuPage")).grid(row=0, column=0, padx=8, pady=6)
        tkinter.Button(btns, text="Add Ticker", width=18, command=lambda: app.show_frame("AddTickerPage")).grid(row=0, column=1, padx=8, pady=6)

    def on_show(self):
        for widget in self.list_container.winfo_children():
            widget.destroy()
            
        if not self.app.current_user:
            tkinter.Label(self.list_container, text="Please log in to view watchlist.", font=("Arial", 14), fg="red").pack()
            return

        user_symbolids = get_user_symbolids(self.app.current_user)
        user_ticker_company = get_ticker_company_from_symbol_id(user_symbolids)
        
        if not user_ticker_company:
            tkinter.Label(self.list_container, text="Your watchlist is empty.", font=("Arial", 14, "italic")).pack(pady=10)
        else:
            main_frame = tkinter.Frame(self.list_container)
            main_frame.pack(fill="both", expand=True)

            canvas = tkinter.Canvas(main_frame)
            canvas.pack(side="left", fill="both", expand=True)

            scrollbar = tkinter.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollbar.pack(side="right", fill="y")

            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

            second_frame = tkinter.Frame(canvas)

            canvas.create_window((0,0), window=second_frame, anchor="nw")

            for ticker, company in user_ticker_company:
                item_frame = tkinter.Frame(second_frame, relief="groove", borderwidth=1)
                item_frame.pack(fill="x", pady=2)
                tkinter.Label(item_frame, text=f"{ticker}", font=("Arial", 14, "bold"), width=10, anchor="w").pack(side="left", padx=10)
                tkinter.Label(item_frame, text=f"{company}", font=("Arial", 12), anchor="w").pack(side="left", padx=10)
    

if __name__ == "__main__":
    app = App()
    app.mainloop()