FROM itsre/slack-py:3.6-onbuild

COPY . /usr/src/app/

ONBUILD RUN pip install nltk
ONBUILD RUN python -m nltk.downloader punkt -d /usr/local/share/nltk_data all
RUN [ "python", "-c", "import nltk; nltk.data.path.append('/usr/local/share/nltk_data')"]
RUN [ "python", "-c", "import nltk; nltk.data.path.remove('/home/slack/nltk_data')"]
RUN [ "python", "-c", "import nltk; nltk.download('wordnet', download_dir='/usr/src/app/nltk_data')" ]
RUN [ "python", "-c", "import nltk; nltk.download('stopwords', download_dir='/usr/src/app/nltk_data')" ]

EXPOSE 5000

CMD sh -c "/usr/local/bin/gunicorn -w ${APP_WORKERS} -b :${APP_PORT} ${APP_MODULE}"