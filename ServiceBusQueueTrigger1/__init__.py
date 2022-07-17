from datetime import datetime
import logging
import azure.functions as func
import psycopg2
import sendgrid

from sendgrid.helpers.mail import Mail
from web.config import BaseConfig
import psycopg2.extras

from .pymodels import PAttendee, PNotification


def main(msg: func.ServiceBusMessage):
    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s', notification_id)
    conn = psycopg2.connect(
        host=BaseConfig.POSTGRES_URL,
        database=BaseConfig.POSTGRES_DB,
        user=BaseConfig.POSTGRES_USER,
        password=BaseConfig.POSTGRES_PW)

    try:
        count_notifications = 0
        # Get notification message and subject from database using the notification_id

        notification_item = get_notification_item(conn=conn, notification_id=notification_id)
        notification_msg = notification_item.message
        notification_sub = notification_item.subject

        # Get attendees email and name
        attendee_list = get_items(conn=conn, table_name="attendee", model=PAttendee)

        # Loop through each attendee and send an email with a personalized subject
        for attendee in attendee_list:
            response = send_email(attendee=attendee, notif_content=notification_msg, notif_sub=notification_sub)

            if response.status_code == 202:
                count_notifications += 1

        # Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        update_notification_item(conn=conn, notification_id=notification_id, count=count_notifications)

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        conn.close()


def get_items(conn: psycopg2.connect, table_name: str, model):
    model_list = list()
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        query = f'SELECT * FROM {table_name}'
        cursor.execute(query)
        column_name_list = [descrip[0] for descrip in cursor.description]
        items = cursor.fetchall()
        cursor.close()
    dict_result = map(lambda x: dict(zip(column_name_list, x)), items)
    for item in dict_result:
        model_list.append(model(**item))
    return model_list


def get_notification_item(conn: psycopg2.connect, notification_id: int):
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        query = f'SELECT * FROM notification WHERE id = {notification_id}'
        cursor.execute(query)
        column_name_list = [descrip[0] for descrip in cursor.description]
        item = cursor.fetchone()
        cursor.close()
        dict_result = dict(zip(column_name_list, item))
        notification_item = PNotification(**dict_result)
    return notification_item


def update_notification_item(conn: psycopg2.connect, notification_id: int, count: int):
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        status_update = f'Notified {count} attendees'
        query = """
                UPDATE notification 
                SET status = %s , 
                completed_date = %s
                WHERE id = %s
                """
        cursor.execute(
            query,
            (status_update, datetime.utcnow(), notification_id)
        )
        # Commit the changes to the database
        conn.commit()
        # Close communication with the PostgreSQL database
        cursor.close()

    return get_notification_item(conn, notification_id)


def send_email(attendee, notif_content, notif_sub):
    sg = sendgrid.SendGridAPIClient(api_key=BaseConfig.SENDGRID_API_KEY)
    from_email = BaseConfig.ADMIN_EMAIL_ADDRESS
    attendee_email = attendee.email
    attendee_name = attendee.first_name + attendee.last_name
    personalized_msg = "Dear" + attendee_name + "/n" + notif_content
    mail = Mail(from_email, attendee_email, notif_sub, personalized_msg)
    mail_json = mail.get()
    response = sg.client.mail.send.post(request_body=mail_json)
    return response
