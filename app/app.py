from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

@app.route('/')
def index():
    return 'hello world!'

@app.route('/db')
def db():
  conn = mysql.connector.connect(
      host="mysql",
      user="user",
      password="password",
      database="db"
  )

  cur = conn.cursor(dictionary=True)
  cur.execute("SELECT * FROM test")
  rows = cur.fetchall()

  buf = ""
  for row in rows:
    list = []
    for k in row:
      list.append(":".join([k, str(row[k])]))
    buf += ", ".join(list) + "<br/>\n"

  cur.close()
  conn.close()

  return buf


if __name__ == '__main__':
    app.run()

