#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
working_with_s3.py
02 Nov 2020
Misc. functions within S3
"""

__author__ = 'Jack Vaughn'
__license__ = '0BSD'
__version__ = '0.1.0'
__maintainer__ = 'Jack Vaughn'
__email__ = 'jack.vaughn0523@gmail.com'
__status__ = 'Production'


from datetime import datetime
from random import randint
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from menu import Menu, MenuOption

s3 = boto3.resource('s3')


# --------------------- UTILITY FUNCTIONS ---------------------


def get_objects(bucket):
    """
    PROVIDE A LIST OF OBJECTS
    :param bucket: BUCKET THE OBJECTS BELONG TO
    :return: LIST OF STRINGS OF OBJECTS
    """
    return [obj.key for obj in s3.Bucket(bucket).objects.all()]


def get_buckets():
    """
    PROVIDE A LIST OF BUCKETS
    :return: LIST OF STRINGS OF BUCKETS
    """
    return [bucket.name for bucket in s3.buckets.all()]


def select(items, prompt):
    """
    PROVIDES A WAY OF SELECT ITEMS
    :param items: LIST OF ITEMS TO CHOOSE FROM
    :param prompt: PROMPT USE FOR INPUT
    :return: THE SELECTED ITEM OR FALSE IF ERROR
    """
    choices = {str(i): item for (i, item) in zip(range(len(items)), items)}
    if len(choices) == 0:
        print('No items to choose from.')
        return False

    [print(f"{key}: {value}") for key, value in choices.items()]
    print()
    choice = input(prompt)

    if choice in choices:
        return choices[choice]
    else:
        return False


def select_bucket(prompt):
    """
    PROMPT THE USER TO SELECT A BUCKET
    :param prompt: PROMPT USED TO REQUEST INPUT
    :return: RETURN BUCKET OF CHOICE OR FALSE IF ERROR
    """
    buckets = get_buckets()
    return select(buckets, prompt)


def select_object(bucket, prompt):
    """
    PROMPT THE USER TO SELECT AN OBJECT
    :param bucket: BUCKET TO SELECT OBJECT FROM
    :param prompt: PROMPT USED TO REQUEST INPUT
    :return: RETURN OBJECT OF CHOICE OR FALSE IF ERROR
    """
    objects = get_objects(bucket)
    return select(objects, prompt)


# --------------------- MENU FUNCTIONS ---------------------


def create_bucket():
    """
    CREATE A BUCKET USING FIRST NAME, LAST NAME, AND 6 RANDOM DIGITS
    :return: NULL
    """
    # GATHER NAMING INFORMATION
    first_name = input('Enter your first name: ').lower()
    last_name = input('Enter your last name: ').lower()
    ran_num = f'{randint(100000, 999999)}'
    bucket_name = f'{first_name}{last_name}{ran_num}'

    if len(f'{first_name}{last_name}') == 0:
        input('No name detected. Press enter to go back to the main menu.')
        return

    # CREATE BUCKET
    s3.create_bucket(Bucket=bucket_name)

    # CONFIRMATION
    if s3.Bucket(bucket_name) in s3.buckets.all():
        print(f'Bucket \'{bucket_name}\' created successfully!\n')
    else:
        print('Uh oh. Something went wrong...\n')

    input('Press enter to continue.\n')


def object_upload():
    """
    UPLOAD AN OBJECT TO A BUCKET
    :return: NULL
    """
    # SELECT BUCKET
    if not (bucket := select_bucket('Which bucket would you like to upload the file to: ')):
        input('Invalid bucket. Press enter to go back to the main menu.')
        return

    # SELECT FILE
    my_file = Path(input('What is the full path to the file you wish to upload: '))
    if not my_file.is_file():
        input(f'{my_file} is not a valid file path. Press enter to go back to the main menu.')
        return

    # UPLOAD FILE
    try:
        s3.meta.client.upload_file(str(my_file), bucket, my_file.name)
        print(f'{str(my_file)} has been uploaded to {bucket}.')
    except ClientError as e:
        print(e)
        print('Uh oh. Something went wrong...\n')

    input('Press enter to continue.')


def object_delete():
    """
    DELETE AN OBJECT FROM A BUCKET
    :return: NULL
    """
    # SELECT BUCKET
    if not (bucket := select_bucket('Which bucket would you like to delete the file from: ')):
        input('Invalid bucket. Press enter to go back to the main menu.')
        return

    # SELECT FILE
    if not (obj := select_object(bucket, 'Which object would you like to delete from the bucket: ')):
        input('Invalid object. Press enter to go back to the main menu.')
        return

    # DELETE FILE
    s3.Object(bucket, obj).delete()

    # CONFIRMATION
    if obj not in get_objects(bucket):
        print(f'{obj} has been deleted from {bucket}.')
    else:
        print('Uh oh. Something went wrong...\n')

    input('Press enter to continue.')


def bucket_delete():
    """
    DELETE A BUCKET
    :return: NULL
    """
    # SELECT BUCKET
    if not (bucket := select_bucket('Which bucket would you like to delete: ')):
        input('Invalid bucket. Press enter to go back to the main menu.')
        return

    # DELETE BUCKET
    s3.Bucket(bucket).objects.all().delete()
    s3.Bucket(bucket).delete()

    # CONFIRMATION
    if bucket not in get_buckets():
        print(f'{bucket} has been deleted.')
    else:
        print('Uh oh. Something went wrong...\n')

    input('Press enter to continue.')


def object_copy():
    """
    COPY AN OBJECT FROM ONE BUCKET TO ANOTHER
    :return: NULL
    """
    # SELECT SOURCE BUCKET
    if not (source_bucket := select_bucket('Which bucket would you like to copy the file from: ')):
        input('Invalid bucket. Press enter to go back to the main menu.')
        return

    # SELECT SOURCE FILE
    if not (obj := select_object(source_bucket, 'Which object would you like to copy from the bucket: ')):
        input('Invalid object. Press enter to go back to the main menu.')
        return

    # SELECT DESTINATION BUCKET
    if not (destination_bucket := select_bucket('Which bucket would you like to copy the file to: ')):
        input('Invalid bucket. Press enter to go back to the main menu.')
        return

    # COPY FILE
    copy_key = {
        'Bucket': source_bucket,
        'Key': obj
    }
    s3.meta.client.copy(copy_key, destination_bucket, obj)

    # CONFIRMATION
    if obj in get_objects(destination_bucket):
        print(f'{obj} has been copied from {source_bucket} to {destination_bucket}.')
    else:
        print('Uh oh. Something went wrong...\n')

    input('Press enter to continue.')


def object_download():
    """
    DOWNLOAD AN OBJECT FROM A BUCKET TO THE LOCAL FILESYSTEM
    :return: NULL
    """
    # SELECT BUCKET
    if not (bucket := select_bucket('Which bucket would you like to download a file from: ')):
        input('Invalid bucket. Press enter to go back to the main menu.')
        return

    # SELECT OBJECT
    if not (obj := select_object(bucket, 'Which object would you like to download from the bucket: ')):
        input('Invalid object. Press enter to go back to the main menu.')
        return

    # DOWNLOAD
    save_directory = Path(input('Enter the directory to save the file to: '))
    if not save_directory.is_dir():
        input('Invalid save directory. Press enter to go back to the main menu.')
        return

    save_full_path = Path(f'{save_directory}/{obj.split("/")[-1]}')

    s3.meta.client.download_file(bucket, obj, str(save_full_path))

    # CONFIRMATION
    if save_full_path.is_file():
        print(f'{obj} has been downloaded from {bucket} to {save_full_path}.')
    else:
        print('Uh oh. Something went wrong...\n')

    input('Press enter to continue.')


# --------------------- MENU ---------------------


app_name = 'Working with S3'
menu = Menu(
    prompt=f'\n********* Welcome to the  {app_name} Application *********\n'
           f'   What would you like to do?',
    menu_options={
        'a': MenuOption(
            menu_text='Create a bucket',
            confirmation_text='********* Create a bucket *********',
            alternatives=['A'],
            function=lambda: create_bucket()
        ),

        'b': MenuOption(
            menu_text='Upload an object to a bucket',
            confirmation_text='********* Upload an object to a bucket *********',
            alternatives=['B'],
            function=lambda: object_upload()
        ),

        'c': MenuOption(
            menu_text='Delete an object in a bucket',
            confirmation_text='********* Delete an object in a bucket *********',
            alternatives=['C'],
            function=lambda: object_delete()
        ),

        'd': MenuOption(
            menu_text='Delete a bucket',
            confirmation_text='********* Delete a bucket *********',
            alternatives=['D'],
            function=lambda: bucket_delete()
        ),

        'e': MenuOption(
            menu_text='Copy an object from one bucket to another',
            confirmation_text='********* Copy an object from one bucket to another *********',
            alternatives=['E'],
            function=lambda: object_copy()
        ),

        'f': MenuOption(
            menu_text='Download an existing object from a bucket',
            confirmation_text='********* Download an existing object from a bucket *********',
            alternatives=['F'],
            function=lambda: object_download()
        ),

        'g': MenuOption(
            menu_text='Exit the program',
            confirmation_text=f'Thanks for trying the {app_name} Application. It is currently {datetime.now()}',
            alternatives=['G', 'exit', 'quit', 'q'],
            exit_option=True
        )
    }
)
# CONTINUE LOOPING THROUGH THE MENU UNTIL THE USER EXITS
while not menu.should_exit:
    menu.show_prompt()
    menu.show()
    menu.choose_option()
