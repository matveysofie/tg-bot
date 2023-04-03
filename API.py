import hashlib
from config import db
from pymysql import MySQLError
from flask import Flask, jsonify, request

app = Flask(__name__)
cur = db.cursor()


@app.route('/call')
def list_classrooms():
    try:
        txt = []
        cur.execute(
            'SELECT filials.full_name, classrooms.number, classrooms.id FROM classrooms INNER JOIN filials ON classrooms.filial_id = filials.filial_id;')
        for r in cur.fetchall():
            txt.append({"id": r[2], "number": r[1], "filial": r[0]})
        return {"data": txt}
    except MySQLError as e:
        return e.args[0]


@app.route('/fall')
def list_filials():
    try:
        txt = []
        cur.execute(
            'SELECT id, full_name, coop_date FROM filials;')
        for r in cur.fetchall():
            txt.append({"id": r[0], "full_name": r[1], "coop_date": r[2]})
        return {"data": txt}
    except MySQLError as e:
        return e.args[0]


@app.route('/sall')
def list_students():
    try:
        txt = []
        cur.execute(
            'SELECT students.id, students.first_name, students.last_name, students.middle_name, students.college_date, filials.full_name FROM students INNER JOIN filials ON students.filial_id = filials.filial_id;')
        for r in cur.fetchall():
            txt.append({"id": r[0], "first_name": r[1], "last_name": r[2],
                        "middle_name": r[3], "college_date": r[4], "filial_full_name": r[5]})
        return {"data": txt}
    except MySQLError as e:
        return e.args[0]


@app.route('/tall')
def list_teachers():
    try:
        txt = []
        cur.execute(
            'SELECT teachers.id, teachers.first_name, teachers.last_name, teachers.middle_name, teachers.college_date, filials.full_name FROM teachers INNER JOIN filials ON teachers.filial_id = filials.filial_id;')
        for r in cur.fetchall():
            txt.append({"id": r[0], "first_name": r[1], "last_name": r[2],
                        "middle_name": r[3], "college_date": r[4], "filial_full_name": r[5]})
        return {"data": txt}
    except MySQLError as e:
        return e.args[0]


@app.route('/add/student', methods=['POST'])
def add_student():
    sid = hashlib.md5(
        (request.json['first_name'] + request.json['last_name'] + request.json['middle_name'] + request.json['college_date'] + str(request.content_length)).encode("utf-8")).hexdigest()
    qr = f"INSERT INTO `students` (`id`, `first_name`, `last_name`, `middle_name`, `college_date`, `student_id`, `filial_id`) VALUES (NULL, '{request.json['first_name']}', '{request.json['last_name']}', '{request.json['middle_name']}', '{request.json['college_date']}', '{sid}', '{request.json['filial_id']}'); "
    try:
        cur.execute(qr)
        db.commit()
        return {"success": True, "sid": sid}
    except MySQLError as e:
        return {"success": False, "error": e.args[0]}


@app.route('/add/teacher', methods=['POST'])
def add_teacher():
    tid = hashlib.md5(
        (request.json['first_name'] + request.json['last_name'] + request.json['middle_name'] + request.json['college_date'] + str(request.content_length)).encode("utf-8")).hexdigest()
    qr = f"INSERT INTO `teachers` (`id`, `first_name`, `last_name`, `middle_name`, `college_date`, `teacher_id`, `filial_id`) VALUES (NULL, '{request.json['first_name']}', '{request.json['last_name']}', '{request.json['middle_name']}', '{request.json['college_date']}', '{tid}', '{request.json['filial_id']}'); "
    try:
        cur.execute(qr)
        db.commit()
        return {"success": True, "tid": tid}
    except MySQLError as e:
        return {"success": False, "error": e.args[0]}


@app.route('/add/classroom', methods=['POST'])
def add_classroom():
    cid = hashlib.md5(str(str(request.json['number']) + str(request.json['is_tech']) + str(request.content_length)).encode(
        "utf-8")).hexdigest()
    qr = f"INSERT INTO `classrooms` (`id`, `is_tech`, `number`, `filial_id`, `classroom_id`) VALUES (NULL, '{request.json['is_tech']}', '{request.json['number']}', '{request.json['filial_id']}', '{cid}'); "
    try:
        cur.execute(qr)
        db.commit()
        return {"success": True, "cid": cid}
    except MySQLError as e:
        return {"success": False, "error": e.args[0]}


@app.route('/add/filial', methods=['POST'])
def add_filial():
    fid = hashlib.md5(str(str(request.json['full_name']) + str(request.json['coop_date']) + str(request.content_length)).encode(
        "utf-8")).hexdigest()
    qr = f"INSERT INTO `filials` (`id`, `full_name`, `coop_date`, `filial_id`) VALUES (NULL, '{request.json['full_name']}', '{request.json['coop_date']}', '{fid}'); "
    try:
        cur.execute(qr)
        db.commit()
        return {"success": True, "fid": fid}
    except MySQLError as e:
        return {"success": False, "error": e.args[0]}


@app.route('/del/filial', methods=['DELETE'])
def del_filial():
    try:
        cur.execute(
            f"DELETE FROM `filials` WHERE id = '{request.json['id']}';")
        db.commit()
        return {"success": True}
    except MySQLError as e:
        return {"success": False, "error": e.args[0]}


@app.route('/del/classroom', methods=['DELETE'])
def del_classroom():
    try:
        cur.execute(
            f"DELETE FROM `classrooms` WHERE id = '{request.json['id']}';")
        db.commit()
        return {"success": True}
    except MySQLError as e:
        return {"success": False, "error": e.args[0]}


@app.route('/del/student', methods=['DELETE'])
def del_student():
    try:
        cur.execute(
            f"DELETE FROM `students` WHERE id = '{request.json['id']}';")
        db.commit()
        return {"success": True}
    except MySQLError as e:
        return {"success": False, "error": e.args[0]}


@app.route('/del/teacher', methods=['DELETE'])
def del_teacher():
    try:
        cur.execute(
            f"DELETE FROM `teachers` WHERE id = '{request.json['id']}';")
        db.commit()
        return {"success": True}
    except MySQLError as e:
        return {"success": False, "error": e.args[0]}


@app.route('/upd/filial', methods=['PUT'])
def upd_filial():
    try:
        cur.execute(
            f"UPDATE `filials` SET `full_name` = '{request.json['full_name']}', `coop_date` = '{request.json['coop_date']}' WHERE `filials`.`id` = {request.json['id']}; ")
        db.commit()
        return {"success": True}
    except MySQLError as e:
        return {"success": False, "error": e.args[0]}


@app.route('/upd/classroom', methods=['PUT'])
def upd_classroom():
    try:
        cur.execute(
            f"UPDATE `classrooms` SET `is_tech` = '{request.json['is_tech']}', `number` = '{request.json['number']}' WHERE `classrooms`.`id` = {request.json['id']}; ")
        db.commit()
        return {"success": True}
    except MySQLError as e:
        return {"success": False, "error": e.args[0]}


@app.route('/upd/student', methods=['PUT'])
def upd_student():
    try:
        cur.execute(
            f"UPDATE `students` SET `first_name` = '{request.json['first_name']}', `last_name` = '{request.json['last_name']}', `middle_name` = '{request.json['middle_name']}', `college_date` = '{request.json['college_date']}' WHERE `students`.`id` = {request.json['id']}; ")
        db.commit()
        return {"success": True}
    except MySQLError as e:
        return {"success": False, "error": e.args[0]}


@app.route('/upd/teacher', methods=['PUT'])
def upd_teacher():
    try:
        cur.execute(
            f"UPDATE `teachers` SET `first_name`='{request.json['first_name']}', `last_name`='{request.json['last_name']}', `middle_name`='{request.json['middle_name']}', `college_date`='{request.json['college_date']}' WHERE `teachers`.`id`={request.json['id']};")
        db.commit()
        return {"success": True}
    except MySQLError as e:
        return {"success": False, "error": e.args[0]}


@app.route('/list/classrooms')
def list_classrooms_by_filial():
    txt = []
    try:
        cur.execute(
            f"SELECT id, number, is_tech FROM classrooms WHERE classrooms.filial_id = '{request.json['filial_id']}' ")
        for r in cur.fetchall():
            txt.append({"id": r[0], "number": r[1], "is_tech": r[2]})
        return {"success": True, "data": txt}
    except MySQLError as e:
        return {"success": False, "error": e.args[0]}


@app.route('/list/students')
def list_students_by_filial():
    txt = []
    try:
        cur.execute(
            f"SELECT id, first_name, last_name, middle_name, college_date FROM students WHERE students.filial_id = '{request.json['filial_id']}' ")
        for r in cur.fetchall():
            txt.append({"id": r[0], "first_name": r[1], "last_name": r[1],
                        "middle_name": r[3], "college_date": r[4]})
        return {"success": True, "data": txt}
    except MySQLError as e:
        return {"success": False, "error": e.args[0]}


@app.route('/list/teachers')
def list_teachers_by_filial():
    txt = []
    try:
        cur.execute(
            f"SELECT id, first_name, last_name, middle_name, college_date FROM teachers WHERE teachers.filial_id = '{request.json['filial_id']}' ")
        for r in cur.fetchall():
            txt.append({"id": r[0], "first_name": r[1], "last_name": r[1],
                        "middle_name": r[3], "college_date": r[4]})
        return {"success": True, "data": txt}
    except MySQLError as e:
        return {"success": False, "error": e.args[0]}


if __name__ == "__main__":
    app.run()
