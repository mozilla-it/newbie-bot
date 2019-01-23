FROM itsre/slack-py:3.6-onbuild


RUN python -m venv venv

RUN venv/bin/pip install gunicorn

COPY requirements.txt requirements.txt

COPY ./database ./forms ./static ./templates /usr/src/app/
COPY . /usr/src/app/

COPY app.py auth.py boot.sh config.py  conversion.py get_config.py json_object_encoder.py nltk_processing.py routes.py settings.py ./


ENV FLASK_APP app.py


EXPOSE 5000

CMD sh -c "/usr/local/bin/gunicorn -w ${APP_WORKERS} -b :${APP_PORT} ${APP_MODULE}"
