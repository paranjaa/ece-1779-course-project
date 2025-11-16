FROM python:3.11
ADD ./templates ./app.py ./forms.py ./utils.py ./requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "-u", "app.py"]