import csv
import json
from io import StringIO
from django.shortcuts import render


class BaseConvertor:
    def __init__(self, content):
        self.content = content

    def get_result(self):
        res = self.parse_content()
        return self.to_edi(res)

    @staticmethod
    def to_edi(val):
        if isinstance(val, str):
            return val
        res = ''
        for i in val:
            res = res + '*'.join(i) + '\n'
        return res


class CsvConvertor(BaseConvertor):
    def parse_content(self):
        f = StringIO(self.content)
        return csv.reader(f, delimiter=',')


class JsonConvertor(BaseConvertor):
    def parse_content(self):
        return json.loads(self.content)


class ExcelConvertor(BaseConvertor):
    def parse_content(self):
        raise Exception("Excel parser is not implemented")


class EdiConvertor(BaseConvertor):
    def parse_content(self):
        return self.content


def index(request):
    if request.method != "POST":
        return render(request, 'index.html')

    file_type = request.POST.get('file-type')
    input_file = request.FILES.get('input-file')
    if input_file.name.split('.')[-1] != file_type:
        return render(request, 'index.html', {
            "err": 'File format does not match file type'
        })
    content = input_file.read().decode('utf8')
    convertor_cls = {
        "csv": CsvConvertor,
        "json": JsonConvertor,
        "xls": ExcelConvertor,
        "edi": EdiConvertor,
    }[file_type]
    convertor = convertor_cls(content)
    try:
        res = convertor.get_result()
    except Exception as e:
        return render(request, 'index.html', {"err": str(e)})
    else:
        return render(request, 'index.html', {"res": res})
