#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Telegram bot to play UNO in group chats
# Copyright (c) 2016 Jannes Höke <uno@jhoeke.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


from config import TOKEN, WORKERS
import logging
import os
import sqlite3

from pony.orm import db_session
from telegram.ext import Updater

from game_manager import GameManager
from database import db

db.bind('sqlite', os.getenv('UNO_DB', 'uno.sqlite3'), create_db=True)

# Add new column 'use_stickers' to UserSetting table if it doesn't exist
@db_session
def ensure_use_stickers_column():
    conn = sqlite3.connect(os.getenv('UNO_DB', 'uno.sqlite3'))
    cursor = conn.cursor()

    # Check if 'use_stickers' column exists
    cursor.execute("PRAGMA table_info(UserSetting);")
    columns = [row[1] for row in cursor.fetchall()]

    if 'use_stickers' not in columns:
        # Add the column with default True
        cursor.execute("ALTER TABLE UserSetting ADD COLUMN use_stickers BOOLEAN DEFAULT 1;")
        conn.commit()

    conn.close()

ensure_use_stickers_column()

db.generate_mapping(create_tables=True)

gm = GameManager()
updater = Updater(token=TOKEN, workers=WORKERS, use_context=True)
dispatcher = updater.dispatcher
