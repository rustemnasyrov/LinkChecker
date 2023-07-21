from collections import OrderedDict
import json
from tkinter.filedialog import asksaveasfilename
from fpdf import FPDF
import pandas as pd
import requests
from bs4 import BeautifulSoup


class LinkCheckResult:
    def __init__(self, http_url, domain, has_link=False, anchor_str='', nofolow=False, ya_check=False, g_check=False):
        self.http_url = http_url
        self.domain = domain
        self.has_link = has_link
        self.anchor_str = anchor_str
        self.nofollow = nofolow
        self.ya_check = ya_check
        self.g_check = g_check
        
    @property
    def http_url_text(self):
        return str(self.http_url)

    @property
    def domain_text(self):
        return str(self.domain)

    @property
    def has_link_text(self):
        return 'да' if self.has_link else 'нет'

    @property
    def anchor_str_text(self):
        return str(self.anchor_str)

    @property
    def nofollow_text(self):
        return 'нет' if self.nofollow else 'да'

    @property
    def ya_check_text(self):
        return 'да' if self.ya_check else 'нет'

    @property
    def g_check_text(self):
        return 'да' if self.g_check else 'нет'
        
    def to_dict(self):
        return {
                    "http_url":     self.http_url,
                    "domain":       self.domain,
                    "has_link":     self.has_link,
                    "anchor_str":   self.anchor_str,
                    "nofollow":     self.nofollow,
                    "ya_check":     self.ya_check,
                    "g_check":      self.g_check
                }
        
    @classmethod    
    def from_dict(cl, value):
        return cl(value['http_url'], value['domain'], value['has_link'], value['anchor_str'], value['nofollow'], value['ya_check'], value['g_check'])    
        
    @staticmethod    
    def save_results_to_json(results, filename,):
        data = OrderedDict()
        for key, value in results.items():
            results = OrderedDict()
            for i in range(len(value)):
                results[i] = value[i].to_dict()
            data[key] = results
        with open(filename, 'w') as f:
            json.dump(data, f)
    
    @staticmethod        
    def load_results_from_json(filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f, object_pairs_hook=OrderedDict)
                results = OrderedDict()
                for key, checks in data.items():
                    chek_results = []
                    for check in checks.values():
                        chek_results.append(LinkCheckResult.from_dict(check))
                    results[key] = chek_results
                return results
        except Exception:
            return OrderedDict()
        
    @staticmethod
    def check(html_urls, link_url):
        result = []
        for html_url in html_urls:
            lc = LinkCheckResult(http_url=html_url, domain=link_url)
            result.append(lc.do_check())
        return result
    
    def do_check(self):
        return self.check_link()
        
        
    @staticmethod
    def check_links_in_html_urls(html_urls, link_url):
        results = []
        for html_url in html_urls:
            try:
                 results.append(LinkCheckResult.check_link(html_url, link_url))
            except requests.exceptions.RequestException:
                results.append(LinkCheckResult(http_url="Ошибка: " + html_url))
        return results
    
    def reset(self):
        self.has_link = False
        self.anchor_str = False
        self.nofollow = False
        self.ya_check = False
        self.g_check = False        
    
    def check_link(self):
            html_url = self.http_url
            link_url = self.domain
            self.reset()
            try:
            # Загрузка HTML страницы
                links = self.get_all_links_of(html_url)

                # Проверка наличия ссылки
                for link in links:
                    if link.get('href') == link_url:
                        self.has_link = True
                        
                        rel = link.get('rel')
                        if rel:
                            self.nofollow = 'nofollow' in rel
                            
                        self.anchor_str = link.get('title')
                        self.ya_check = self.check_index_ya(html_url, self.anchor_str)
                        self.g_check = self.check_index_google(html_url, self.anchor_str)
            except Exception as e:
                self.anchor_str = f"Err: {e.args[0]}"
            return self

    def get_all_links_of(self, html_url):
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(html_url, headers=headers)
        response.raise_for_status()

            # Парсинг HTML
        soup = BeautifulSoup(response.text, 'html.parser')

            # Поиск ссылок на странице
        links = soup.find_all('a')
        return links
      
    def check_index_ya(self, site_url, text_query):
        return self.check_index(site_url, text_query, self.get_ya_links)

    def check_index_google(self, site_url, text_query):
        return self.check_index(site_url, text_query, self.get_g_links)
        
    def check_index(self, site_url, text_query, query_func):
        no_result_links = query_func(site_url, 'ровпавырпаорвпыопвыапывм')
        links = query_func(site_url, text_query)
        return len(links) > len(no_result_links)
    
    def get_ya_links(self, site_url, text_query):
        search_url = f"https://yandex.ru/search/?text={text_query}+site%3A{site_url}&lr=1107"
        links = self.get_all_links_of(search_url)
        return links

    def get_g_links(self, site_url, text_query):
        search_url = f"https://www.google.com/search?q={text_query}+site:{site_url}&lr=lang_ru"
        links = self.get_all_links_of(search_url)
        return links
    
    @staticmethod
    def export_to_excel(results):
        file_path = asksaveasfilename(defaultextension='.xlsx', filetypes=[("Файлы Excel", "*.xlsx")])
        if not file_path:
            return
        data = []
        for result in results:
            data.append({
                'http_url': result.http_url_text,
                'domain': result.domain_text,
                'has_link': result.has_link_text,
                'anchor_str': result.anchor_str_text,
                'nofollow': result.nofollow_text,
                'ya_check': result.ya_check_text,
                'g_check': result.g_check_text
            })
        df = pd.DataFrame(data) # columns=['Адрес сайта', 'Домен', 'Ссылка', 'Анкор', 'DoFollow', 'Yandex', 'Google'])
        writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        worksheet.set_column(0, 0, 20)
        worksheet.set_column(1, 5, 10)
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        workbook.close()
        
    def export_to_pdf(results):
        # Создание PDF-файла
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()
        pdf.add_font('NotoSans', '', 'NotoSans-Regular.ttf', uni=True)
        pdf.set_font('NotoSans', size=10)
             
        pdf.cell(200, 10, txt="Экспорт из программы LinkChecker", ln=1)
        pdf.cell(200, 10, txt="", ln=1)
        pdf.cell(50, 10, txt="URL", border=1, align='C')
        pdf.cell(50, 10, txt="Домен", border=1, align='C')
        pdf.cell(20, 10, txt="Ссылка", border=1, align='C')
        pdf.cell(100, 10, txt="Анкор", border=1, align='C')
        pdf.cell(20, 10, txt="DoFollow", border=1, align='C')
        pdf.cell(20, 10, txt="Yandex", border=1, align='C')
        pdf.cell(20, 10, txt="Google", border=1, align='C')
        pdf.cell(0, 10, txt="", ln=1)
        for row in results:
            pdf.cell(50, 10, txt=str(row.http_url_text), border=1)
            pdf.cell(50, 10, txt=str(row.domain_text), border=1)
            pdf.cell(20, 10, txt=str(row.has_link_text), border=1, align='C')
            pdf.cell(100, 10, txt=str(row.anchor_str_text), border=1)
            pdf.cell(20, 10, txt=str(row.nofollow_text), border=1, align='C')
            pdf.cell(20, 10, txt=str(row.ya_check_text), border=1, align='C')
            pdf.cell(20, 10, txt=str(row.g_check_text), border=1, align='C')
            pdf.cell(0, 10, txt="", ln=1)
            
            # Если таблица не помещается на страницу, добавляем новую страницу
            if pdf.get_y() > 250:
                pdf.add_page()


        # Сохранение PDF-файла
        file_name = asksaveasfilename(defaultextension='.pdf', filetypes=[("Файлы PDF", "*.pdf")])
        if file_name:
            pdf.output(file_name, 'F')

        
