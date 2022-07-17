import datetime
from typing import Union, Optional

import pydantic

from web.config import BaseConfig
import logging
import azure.functions as func
import psycopg2

from pydantic import BaseModel
import psycopg2.extras


# logging.info('Python ServiceBus queue trigger processed message: %s', notification_id)

class Notification(BaseModel):
    id: str
    status: str
    message: str
    submitted_date: Union[datetime.datetime, None]
    completed_date: Union[datetime.datetime, None]
    subject: str


class Conference(BaseModel):
    id: str
    name: str
    active: str
    date: datetime.date
    price: str
    address: str


class Attendee(BaseModel):
    id: str
    first_name: str
    last_name: str
    conference_id: str
    job_position: str
    email: str
    company: str
    city: str
    state: str
    interests: str
    submitted_date: datetime.datetime
    comments: str


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
        notification_item = Notification(**dict_result)
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
            (status_update, datetime.datetime.utcnow(), notification_id)
        )
        # Commit the changes to the database
        conn.commit()
        # Close communication with the PostgreSQL database
        cursor.close()

    return get_notification_item(conn, notification_id)


if __name__ == "__main__":
    conn = psycopg2.connect(
        host=BaseConfig.POSTGRES_URL,
        database=BaseConfig.POSTGRES_DB,
        user=BaseConfig.POSTGRES_USER,
        password=BaseConfig.POSTGRES_PW)
    print(update_notification_item(conn=conn, notification_id=7, count=10))
    #print(get_notification_item(conn=conn, notification_id=2))
    #print(get_items(conn=conn, table_name="notification", model=Notification))
    #print(get_items(conn=conn, table_name="attendee", model=Attendee))
    #print(get_items(conn=conn, table_name="conference", model=Conference))
