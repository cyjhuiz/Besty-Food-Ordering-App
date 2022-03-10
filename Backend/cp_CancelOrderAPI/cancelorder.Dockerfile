FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY cancel_order.py ./
COPY invokes.py ./
COPY amqp_setup.py ./
CMD [ "python", "./cancel_order.py" ]