import tkinter as tk
from tkinter import ttk

from cl_link_checker import LinkCheckResult

class TableReportView:
    def __init__(self, root, checks):
        self.checks = checks
        self.root = root
         
    def create_table(self):
        # Создание виджета Treeview
        self.tree = ttk.Treeview(self.root)

        # Задание заголовков столбцов
        self.tree["columns"] = ("has_link", "anchor_str", "dofolow", "ya_check", "g_check")
        self.tree.column("#0", width=120, minwidth=100, stretch=True)
        self.tree.column("has_link", width=60, minwidth=100, stretch=False, anchor=tk.CENTER)
        self.tree.column("has_link", width=60, minwidth=100, stretch=False)
        self.tree.column("anchor_str", width=100, minwidth=100)
        self.tree.column("dofolow", width=80, stretch=False, anchor=tk.CENTER)
        self.tree.column("ya_check", width=60, stretch=False, anchor=tk.CENTER)
        self.tree.column("g_check", width=60, stretch=False, anchor=tk.CENTER)

        self.tree.heading("#0", text="Адрес сайта", anchor=tk.CENTER)
        self.tree.heading("has_link", text="Ссылка", anchor=tk.CENTER)
        self.tree.heading("anchor_str", text="Анкор", anchor=tk.CENTER)
        self.tree.heading("dofolow", text="DoFollow", anchor=tk.CENTER)
        self.tree.heading("ya_check", text="Yandex", anchor=tk.CENTER)
        self.tree.heading("g_check", text="Google", anchor=tk.CENTER)

        #self.tree.tag_configure('evenrow', background='red')
        # Задание стиля разделительной полосы
        #style = ttk.Style()
        #style.configure("Treeview", rowheight=20, bordercolor="black", borderwidth=1)

        # Размещение Treeview на форме
        #self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.tree.grid(row=4, column=1, columnspan=4, sticky="nsew", padx=4, pady=4)

    def set_checks(self, checks):
        self.checks = checks
        self.tree.delete(*self.tree.get_children())
        self.fill_table()
        
    def fill_table(self):
        # Заполнение таблицы данными из списка checks
        for i, check in enumerate(self.checks):
            if i % 2 == 0:
                tags = ('evenrow',)
            else:
                tags = ()
            self.tree.insert("", tk.END, text=check.http_url, values=(check.has_link_text, check.anchor_str_text, check.nofollow_text, check.ya_check_text, check.g_check_text), tags=tags)
        self.tree.tag_configure('evenrow', background='#f0f0f0')

    def run(self):
        # Задание минимальной ширины окна
        self.root.minsize(600, 400)

        # Запуск главного цикла обработки событий
        self.root.mainloop()

checks = [LinkCheckResult("http://example.com", True, "Example", True, False, True),
          LinkCheckResult("http://google.com", False, "", False, True, True)]

def test_table_report_view():
    root = tk.Tk()
    table_view = TableReportView(root, checks)
    table_view.create_table()
    table_view.fill_table()
    table_view.run()