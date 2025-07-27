# ���������� Python 3.11 ������ 3.13
FROM python:3.11-slim

# ������� ���������� ������ ����������
WORKDIR /app

# �������� ��� ����� ������� ������ ����������
COPY . .

# ������� pip � ��������� �����������
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# ������� �������
CMD ["python", "main.py"]
