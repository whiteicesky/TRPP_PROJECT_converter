# Импорт необходимых библиотек
import requests  # для работы с API
import customtkinter as ctk  # для создания графического интерфейса
from datetime import datetime, timedelta  # для работы с датами
import random  # используется для генерации исторических данных при отсутствии API
import matplotlib.pyplot as plt  # для построения графиков
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # для отображения графика в окне Tkinter

# Класс основного приложения
class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("1000x800")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Переменные состояния
        self.dark_mode = False
        self.language = "ru"
        self.canvas = None

        # Словарь с переводами на русский и английский
        self.strings = {
            "ru": {
                "from": "Из:", "to": "В:", "convert": "Конвертировать",
                "updated": "Обновлено", "swap": "↔", "error": "Ошибка ввода!",
                "refresh": "Обновить график", "no_data": "Не удалось загрузить данные\nПроверьте подключение к интернету",
                "theme": "☾ Тема", "lang": "🌍 Язык", "search": "Поиск валюты",
                "amount": "Количество", "date": "Дата", "rate": "Курс",
                "chart_title": "Курс {0} к {1} (30 дней)"
            },
            "en": {
                "from": "From:", "to": "To:", "convert": "Convert",
                "updated": "Updated", "swap": "↔", "error": "Invalid input!",
                "refresh": "Refresh Chart", "no_data": "Could not load data\nCheck internet connection",
                "theme": "☼ Theme", "lang": "🌍 Language", "search": "Search currency",
                "amount": "Amount", "date": "Date", "rate": "Rate",
                "chart_title": "{0} to {1} Exchange Rate (30 Days)"
            }
        }

        # API и поддерживаемые валюты
        self.API_KEY = "df8e90ea766cff275e9403f2"
        self.ALTERNATE_API = "https://api.exchangerate.host"
        self.CRYPTO_API = "https://api.coingecko.com/api/v3"

        # Список поддерживаемых валют и криптовалют
        self.currencies = [
            "USD", "EUR", "GBP", "RUB", "JPY", "CNY", "AUD", "CAD", "CHF", "NZD",
            "BRL", "INR", "ZAR", "MXN", "SGD", "HKD", "KRW", "TRY", "NOK", "SEK",
            "BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOGE", "LTC"
        ]

        self.exchange_rates = {}  # сюда будут загружены курсы
        self.last_update = None  # время последнего обновления

        # Загрузка курсов и интерфейса
        self.load_exchange_rates()
        self.setup_ui()
        self.plot_exchange_rate("USD", "EUR")  # отобразить график по умолчанию

    # Метод перевода строк
    def t(self, key):
        return self.strings[self.language].get(key, key)

    # Смена языка интерфейса
    def toggle_language(self):
        self.language = "en" if self.language == "ru" else "ru"
        self.update_labels()

    # Смена темы (светлая/тёмная)
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        ctk.set_appearance_mode("dark" if self.dark_mode else "light")
        self.update_labels()
        self.plot_exchange_rate(self.from_currency.get(), self.to_currency.get())

    # Обновление текста элементов интерфейса
    def update_labels(self):
        self.from_label.configure(text=self.t("from"))
        self.to_label.configure(text=self.t("to"))
        self.convert_button.configure(text=self.t("convert"))
        self.swap_button.configure(text=self.t("swap"))
        self.update_button.configure(text=self.t("refresh"))
        self.theme_button.configure(text=self.t("theme"))
        self.lang_button.configure(text=self.t("lang"))
        self.from_search_label.configure(text=self.t("search"))
        self.to_search_label.configure(text=self.t("search"))
        self.amount_label.configure(text=self.t("amount"))

    # Загрузка актуальных курсов валют и криптовалют
    def load_exchange_rates(self):
        try:
            res = requests.get(f"https://v6.exchangerate-api.com/v6/{self.API_KEY}/latest/USD").json()
            if res.get("result") == "success":
                self.exchange_rates = res["conversion_rates"]
                self.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                # Резервный API
                res = requests.get(f"{self.ALTERNATE_API}/latest?base=USD").json()
                if res.get("success"):
                    self.exchange_rates = res["rates"]
                    self.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Загрузка курсов криптовалют
            crypto_res = requests.get(
                f"{self.CRYPTO_API}/simple/price?ids=bitcoin,ethereum,binancecoin,ripple,cardano,solana,dogecoin,litecoin&vs_currencies=usd"
            ).json()
            crypto_map = {
                "bitcoin": "BTC", "ethereum": "ETH", "binancecoin": "BNB", "ripple": "XRP",
                "cardano": "ADA", "solana": "SOL", "dogecoin": "DOGE", "litecoin": "LTC"
            }
            for crypto, symbol in crypto_map.items():
                if crypto in crypto_res:
                    usd_rate = crypto_res[crypto]["usd"]
                    self.exchange_rates[symbol] = 1 / usd_rate if usd_rate != 0 else 1.0
        except:
            self.use_backup_rates()

    # Резервные (офлайн) курсы на случай отсутствия интернета
    def use_backup_rates(self):
        self.exchange_rates = {
            "USD": 1.0, "EUR": 0.93, "GBP": 0.80, "RUB": 90.0, "JPY": 150.0, "CNY": 7.20,
            "AUD": 1.50, "CAD": 1.35, "CHF": 0.90, "NZD": 1.65, "BRL": 5.20, "INR": 83.0,
            "ZAR": 18.5, "MXN": 17.0, "SGD": 1.35, "HKD": 7.80, "KRW": 1350.0, "TRY": 32.0,
            "NOK": 10.5, "SEK": 10.8, "BTC": 0.000014, "ETH": 0.00027, "BNB": 0.0015,
            "XRP": 1.92, "ADA": 2.22, "SOL": 0.006, "DOGE": 6.25, "LTC": 0.012
        }
        self.last_update = "offline"

    # Метод конвертации валют
    def convert_currency(self):
        try:
            from_curr = self.from_currency.get()
            to_curr = self.to_currency.get()
            amount = float(self.amount_entry.get())
            usd = amount / self.exchange_rates[from_curr]
            result = usd * self.exchange_rates[to_curr]
            self.result_label.configure(
                text=f"{amount:.2f} {from_curr} = {result:.2f} {to_curr}\n({self.t('updated')}: {self.last_update})"
            )
            self.plot_exchange_rate(from_curr, to_curr)
        except:
            self.result_label.configure(text=self.t("error"))

    # Метод обмена валют местами
    def swap_currencies(self):
        f, t = self.from_currency.get(), self.to_currency.get()
        self.from_currency.set(t)
        self.to_currency.set(f)
        self.plot_exchange_rate(t, f)

    # Поиск валюты в списке
    def search_currency(self, event, var, menu):
        search_term = event.widget.get().upper()
        filtered = [c for c in self.currencies if search_term in c]
        menu.configure(values=filtered if filtered else self.currencies)
        if filtered and var.get() not in filtered:
            var.set(filtered[0])

    # Генерация фиктивных исторических данных (при отсутствии API)
    def fetch_historical_data(self, from_curr, to_curr):
        try:
            dates = [datetime.now().strftime("%Y-%m-%d")]
            rates = [self.exchange_rates[to_curr] / self.exchange_rates[from_curr]]
            for i in range(1, 30):
                dates.append((datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"))
                rates.append(rates[-1] * (1 + (random.uniform(-0.02, 0.02))))
            return dates[::-1], rates[::-1]
        except:
            return None, None

    # Очистка старого графика
    def clear_chart(self):
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

    # Построение графика курса валют
    def plot_exchange_rate(self, from_curr, to_curr):
        self.clear_chart()
        dates, rates = self.fetch_historical_data(from_curr, to_curr)
        if not dates or not rates:
            self.result_label.configure(text=self.t("no_data"))
            return

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(dates, rates, marker='o', linestyle='-', color='#1f77b4')
        ax.set_title(self.t("chart_title").format(from_curr, to_curr))
        ax.set_xlabel(self.t("date"))
        ax.set_ylabel(self.t("rate"))
        ax.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()

        if self.dark_mode:
            fig.patch.set_facecolor('#2d2d2d')
            ax.set_facecolor('#3c3c3c')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')
            ax.grid(color='gray')

        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    # Создание пользовательского интерфейса
    def setup_ui(self):
        frame = ctk.CTkFrame(self.root)
        frame.pack(pady=10)

        # Валюты по умолчанию
        self.from_currency = ctk.StringVar(value="USD")
        self.to_currency = ctk.StringVar(value="EUR")

        # Метки и поля выбора валют
        self.from_label = ctk.CTkLabel(frame, text=self.t("from"))
        self.from_label.grid(row=0, column=0, padx=5)

        self.from_search_label = ctk.CTkLabel(frame, text=self.t("search"))
        self.from_search_label.grid(row=0, column=1, padx=5)
        self.from_search = ctk.CTkEntry(frame, width=100)
        self.from_search.grid(row=1, column=1, padx=5)
        self.from_search.bind("<KeyRelease>", lambda e: self.search_currency(e, self.from_currency, self.from_menu))

        self.from_menu = ctk.CTkOptionMenu(frame, variable=self.from_currency, values=self.currencies)
        self.from_menu.grid(row=1, column=0, padx=5)

        self.swap_button = ctk.CTkButton(frame, text=self.t("swap"), command=self.swap_currencies)
        self.swap_button.grid(row=1, column=2, padx=5)

        self.to_label = ctk.CTkLabel(frame, text=self.t("to"))
        self.to_label.grid(row=0, column=3, padx=5)

        self.to_search_label = ctk.CTkLabel(frame, text=self.t("search"))
        self.to_search_label.grid(row=0, column=4, padx=5)
        self.to_search = ctk.CTkEntry(frame, width=100)
        self.to_search.grid(row=1, column=4, padx=5)
        self.to_search.bind("<KeyRelease>", lambda e: self.search_currency(e, self.to_currency, self.to_menu))

        self.to_menu = ctk.CTkOptionMenu(frame, variable=self.to_currency, values=self.currencies)
        self.to_menu.grid(row=1, column=3, padx=5)

        self.amount_label = ctk.CTkLabel(frame, text=self.t("amount"))
        self.amount_label.grid(row=0, column=5, padx=5)

        self.amount_entry = ctk.CTkEntry(frame, width=100)
        self.amount_entry.grid(row=1, column=5, padx=5)
        self.amount_entry.insert(0, "100")

        self.convert_button = ctk.CTkButton(frame, text=self.t("convert"), command=self.convert_currency)
        self.convert_button.grid(row=1, column=6, padx=5)

        self.result_label = ctk.CTkLabel(frame, text="", font=("Arial", 14))
        self.result_label.grid(row=2, column=0, columnspan=7, pady=10)

        self.chart_frame = ctk.CTkFrame(self.root)
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=10)

        bottom_frame = ctk.CTkFrame(self.root)
        bottom_frame.pack(pady=5)

        self.update_button = ctk.CTkButton(bottom_frame, text=self.t("refresh"),
                                           command=lambda: self.plot_exchange_rate(
                                               self.from_currency.get(), self.to_currency.get()))
        self.update_button.pack(side="left", padx=10)

        self.theme_button = ctk.CTkButton(bottom_frame, text=self.t("theme"), command=self.toggle_theme)
        self.theme_button.pack(side="left", padx=10)

        self.lang_button = ctk.CTkButton(bottom_frame, text=self.t("lang"), command=self.toggle_language)
        self.lang_button.pack(side="left", padx=10)

# Запуск приложения
if __name__ == "__main__":
    root = ctk.CTk()
    app = CurrencyConverterApp(root)
    root.mainloop()
