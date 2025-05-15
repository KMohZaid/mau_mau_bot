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


from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, Update)
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler)

from utils import send_async
from user_setting import UserSetting
from shared_vars import dispatcher
from locales import available_locales
from internationalization import _, user_locale

@user_locale
def toggle_stickers(update: Update, context: CallbackContext):
    """Ask for confirmation to toggle stickers/image previews"""
    user_id = update.message.from_user.id
    us = UserSetting.get(id=user_id)

    if not us:
        us = UserSetting(id=user_id)

    if us.use_stickers:
        text = _("Currently using:\n✅ Stickers\n❌ Image previews\n\nDo you want to switch to image previews?")
    else:
        text = _("Currently using:\n❌ Stickers\n✅ Image previews\n\nDo you want to switch to stickers?")

    keyboard = [
        [InlineKeyboardButton(_("Yes, switch"), callback_data="use_stickers_confirm")],
        [InlineKeyboardButton(_("Cancel"), callback_data="use_stickers_cancel")]

    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    send_async(
        context.bot,
        update.message.chat.id,
        text=text,
        reply_markup=reply_markup
    )

@user_locale
def toggle_stickers_confirm(update: Update, context: CallbackContext):
    """Handles the confirmation to toggle the setting"""
    query = update.callback_query
    user_id = query.from_user.id
    us = UserSetting.get(id=user_id)

    # Ensure that user himself is clicking the button
    # TODO

    if query.data == "use_stickers_confirm":
        us.use_stickers = not us.use_stickers
        if us.use_stickers:
            text = _("Switched to using stickers!")
        else:
            text = _("Switched to using image previews!")
    else:
        text = _("Cancelled.")

    query.answer()
    query.edit_message_text(text=text)

@user_locale
def show_settings(update: Update, context: CallbackContext):
    chat = update.message.chat

    if update.message.chat.type != 'private':
        send_async(context.bot, chat.id,
                   text=_("Please edit your settings in a private chat with "
                          "the bot."))
        return

    us = UserSetting.get(id=update.message.from_user.id)

    if not us:
        us = UserSetting(id=update.message.from_user.id)

    if not us.stats:
        stats = '📊' + ' ' + _("Enable statistics")
    else:
        stats = '❌' + ' ' + _("Delete all statistics")

    kb = [[stats], ['🌍' + ' ' + _("Language")]]
    send_async(context.bot, chat.id, text='🔧' + ' ' + _("Settings"),
               reply_markup=ReplyKeyboardMarkup(keyboard=kb,
                                                one_time_keyboard=True))


@user_locale
def kb_select(update: Update, context: CallbackContext):
    chat = update.message.chat
    user = update.message.from_user
    option = context.match[1]

    if option == '📊':
        us = UserSetting.get(id=user.id)
        us.stats = True
        send_async(context.bot, chat.id, text=_("Enabled statistics!"))

    elif option == '🌍':
        kb = [[locale + ' - ' + descr]
              for locale, descr
              in sorted(available_locales.items())]
        send_async(context.bot, chat.id, text=_("Select locale"),
                   reply_markup=ReplyKeyboardMarkup(keyboard=kb,
                                                    one_time_keyboard=True))

    elif option == '❌':
        us = UserSetting.get(id=user.id)
        us.stats = False
        us.first_places = 0
        us.games_played = 0
        us.cards_played = 0
        send_async(context.bot, chat.id, text=_("Deleted and disabled statistics!"))


@user_locale
def locale_select(update: Update, context: CallbackContext):
    chat = update.message.chat
    user = update.message.from_user
    option = context.match[1]

    if option in available_locales:
        us = UserSetting.get(id=user.id)
        us.lang = option
        _.push(option)
        send_async(context.bot, chat.id, text=_("Set locale!"))
        _.pop()

def register():
    dispatcher.add_handler(CommandHandler("toggle_stickers", toggle_stickers))
    dispatcher.add_handler(CommandHandler('settings', show_settings))
    dispatcher.add_handler(MessageHandler(Filters.regex('^([' + '📊' +
                                                        '🌍' +
                                                        '❌' + ']) .+$'),
                                        kb_select))
    dispatcher.add_handler(MessageHandler(Filters.regex(r'^(\w\w_\w\w) - .*'),
                                        locale_select))
