from newb import app, scheduler
import atexit
from newb.routes import send_newhire_messages, get_auth_zero, updates_from_slack
import logging


@atexit.register
def shutdown():
    """
    Register the function to be called on exit
    """
    atexit.register(lambda: scheduler.shutdown())

@app.before_first_request
def start_schedule():
    print('scheduler = {}'.format(scheduler.running))
    if scheduler.running is False:
        print(f'schedule running {scheduler.running}')
        scheduler.start()
        with app.app_context():
            # scheduler.add_job(func=send_newhire_messages, trigger='cron', hour='*', minute='*/10')
            # scheduler.add_job(func=get_auth_zero, trigger='cron', hour='*', minute=0)
            # scheduler.add_job(func=updates_from_slack, trigger='cron', hour='*', minute=15)
            pass

start_schedule()


if __name__ != '__main__':
    print(f'name not main')
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':
    print('starting app')
    # app.run(ssl_context=('cert.pem', 'key.pem'), host='0.0.0.0', port=8000)
    app.run(host='0.0.0.0', port=8000)
