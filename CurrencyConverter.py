import tkinter as tk
from tkinter import ttk, messagebox
import json
import requests
from datetime import datetime

# --- Настройки ---
API_KEY = "YOUR_API_KEY"  # Замените на свой ключ
BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"
HISTORY_FILE = "history.json"

# --- Логика работы с API и конвертацией ---
def get_rates():
    """Получает актуальные курсы валют."""
    try:
        response = requests.get(BASE_URL)
        data = response.json()
        if data.get("result") == "success":
            return data["conversion_rates"]
        else:
            raise Exception("Ошибка API: " + data.get("error-type", "неизвестная ошибка"))
    except Exception as e:
        print(f"Ошибка при получении курсов: {e}")
        return None

def convert_currency(amount, from_cur, to_cur, rates):
    """Конвертирует сумму из одной валюты в другую."""
    if from_cur == to_cur:
        return amount
    if from_cur != "USD":
        amount = amount / rates[from_cur]
    return amount * rates[to_cur]

# --- Логика работы с историей ---
def save_history(history):
    """Сохраняет историю в файл."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def load_history():
    """Загружает историю из файла."""
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def add_to_history(entry):
    """Добавляет новую запись в историю."""
    history = load_history()
    history.append(entry)
    save_history(history)

# --- Графический интерфейс ---
class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        
        self.currencies = ["USD", "EUR", "RUB", "GBP", "JPY", "CNY"]
        
        # Элементы интерфейса
        ttk.Label(root, text="Из:").grid(row=0, column=0, padx=5, pady=5)
        self.from_currency = ttk.Combobox(root, values=self.currencies)
        self.from_currency.set("USD")
        self.from_currency.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(root, text="В:").grid(row=1, column=0, padx=5, pady=5)
        self.to_currency = ttk.Combobox(root, values=self.currencies)
        self.to_currency.set("EUR")
        self.to_currency.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(root, text="Сумма:").grid(row=2, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(root)
        self.amount_entry.grid(row=2, column=1, padx=5, pady=5)
        
        self.convert_button = ttk.Button(root, text="Конвертировать", command=self.convert)
        self.convert_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.result_label = ttk.Label(root, text="Результат: ")
        self.result_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Таблица истории
        self.history_tree = ttk.Treeview(root, columns=("date", "from", "to", "amount", "result"), show="headings")
        self.history_tree.heading("date", text="Дата")
        self.history_tree.heading("from", text="Из")
        self.history_tree.heading("to", text="В")
        self.history_tree.heading("amount", text="Сумма")
        self.history_tree.heading("result", text="Результат")
        
        for col in ("date", "from", "to", "amount", "result"):
            self.history_tree.column(col, width=100)
            
        self.history_tree.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        
        self.load_history_to_table()
    
    def is_valid_amount(self):
        value = self.amount_entry.get()
        try:
            amount = float(value)
            return amount > 0
        except ValueError:
            return False

    def convert(self):
        if not self.is_valid_amount():
            messagebox.showerror("Ошибка", "Введите положительное число!")
            return

        from_cur = self.from_currency.get()
        to_cur = self.to_currency.get()
        
        rates = get_rates()
        if not rates:
            messagebox.showerror("Ошибка", "Не удалось получить курсы валют. Проверьте интернет и API-ключ.")
            return

        amount = float(self.amount_entry.get())
        
        try:
            result = convert_currency(amount, from_cur, to_cur, rates)
            result_str = f"{result:.2f} {to_cur}"
            self.result_label.config(text=f"Результат: {result_str}")
            
            # Сохранение в историю
            entry = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "from": from_cur,
                "to": to_cur,
                "amount": amount,
                "result": result,
                "result_str": result_str
            }
            add_to_history(entry)
            
            # Добавление строки в таблицу (в начало для наглядности)
            self.history_tree.insert("", 0, values=(entry["date"], from_cur, to_cur, f"{amount:.2f}", result_str))
            
        except KeyError:
            messagebox.showerror("Ошибка", f"Неизвестная валюта. Доступны: {', '.join(rates.keys())}")
    
    def load_history_to_table(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        hist = load_history()
        for entry in hist:
            self.history_tree.insert("", tk.END, values=(entry["date"], entry["from"], entry["to"], f"{entry['amount']:.2f}", entry["result_str"]))

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverterApp(root)
    root.mainloop()
