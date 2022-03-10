FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY place_order.py ./
COPY check_stripe_payment_success.py ./
COPY invokes.py ./
COPY amqp_setup.py ./
CMD [ "python", "./place_order.py" ]