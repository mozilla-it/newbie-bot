FROM itsre/slack-py:3.6-onbuild

COPY . /usr/src/app/

EXPOSE 5000

CMD sh -c "/usr/local/bin/gunicorn -w ${APP_WORKERS} -b :${APP_PORT} ${APP_MODULE}"