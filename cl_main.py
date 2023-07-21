from genericpath import exists
from tkinter import Frame, Menu, Tk, Label, Entry, Listbox, Button, StringVar, END, messagebox

import requests
from cl_link_checker import LinkCheckResult
from cl_project import CLProject

from cl_report_view import ReportViewer
from cl_settings import CLSettings


class MainWindow:
    content_changed_flag = False
    title = "LinkChecker 1.0 beta"
    
    def __init__(self):    
        self.listbox_file = "listbox_content.txt"
        self.root = Tk()
        self.root.title(self.title)
        self.root.geometry("640x480")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # создание меню
        menu_bar = Menu(self.root)
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Новый проект", command=self.clear_listbox)
        file_menu.add_command(label="Открыть проект...", command=self.load_listbox)
        file_menu.add_command(label="Сохранить", command=self.save_listbox)
        file_menu.add_command(label="Сохранить как...", command=self.save_as_listbox)
        menu_bar.add_cascade(label="Файл", menu=file_menu)
        self.root.config(menu=menu_bar)

        label = Label(self.root, text="Адрес страницы:")
        label.grid(row=0, column=0, padx=2, pady=2, sticky='w')

        self.entry = Entry(self.root)
        self.entry.grid(row=0, column=1, padx=2, pady=2, sticky="nsew")

        add_button = Button(self.root, text="  Добавить  ", command=self.add_string)
        add_button.grid(row=0, column=2, padx=2, pady=2)

        delete_button = Button(self.root, text="  Удалить  ", command=self.delete_string)
        delete_button.grid(row=0, column=3, padx=2, pady=2)

        edit_button = Button(self.root, text="  Заменить  ", command=self.edit_string)
        edit_button.grid(row=0, column=4, padx=2, pady=2)

        self.listbox_pages = Listbox(self.root)
        self.listbox_pages.grid(row=1, column=0, columnspan=5, sticky="nsew", padx=4, pady=4)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        label2 = Label(self.root, text="Ссылка для проверки:")
        label2.grid(row=2, column=0, padx=2, pady=2, sticky='w')

        self.domain_name = Entry(self.root)
        self.domain_name.grid(row=2, column=1, padx=2, pady=2, sticky="nsew")
        self.domain_name.bind("<KeyRelease>", self.on_domain_change)

        check_button = Button(self.root, text="Проверить", command=self.check_link_action)
        check_button.grid(row=2, column=2, padx=2, pady=2)

        label = Label(self.root, text="Отчет о проверке")
        label.grid(row=3, column=0, columnspan=5, padx=4, pady=0)

        self.report_view = ReportViewer()
        self.report_view.create_report(self.root)
        self.root.grid_rowconfigure(4, weight=1)
        self.root.grid_columnconfigure(0, minsize=150, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
        
        pdf_button = Button(self.root, text="  Экспорт PDF  ", command=self.on_pdf_export)
        pdf_button.grid(row=5, column=3, padx=6, pady=6)

        xls_button = Button(self.root, text="  Экспорт Excell  ", command=self.on_excel_export)
        xls_button.grid(row=5, column=4, padx=6, pady=6)

        self.settings = CLSettings.load()
        self.set_project(self.settings.load_project_or_default())

    @property
    def content_changed_set(self):
        self.content_changed_flag = True
        self.update_title()

    @property
    def content_changed_reset(self):
        self.content_changed_flag = False
        self.update_title()

    def on_domain_change(self, event):
        self.content_changed_set
        
    def on_pdf_export(self):
        self.report_view.export_pdf()
    
    def on_excel_export(self):
        self.report_view.export_excel()
  
    
    def add_string(self):
        string = self.entry.get()
        if string:
            self.listbox_pages.insert(END, string)
            self.entry.delete(0, END)
        self.content_changed_set

    def delete_string(self):
        selected_index = self.listbox_pages.curselection()
        if selected_index:
            self.listbox_pages.delete(selected_index)
        self.content_changed_set

    def edit_string(self):
        selected_index = self.listbox_pages.curselection()
        if selected_index:
            string = self.entry.get()
            if string:
                self.listbox_pages.delete(selected_index)
                self.listbox_pages.insert(selected_index, string)
                self.entry.delete(0, END)
        self.content_changed_set

    def check_link_action(self):
        checks = LinkCheckResult.check(self.listbox_pages.get(0, END), self.domain_name.get())
        self.report_view.add_report(checks)
        if self.cl_project.report_filename:
            self.report_view.save_report_to(self.cl_project.report_filename) 

    def save_as_listbox(self):
        self.save_listbox_with(self.cl_project.save_as_json)

    def save_listbox(self):
        self.save_listbox_with(self.cl_project.do_autosave)
        
    def save_listbox_with(self, save_func):
        self.cl_project.domain = self.domain_name.get()
        self.cl_project.pages = self.listbox_pages.get(0, END)
        if save_func():
            self.settings.set_project(self.cl_project)
            self.content_changed_reset

    def clear_listbox(self):
        self.set_project(CLProject())
        self.report_view.clear_report()

    def load_listbox(self):
        try:
            self.clear_project()
            self.set_project(CLProject.load())
        except ValueError as e:
            # messagebox.showerror("Ошибка", str(e))
            return
        return

    def set_project(self, cl_project):
        self.clear_project()
                    
        self.cl_project = cl_project
        self.settings.set_project(cl_project)
        self.update_title()
        self.domain_name.delete(0, END)
        self.domain_name.insert(0, self.cl_project.domain)
        self.listbox_pages.delete(0, self.listbox_pages.size())
        for line in self.cl_project.pages:
            self.listbox_pages.insert(END, line)
        if self.cl_project.report_filename:
            self.report_view.load_report_from(self.cl_project.report_filename) 
        
        self.content_changed_reset

    def update_title(self):
        title = self.title
        if self.cl_project.name:
            title +=  (" - " + ('* ' if self.content_changed_flag else '') +  self.cl_project.name)
        self.root.title(title)

    def on_closing(self):
        self.clear_project()
        self.settings.save()
        self.root.destroy()

    def clear_project(self):
        if self.content_changed_flag and messagebox.askyesno(self.title, "Проект был изменён. Вы хотите сохранить изменения?"):
            self.save_listbox_with(self.cl_project.do_autosave)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()