import os
import datetime
import hashlib
from bs4 import BeautifulSoup
import json, sys, glob, subprocess, shlex, shutil
from flask import Flask, session, url_for, redirect, render_template, request, abort, flash, send_from_directory
from database import list_users, verify, delete_user_from_db, add_user
from database import read_note_from_db, write_note_into_db, delete_note_from_db, match_user_id_with_note_id
from database import image_upload_record, list_images_for_user, match_user_id_with_image_uid, delete_image_from_db
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin



app = Flask(__name__)
app.config.from_object('config')
CORS(app)



@app.errorhandler(401)
def FUN_401(error):
    return render_template("page_401.html"), 401

@app.errorhandler(403)
def FUN_403(error):
    return render_template("page_403.html"), 403

@app.errorhandler(404)
def FUN_404(error):
    return render_template("page_404.html"), 404

@app.errorhandler(405)
def FUN_405(error):
    return render_template("page_405.html"), 405

@app.errorhandler(413)
def FUN_413(error):
    return render_template("page_413.html"), 413





@app.route("/")
def FUN_root():
    return render_template("index.html")

@app.route("/public/")
def FUN_public():
    return render_template("public_page.html")

@app.route('/result/output/<path:filename>')
def custom_static(filename):
    return send_from_directory('output', filename)

@app.route('/result/<path:filename>')
def custom_static1(filename):
    return send_from_directory('.', filename)

@app.route("/result/")
def FUN_result():
    # return render_template("index.html")
    return send_from_directory('.', 'index.html')

@app.route("/private/")
def FUN_private():
    if "current_user" in session.keys():
        notes_list = read_note_from_db(session['current_user'])
        notes_table = zip([x[0] for x in notes_list],\
                          [x[1] for x in notes_list],\
                          [x[2] for x in notes_list],\
                          ["/delete_note/" + x[0] for x in notes_list])

        images_list = list_images_for_user(session['current_user'])
        images_table = zip([x[0] for x in images_list],\
                          [x[1] for x in images_list],\
                          [x[2] for x in images_list],\
                          ["/delete_image/" + x[0] for x in images_list])

        return render_template("private_page.html", notes = notes_table, images = images_table)
    else:
        return abort(401)

@app.route("/admin/")
def FUN_admin():
    if session.get("current_user", None) == "ADMIN":
        user_list = list_users()
        user_table = zip(range(1, len(user_list)+1),\
                        user_list,\
                        [x + y for x,y in zip(["/delete_user/"] * len(user_list), user_list)])
        return render_template("admin.html", users = user_table)
    else:
        return abort(401)

@app.route("/write_note", methods = ["POST"])
def FUN_write_note():
    text_to_write = request.form.get("text_note_to_take")
    write_note_into_db(session['current_user'], text_to_write)

    return(redirect(url_for("FUN_private")))

@app.route("/iters", methods = ["POST"])
def FUN_iters_write():
    iters_to_write = request.form.get("iters_take")
    session['iters_to_write'] = iters_to_write
    return ('', 204)

@app.route("/primitive", methods = ["POST"])
def FUN_prime_write():
    prime_to_write = request.form.get("prime_take")
    session['prime_to_write'] = prime_to_write
    return ('', 204)

@app.route("/size", methods = ["POST"])
def FUN_size_write():
    size_to_write = request.form.get("size_take")
    session['size_to_write'] = size_to_write
    return ('', 204)

@app.route("/processing", methods = ["POST"])
def FUN_processing():
  # папки вывода json
  output_directory = 'output'
  folder = 'output'
  # Пост запросы от ползунков в privatepage
  iters = session.get('iters_to_write')
  prime = session.get('prime_to_write')
  for the_file in os.listdir(folder):
    file_path = os.path.join(folder, the_file)
    try:
      if os.path.isfile(file_path):
          os.unlink(file_path)
      #elif os.path.isdir(file_path): shutil.rmtree(file_path)
    except Exception as e:
      print(e)
  size = session.get('size_to_write')
  svgs = []
  input_images = glob.glob('image_pool/*')

# конвертируем в svg вызовом на Go
  def img_to_svg(img):
    basename = os.path.basename(img)
    new_name = os.path.splitext(basename)[0] + '.svg'
    out_file = os.path.join(output_directory, new_name)
    call =  'primitive -i ' + img 
    call += ' -o ' + out_file
    call += ' -r ' + size
    call += ' -s ' + size
    call += ' -n ' + iters 
    call += ' -m ' + prime

    print(' * Process Run', call)
    sholl = call
    print(sholl.split())
    subprocess.call(shlex.split(call))
    return out_file
  
  # svg в json вручную, подходящий для d3js
  def svg_to_json(svg):
    outsv = svg.replace("\\", "")
    filename = os.path.basename(svg)
    data = {
      'svg': {},
      'group': {},
      'rect': {},
      'points': [],
      'name': filename
    }
  
    
    with open(outsv) as f:
      f = f.read()
      soup = BeautifulSoup(f, 'lxml')
  
      svg_elem = soup.find('svg')
      data['svg'] = {
        'width': svg_elem['width'],
        'height': svg_elem['height']
      }
  
      group = soup.find('g')
      data['group'] = {
        'transform': group['transform']
      } 
  
      rect = soup.find('rect')
      data['rect'] = {
        'x': rect['x'],
        'y': rect['y'],
        'width': rect['width'],
        'height': rect['height'],
        'fill': rect['fill']
      }
  
      point_attributes = ['fill', 'fill-opacity', 'cx', 'cy', 'rx', 'ry']
      points = soup.find_all('ellipse')
      for i in points:
        observation = {}
        for a in point_attributes:
          observation[a] = i[a]
        data['points'].append(observation)
  
    output_filename = filename.replace('.svg', '.json')
    outfile = os.path.join(output_directory, output_filename)
    print(outfile)
    with open(outfile, 'w') as out:
      json.dump(data, out)

  for filename in os.listdir("image_pool"): 
    dst ="image_pool" + filename
    src ='image_pool/'+ filename 
    shutil.copy2(src, dst)

  for i in input_images:
    svgs.append(img_to_svg(i))

  for i in svgs:
    svg_to_json(i)
# сохраняем пути для json в массив js файла, как функцию, который вызовем в result
  f = open('listdir.js', 'w')
  listdir = os.listdir('output')
  dirs = []
  for elem in listdir:
    dirs.append("/output/" + elem)
  f.write("var inputs = " + json.dumps(dirs))
  f.close()

  return(redirect("http://localhost:7000/"))
  # return send_from_directory('.', 'index.html')

@app.route("/result/listdir")
@cross_origin()
def listdir():
	return json.dumps(os.listdir('output'))




@app.route("/delete_note/<note_id>", methods = ["GET"])
def FUN_delete_note(note_id):
    if session.get("current_user", None) == match_user_id_with_note_id(note_id): # проверяем id надписи и user
        delete_note_from_db(note_id)
    else:
        return abort(401)
    return(redirect(url_for("FUN_private")))


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload_image", methods = ['POST'])
def FUN_upload_image():
    if request.method == 'POST':
        # проверка содержит ли пост запрос файл
        if 'file' not in request.files:
            flash('No file part')
            return(redirect(url_for("FUN_private")))
        file = request.files['file']
        # если нет, все равно вернем пустой
        if file.filename == '':
            flash('No selected file')
            return(redirect(url_for("FUN_private")))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_time = str(datetime.datetime.now())
            image_uid = hashlib.sha1((upload_time + filename).encode()).hexdigest()
            # сохраняем картинку в папку
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_uid + "-" + filename))
            # записываем в БД
            image_upload_record(image_uid, session['current_user'], filename, upload_time)
            return(redirect(url_for("FUN_private")))

    return(redirect(url_for("FUN_private")))


@app.route("/delete_image/<image_uid>", methods = ["GET"])
def FUN_delete_image(image_uid):
    if session.get("current_user", None) == match_user_id_with_image_uid(image_uid): # Ensure the current user is NOT operating on other users' note.
        # удаляем связанную запись из бд
        delete_image_from_db(image_uid)
        # удаляем файл из папки
        image_to_delete_from_pool = [y for y in [x for x in os.listdir(app.config['UPLOAD_FOLDER'])] if y.split("-", 1)[0] == image_uid][0]
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image_to_delete_from_pool))
    else:
        return abort(401)
    return(redirect(url_for("FUN_private")))

@app.route("/login", methods = ["POST"])
def FUN_login():
    id_submitted = request.form.get("id").upper()
    if (id_submitted in list_users()) and verify(id_submitted, request.form.get("pw")):
        session['current_user'] = id_submitted
    
    return(redirect(url_for("FUN_root")))

@app.route("/logout/")
def FUN_logout():
    session.pop("current_user", None)
    return(redirect(url_for("FUN_root")))

@app.route("/delete_user/<id>/", methods = ['GET'])
def FUN_delete_user(id):
    if session.get("current_user", None) == "ADMIN":
        if id == "ADMIN": # ADMIN нельзя удалить
            return abort(403)

        # [1] удаляем изображения этого юзера из папки
        images_to_remove = [x[0] for x in list_images_for_user(id)]
        for f in images_to_remove:
            image_to_delete_from_pool = [y for y in [x for x in os.listdir(app.config['UPLOAD_FOLDER'])] if y.split("-", 1)[0] == f][0]
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image_to_delete_from_pool))
        # [2] удаляем записи
        delete_user_from_db(id)
        return(redirect(url_for("FUN_admin")))
    else:
        return abort(401)

@app.route("/add_user", methods = ["POST"])
def FUN_add_user():
    if session.get("current_user", None) == "ADMIN": # только админ может добавлять юзеров
        if request.form.get('id').upper() in list_users():
            user_list = list_users()
            user_table = zip(range(1, len(user_list)+1),\
                            user_list,\
                            [x + y for x,y in zip(["/delete_user/"] * len(user_list), user_list)])
            return(render_template("admin.html", id_to_add_is_duplicated = True, users = user_table))
        if " " in request.form.get('id') or "'" in request.form.get('id'):
            user_list = list_users()
            user_table = zip(range(1, len(user_list)+1),\
                            user_list,\
                            [x + y for x,y in zip(["/delete_user/"] * len(user_list), user_list)])
            return(render_template("admin.html", id_to_add_is_invalid = True, users = user_table))
        else:
            add_user(request.form.get('id'), request.form.get('pw'))
            return(redirect(url_for("FUN_admin")))
    else:
        return abort(401)





if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
