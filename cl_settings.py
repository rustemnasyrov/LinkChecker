import json
from cl_project import CLProject
from tkinter.filedialog import asksaveasfile, askopenfilename

class CLSettings:
    def __init__(self, last_file, project):
        self.last_file = last_file
        self.project = project
                
    def set_project(self, cl_project):
        self.project = cl_project
        self.last_file = cl_project.filename
        
    def load_project_or_default(self):
        if self.last_file:
            return CLProject.from_json(self.last_file)
        
        return self.project
    
    def to_dict(self):
        return {"filename": self.last_file, "project": self.project.to_dict()}
    
    @classmethod
    def from_dict(cls, set_dict):
        prj_dict = set_dict["project"]
        project = CLProject.from_dict(prj_dict)
        return cls(set_dict["filename"], project)

    def save(self):
        with open("settings.json", "w", encoding='utf-8') as f:
            json.dump(self.to_dict(), f)

    @classmethod
    def load(cls):
        try:
            with open("settings.json", "r") as f:
                return cls.from_dict(json.load(f))
        except Exception:
            return CLSettings("", CLProject())

    def save_project(self):
        if self.project:
            self.project.do_autosave()
            self.last_file = self.project.filename
            self.save()

    def load_project(self, file_type_name, file_type_ext):
        try:
            filename = askopenfilename(filetypes=[(file_type_name, "*"+file_type_ext)])
            if filename:
                project = CLProject.from_json()
                self.project = project
                self.last_file = project.filename
                self.save()
        except ValueError as e:
            print(e)

# пример использования класса Settings
def test():
    settings = CLSettings()
    settings.load()

    if settings.last_file:
        try:
            project = CLProject.from_json(settings.last_file)
            settings.project = project
        except ValueError as e:
            print(e)