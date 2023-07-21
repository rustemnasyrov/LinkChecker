from datetime import time
import datetime
import tkinter as tk
from cl_link_checker import LinkCheckResult

from cl_table_report_view import TableReportView
from collections import OrderedDict

class ReportViewer:
    def __init__(self, checks):
        self.checks = checks
    
    def __init__(self):
        self.checks = OrderedDict()
    
    checks = OrderedDict()
    left_listbox = None
    right_listbox = None

    def current_time_string(self):
        current_timestamp = datetime.datetime.now()
        formatted_datetime = current_timestamp.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_datetime  # 2021-05-24 15:23:45

    def add_report(self, check_results):
        self.right_table.set_checks(check_results)
        
        key = self.current_time_string()
        self.checks[key] = check_results
        self.checks.move_to_end(key, last=False)
        
        self.fill_left_listbox(sel_idx=0)
        self.update_right_table()
        return 4
    
    def clear_report(self):
        self.checks = OrderedDict()
        self.fill_left_listbox()
        self.right_table.set_checks([])

    # Функция для обновления правого списка в зависимости от выбранного элемента левого списка
    def update_right_table(self, event=None):
        # Получение выбранного элемента левого списка
        if self.left_listbox.size() > 0:
            cur_sel = self.left_listbox.curselection()
            selected_item = self.left_listbox.get(cur_sel)
            self.right_table.set_checks(self.checks[selected_item])

    def export_excel(self):
        self.export(LinkCheckResult.export_to_excel)  

    def export_pdf(self):
        self.export(LinkCheckResult.export_to_pdf)  

    def export(self, export_func):
        # Получение выбранного элемента левого списка
        if self.left_listbox.size() > 0:
            cur_sel = self.left_listbox.curselection()
            selected_item = self.left_listbox.get(cur_sel)
            export_func(self.checks[selected_item])  
            
    def create_report(self, root):
        # Создание двух списков
        self.left_listbox = tk.Listbox(root)
        self.right_table = TableReportView(root, [])

        # Заполнение левого списка полями date_info
        self.fill_left_listbox()

        # Привязка функции update_right_table к событию выбора элемента левого списка
        self.left_listbox.bind("<<ListboxSelect>>", self.update_right_table)

        # Размещение списков на форме
        self.left_listbox.grid(row=4, column=0, sticky="nsew", padx=4, pady=4)
        self.right_table.create_table()

    def fill_left_listbox(self, sel_idx = None):
        self.left_listbox.delete(0, tk.END)  # очищаем листбокс
        for key in self.checks.keys():
            self.left_listbox.insert(tk.END, key)
        if sel_idx is not None:
            self.left_listbox.select_set(sel_idx)
            
    def save_report_to(self, filename):
        LinkCheckResult.save_results_to_json(self.checks, filename)
        
    def load_report_from(self, filename):
        self.checks = LinkCheckResult.load_results_from_json(filename)
        self.fill_left_listbox(0)
        self.update_right_table()
        
