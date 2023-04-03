import telebot
import pymysql
import hashlib
import config
from telebot import types
from config import db
from pymysql import MySQLError


cur = db.cursor()

bot = telebot.TeleBot(config.telegram_key)


@bot.message_handler(commands=['fall'])
def command_fall(message):
    cur.execute('SELECT full_name, coop_date FROM filials')
    for r in cur.fetchall():
        bot.send_message(message.chat.id, '{} - {}'.format(r[0], r[1]))


@bot.message_handler(commands=['call'])
def command_call(message):
    txt = []
    cur.execute('SELECT filials.full_name, classrooms.number FROM classrooms INNER JOIN filials ON classrooms.filial_id = filials.filial_id')
    for r in cur.fetchall():
        txt.append('Аудитория <b> {} </b> расположена в {}'.format(r[1], r[0]))
    bot.send_message(message.chat.id, text='\n\n'.join(txt), parse_mode='html')


@bot.message_handler(commands=['sall'])
def command_sall(message):
    txt = []
    cur.execute('SELECT filials.full_name, students.first_name, students.last_name, students.middle_name, students.college_date FROM students INNER JOIN filials ON students.filial_id = filials.filial_id')
    for r in cur.fetchall():
        txt.append(
            'Студент <b> {} {} {} </b> обучается в филиале {} с {}'.format(r[2], r[1], r[3], r[0], r[4]))
    bot.send_message(message.chat.id, text='\n\n'.join(txt), parse_mode='html')


@bot.message_handler(commands=['tall'])
def command_tall(message):
    txt = []
    cur.execute('SELECT filials.full_name, teachers.first_name, teachers.last_name, teachers.middle_name, teachers.college_date FROM teachers INNER JOIN filials ON teachers.filial_id = filials.filial_id')
    for r in cur.fetchall():
        txt.append(
            'Педагог <b> {} {} {} </b> преподает в филиале {} с {}'.format(r[2], r[1], r[3], r[0], r[4]))
    bot.send_message(message.chat.id, text='\n\n'.join(txt), parse_mode='html')


@bot.message_handler(commands=['add'])
def add_command_switch(message):
    mk = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    mk.add('Добавить филиал', 'Добавить аудиторию',
           'Добавить преподавателя', 'Добавить студента')
    msg = bot.send_message(
        message.chat.id, text='Выберите действие', reply_markup=mk)
    bot.register_next_step_handler(msg, add_command_choose)


def add_command_choose(message):
    if message.text == u'Добавить филиал':
        msg = bot.send_message(
            message.chat.id, text='Введите полное название филиала и его дату присоединения в формете гггг-мм-дд, разделив их символом "/" например, например ФГБОУ "РЭУ им. Г.В. Плеханова"/2018-12-1', parse_mode='html')
        bot.register_next_step_handler(msg, add_f)
    elif message.text == u'Добавить аудиторию':
        cur.execute('SELECT full_name, id FROM filials')
        mk = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for r in cur.fetchall():
            mk.add('{} - {}'.format(r[1], r[0]))
        msg = bot.send_message(
            message.chat.id, text='Выберите филиал', reply_markup=mk)
        bot.register_next_step_handler(msg, add_a)
    elif message.text == u'Добавить преподавателя':
        cur.execute('SELECT full_name, id FROM filials')
        mk = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for r in cur.fetchall():
            mk.add('{} - {}'.format(r[1], r[0]))
        msg = bot.send_message(
            message.chat.id, text='Выберите филиал', reply_markup=mk)
        bot.register_next_step_handler(msg, add_t)
    elif message.text == u'Добавить студента':
        cur.execute('SELECT full_name, id FROM filials')
        mk = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for r in cur.fetchall():
            mk.add('{} - {}'.format(r[1], r[0]))
        msg = bot.send_message(
            message.chat.id, text='Выберите филиал', reply_markup=mk)
        bot.register_next_step_handler(msg, add_s)
    else:
        bot.send_message(
            message.chat.id, text='Но-но-но...')


def add_f(message):
    fi = message.text.split('/')
    fid = hashlib.md5(
        (str(fi[0]) + str(fi[1]) + str(message.message_id)).encode("utf-8")).hexdigest()
    qr = f"INSERT INTO `filials` (`id`, `full_name`, `coop_date`, `filial_id`) VALUES (NULL, '{fi[0]}', '{fi[1]}', '{fid}'); "
    try:
        cur.execute(qr)
        db.commit()
        bot.send_message(
            message.chat.id, text='Филиал <b>успешно</b> зарегистрирован!', parse_mode='html')
    except MySQLError as e:
        bot.send_message(
            message.chat.id, text=e.args[0])


def add_a(message):
    fid = message.text.split()[0]
    msg = bot.send_message(
        message.chat.id, text='Введите физический номер аудитории, указав через пробел является ли она технической (вар. 0/1), 115 1 или 302 0', parse_mode='html')
    try:
        cur.execute(f'SELECT filial_id FROM `filials` WHERE `id` = {fid} ')
        fhash = cur.fetchall()
    except:
        bot.send_message(message.chat.id, text="Но-но-но...")
    bot.register_next_step_handler(msg, insert_classroom, fhash)


def add_s(message):
    fid = message.text.split()[0]
    msg = bot.send_message(
        message.chat.id, text='Введите фамилию, имя, отчество студента, дату поступления, разделив их символом "/", например Кулиев Алижон Денисович/2019-10-12', parse_mode='html')
    try:
        cur.execute(f'SELECT filial_id FROM `filials` WHERE `id` = {fid} ')
        fhash = cur.fetchall()
    except:
        bot.send_message(message.chat.id, text="Но-но-но...")
    bot.register_next_step_handler(msg, insert_student, fhash)


def add_t(message):
    fid = message.text.split()[0]
    msg = bot.send_message(
        message.chat.id, text='Введите фамилию, имя, отчество преподавателя, дату начала сотрудничества, разделив их символом "/", например Ключник Владлен Иванович/2019-10-12', parse_mode='html')
    try:
        cur.execute(f'SELECT filial_id FROM `filials` WHERE `id` = {fid} ')
        fhash = cur.fetchall()
    except:
        bot.send_message(message.chat.id, text="Но-но-но...")
    bot.register_next_step_handler(msg, insert_teacher, fhash)


def insert_classroom(message, *args):
    ci = message.text.split()
    cid = hashlib.md5(
        (str(ci[0]) + str(ci[1]) + str(message.message_id)).encode("utf-8")).hexdigest()
    qr = f"INSERT INTO `classrooms` (`id`, `is_tech`, `number`, `filial_id`, `classroom_id`) VALUES (NULL, '{ci[1]}', '{ci[0]}', '{args[0][0][0]}', '{cid}'); "
    try:
        cur.execute(qr)
        db.commit()
        bot.send_message(
            message.chat.id, text='Аудитория <b>успешно</b> зарегистрирована!', parse_mode='html')
    except MySQLError as e:
        bot.send_message(
            message.chat.id, text=e.args[0])


def insert_teacher(message, *args):
    ti = message.text.split('/')
    tcr = ti[0].split()
    tid = hashlib.md5(
        (str(ti[0]) + str(ti[1]) + str(message.message_id)).encode("utf-8")).hexdigest()
    qr = f"INSERT INTO `teachers` (`id`, `last_name`, `first_name`, `middle_name`, `college_date`, `filial_id`, `teacher_id`) VALUES (NULL, '{tcr[0]}', '{tcr[1]}', '{tcr[2]}', '{ti[1]}', '{args[0][0][0]}', '{tid}'); "
    try:
        cur.execute(qr)
        db.commit()
        bot.send_message(
            message.chat.id, text='Преподаватель <b>успешно</b> зарегистрирован!', parse_mode='html')
    except MySQLError as e:
        bot.send_message(
            message.chat.id, text=e.args[0])


def insert_student(message, *args):
    si = message.text.split('/')
    scr = si[0].split()
    sid = hashlib.md5(
        (str(si[0]) + str(si[1]) + str(message.message_id)).encode("utf-8")).hexdigest()
    qr = f"INSERT INTO `students` (`id`, `last_name`, `first_name`, `middle_name`, `college_date`, `filial_id`, `student_id`) VALUES (NULL, '{scr[0]}', '{scr[1]}', '{scr[2]}', '{si[1]}', '{args[0][0][0]}', '{sid}'); "
    try:
        cur.execute(qr)
        db.commit()
        bot.send_message(
            message.chat.id, text='Студент <b>успешно</b> зарегистрирован!', parse_mode='html')
    except MySQLError as e:
        bot.send_message(message.chat.id, text=e.args[0])


@bot.message_handler(commands=['del'])
def del_command_switch(message):
    mk = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    mk.add('Удалить филиал', 'Удалить аудиторию',
           'Удалить преподавателя', 'Удалить студента')
    msg = bot.send_message(
        message.chat.id, text='Выберите действие', reply_markup=mk)
    bot.register_next_step_handler(msg, del_command_choose)


def del_command_choose(message):
    if message.text == u'Удалить филиал':
        cur.execute('SELECT full_name, id FROM filials')
        mk = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for r in cur.fetchall():
            mk.add('{} - {}'.format(r[1], r[0]))
        msg = bot.send_message(
            message.chat.id, text='Выберите филиал', reply_markup=mk)
        bot.register_next_step_handler(msg, del_f)
    elif message.text == u'Удалить аудиторию':
        cur.execute('SELECT filials.full_name, classrooms.number, classrooms.id FROM classrooms INNER JOIN filials ON classrooms.filial_id = filials.filial_id')
        mk = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for r in cur.fetchall():
            mk.add('{} - {} - {}'.format(r[2], r[1], r[0]))
        msg = bot.send_message(
            message.chat.id, text='Выберите филиал', reply_markup=mk)
        bot.register_next_step_handler(msg, del_c)
    elif message.text == u'Удалить преподавателя':
        cur.execute('SELECT teachers.first_name, teachers.last_name, teachers.middle_name, teachers.id, filials.full_name FROM teachers INNER JOIN filials ON teachers.filial_id = filials.filial_id')
        mk = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for r in cur.fetchall():
            tc = f'{r[1]} {r[0]} {r[2]}'
            mk.add('{} - {} из {}'.format(r[3], tc, r[4]))
        msg = bot.send_message(
            message.chat.id, text='Выберите преподавателя', reply_markup=mk)
        bot.register_next_step_handler(msg, del_t)
    elif message.text == u'Удалить студента':
        cur.execute('SELECT students.first_name, students.last_name, students.middle_name, students.id, filials.full_name FROM students INNER JOIN filials ON students.filial_id = filials.filial_id')
        mk = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for r in cur.fetchall():
            tc = f'{r[1]} {r[0]} {r[2]}'
            mk.add('{} - {} из {}'.format(r[3], tc, r[4]))
        msg = bot.send_message(
            message.chat.id, text='Выберите студента', reply_markup=mk)
        bot.register_next_step_handler(msg, del_s)
    else:
        bot.send_message(
            message.chat.id, text='Но-но-но...')


def del_f(message):
    fid = message.text.split()[0]
    try:
        cur.execute(
            f"DELETE FROM `filials` WHERE id = '{fid}';")
        db.commit()
        bot.send_message(
            message.chat.id, text='Филиал <b>успешно</> удален!', parse_mode='html')
    except MySQLError as e:
        bot.send_message(
            message.chat.id, text=e.args[0])


def del_c(message):
    fid = message.text.split()[0]
    try:
        cur.execute(
            f"DELETE FROM `classrooms` WHERE id = '{fid}';")
        db.commit()
        bot.send_message(
            message.chat.id, text='Аудитория <b>успешно</> удалена!', parse_mode='html')
    except MySQLError as e:
        bot.send_message(
            message.chat.id, text=e.args[0])


def del_s(message):
    fid = message.text.split()[0]
    try:
        cur.execute(
            f"DELETE FROM `students` WHERE id = '{fid}';")
        db.commit()
        bot.send_message(
            message.chat.id, text='Студент <b>успешно</> удален!', parse_mode='html')
    except MySQLError as e:
        bot.send_message(
            message.chat.id, text=e.args[0])


def del_t(message):
    fid = message.text.split()[0]
    try:
        cur.execute(
            f"DELETE FROM `teachers` WHERE id = '{fid}';")
        db.commit()
        bot.send_message(
            message.chat.id, text='Преподаватель <b>успешно</> удален!', parse_mode='html')
    except MySQLError as e:
        bot.send_message(
            message.chat.id, text=e.args[0])


@bot.message_handler(commands=['upd'])
def upd_command_switch(message):
    mk = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    mk.add('Изменить филиал', 'Изменить аудиторию',
           'Изменить преподавателя', 'Изменить студента')
    msg = bot.send_message(
        message.chat.id, text='Выберите действие', reply_markup=mk)
    bot.register_next_step_handler(msg, upd_command_choose)


def upd_command_choose(message):
    if message.text == u'Изменить филиал':
        cur.execute('SELECT full_name, id FROM filials')
        mk = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for r in cur.fetchall():
            mk.add('{} - {}'.format(r[1], r[0]))
        msg = bot.send_message(
            message.chat.id, text='Выберите филиал', reply_markup=mk)
        bot.register_next_step_handler(msg, upd_f)
    elif message.text == u'Изменить аудиторию':
        cur.execute('SELECT filials.full_name, classrooms.number, classrooms.id FROM classrooms INNER JOIN filials ON classrooms.filial_id = filials.filial_id')
        mk = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for r in cur.fetchall():
            mk.add('{} - {} - {}'.format(r[2], r[1], r[0]))
        msg = bot.send_message(
            message.chat.id, text='Выберите аудиторию', reply_markup=mk)
        bot.register_next_step_handler(msg, upd_c)
    elif message.text == u'Изменить преподавателя':
        cur.execute('SELECT teachers.first_name, teachers.last_name, teachers.middle_name, teachers.id, filials.full_name FROM teachers INNER JOIN filials ON teachers.filial_id = filials.filial_id')
        mk = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for r in cur.fetchall():
            tc = f'{r[1]} {r[0]} {r[2]}'
            mk.add('{} - {} из {}'.format(r[3], tc, r[4]))
        msg = bot.send_message(
            message.chat.id, text='Выберите преподавателя', reply_markup=mk)
        bot.register_next_step_handler(msg, upd_t)
    elif message.text == u'Изменить студента':
        cur.execute('SELECT students.first_name, students.last_name, students.middle_name, students.id, filials.full_name FROM students INNER JOIN filials ON students.filial_id = filials.filial_id')
        mk = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for r in cur.fetchall():
            tc = f'{r[1]} {r[0]} {r[2]}'
            mk.add('{} - {} из {}'.format(r[3], tc, r[4]))
        msg = bot.send_message(
            message.chat.id, text='Выберите студента', reply_markup=mk)
        bot.register_next_step_handler(msg, upd_s)
    else:
        bot.send_message(
            message.chat.id, text='Но-но-но...')


def upd_f(message):
    fid = message.text.split()[0]
    msg = bot.send_message(
        message.chat.id, text='Введите полное название филиала и его дату присоединения в формете гггг-мм-дд, разделив их символом "/" например, например ФГБОУ "РЭУ им. Г.В. Плеханова"/2018-12-01', parse_mode='html')
    bot.register_next_step_handler(msg, upd_insert_filial, fid)


def upd_insert_filial(message, *args):
    fi = message.text.split("/")
    try:
        cur.execute(
            f"UPDATE `filials` SET `full_name` = '{fi[0]}', `coop_date` = '{fi[1]}' WHERE `filials`.`id` = {args[0]}; ")
        db.commit()
        bot.send_message(
            message.chat.id, text='Филиал <b>успешно</> отредактирован и обновлен!', parse_mode='html')
    except MySQLError as e:
        bot.send_message(
            message.chat.id, text=e.args[0])


def upd_c(message):
    cid = message.text.split()[0]
    msg = bot.send_message(
        message.chat.id, text='Введите физический номер аудитории, указав через пробел является ли она технической (вар. 0/1), 115 1 или 302 0', parse_mode='html')
    bot.register_next_step_handler(msg, upd_insert_classroom, cid)


def upd_insert_classroom(message, *args):
    ci = message.text.split()
    try:
        cur.execute(
            f"UPDATE `classrooms` SET `is_tech` = '{ci[1]}', `number` = '{ci[0]}' WHERE `classrooms`.`id` = {args[0][0][0]}; ")
        db.commit()
        bot.send_message(
            message.chat.id, text='Аудитория <b>успешно</> отредактирована и обновлена!', parse_mode='html')
    except MySQLError as e:
        bot.send_message(
            message.chat.id, text=e.args[0])


def upd_s(message):
    cid = message.text.split()[0]
    msg = bot.send_message(
        message.chat.id, text='Введите фамилию, имя, отчество студента, дату поступления, разделив их символом "/", например Кулиев Алижон Денисович/2019-10-12', parse_mode='html')
    bot.register_next_step_handler(msg, upd_insert_student, cid)


def upd_insert_student(message, *args):
    ti = message.text.split('/')
    tcr = ti[0].split()
    qr = f"UPDATE `students` SET `first_name` = '{tcr[1]}', `last_name` = '{tcr[0]}', `middle_name` = '{tcr[2]}', `college_date` = '{ti[1]}' WHERE `students`.`id` = {args[0]}; "
    try:
        cur.execute(qr)
        db.commit()
        bot.send_message(
            message.chat.id, text='Студент <b>успешно</b> отредактирован и обновлен!', parse_mode='html')
    except MySQLError as e:
        bot.send_message(
            message.chat.id, text=e.args[0])


def upd_t(message):
    cid = message.text.split()[0]
    msg = bot.send_message(
        message.chat.id, text='Введите фамилию, имя, отчество преподавателя, дату начала сотрудничества, разделив их символом "/", например Ключник Владлен Иванович/2019-10-12', parse_mode='html')
    bot.register_next_step_handler(msg, upd_insert_teacher, cid)


def upd_insert_teacher(message, *args):
    ti = message.text.split('/')
    tcr = ti[0].split()
    qr = f"UPDATE `teachers` SET `first_name` = '{tcr[1]}', `last_name` = '{tcr[0]}', `middle_name` = '{tcr[2]}', `college_date` = '{ti[1]}' WHERE `teachers`.`id` = {args[0]}; "
    try:
        cur.execute(qr)
        db.commit()
        bot.send_message(
            message.chat.id, text='Преподаватель <b>успешно</b> отредактирован и обновлен!', parse_mode='html')
    except MySQLError as e:
        bot.send_message(
            message.chat.id, text=e.args[0])


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)


bot.polling()
