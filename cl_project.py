import json
import os
from tkinter.filedialog import asksaveasfile, askopenfilename

file_type_name = "Файл проекта проверки ссылок"
file_type_ext = ".clprj"

class CLProject:
    def __init__(self, domain="", pages=[], filename=""):
        self.domain = domain
        self.pages = pages
        self.filename = filename
    
    def to_dict(self):
        return {
            "domain": self.domain,
            "pages": self.pages
        }
    
    @property    
    def report_filename(self):
        return (os.path.splitext(self.filename)[0] + ".clrep") if self.filename.strip() else ""

    @classmethod
    def from_dict(cls, data):
        return cls(data["domain"], data["pages"])
        
    @property   
    def name(self):
        return self.filename if self.filename.strip() else "ПРОЕКТ НЕ СОХРАНЁН"
    
    def do_autosave(self):
        if self.filename:
            return self.to_json()
        else:
            return self.save_as_json()
            
            
    def to_json(self):
        if self.filename:
            with open(self.filename, "w") as f:
                json.dump(self.to_dict(), f)
                return True
        return False
    
    @classmethod
    def from_json(cls, filename):
        if filename:
            try:
                with open(filename, "r") as f:
                    data = json.load(f)
                    prj = cls.from_dict(data)
                    prj.filename = filename
                    return prj
            except Exception:
                return CLProject()
        else:
            raise ValueError("No file selected!")
    
    @classmethod     
    def load(cls):
        filename = askopenfilename(filetypes=[(file_type_name, "*"+file_type_ext)])
        return cls.from_json(filename)
    
    def save_as_json(self):
        dir_path, file_name = os.path.split(self.filename)
        filename = asksaveasfile(defaultextension=file_type_ext, initialdir=dir_path, initialfile=file_name, filetypes=[(file_type_name, "*"+file_type_ext)])

        if filename:
            self.filename = filename.name
            self.to_json()
            return True
        
        return False