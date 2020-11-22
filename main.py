
from flask import Flask,render_template,request,session,redirect,url_for
import pyodbc
import re
from random import seed
from random import randint

app=Flask(__name__)
app.secret_key="sss"



@app.route("/" )
def home():
    if 'user' in session:
         dbfirstname = session['user']
         return render_template("home2.html",dbfirstname=dbfirstname)
    else:
        return render_template("home.html")

@app.route("/data" )
def data():
    if 'user' in session:
        dbfirstname = session['user']
        if session['roleno']==2:
           return render_template("admin.html",dbfirstname=dbfirstname)
        elif session['roleno']==3:
           return render_template("reader.html",dbfirstname=dbfirstname)
    else:
        return render_template("login.html")

@app.route("/logout" )
def logout():
      session.pop('user',None)
      return redirect(url_for('login'))


@app.route("/aboutus" )
def aboutus():
    if 'user' in session:
        dbfirstname = session['user']
        return render_template("aboutus2.html",dbfirstname=dbfirstname)
    else:
        return render_template("aboutus.html")



@app.route("/login", methods=['GET','POST'] )
def login():
    if request.method == 'POST':
        regno = request.form['regno']
        password = request.form['password']

        if regno == '' or password == '' or len(password) < 8 or len(regno) != 5:
            x = 'something wrong with entered values'
            return render_template('login.html', x=x)

        else:
            conn = pyodbc.connect(
                "Driver={SQL Server Native Client 11.0};"
                "Server=DESKTOP-015KT2K;"
                "Database=library;"
                "Trusted_Connection=yes;")
            cursor = conn.cursor()
            cursor.execute(

                "SELECT * FROM [user] WHERE regno=?", regno
            )

            for row in cursor:
                dbpassword = row[2]
                dbfirstname = row[3]
                dbroleno = row[5]
                dbregno=row[1]

                if dbpassword == password:
                    session['user'] = dbfirstname
                    session['roleno']=dbroleno
                    session['regno'] = dbregno
                    return redirect(url_for('home'))

                elif dbpassword != password and dbpassword != None:
                    x = 'Username and password are not matching'
                    return render_template("login.html", x=x)
            else:
                x = 'Try again'
                return render_template("login.html", x=x)
    else:

         return render_template("login.html")


@app.route("/register",methods=['POST','GET'])
def register():
   if request.method=='POST':
    regno = request.form['regno']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    password = request.form['password']
    repassword = request.form['repassword']

    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    validemail = re.search(regex, email)

    if regno == '' or firstname == '' or lastname == '' or email == '' or password == '' or repassword == '':
        return "fill all the blanks"
    elif (validemail == None):
        return "enter a valid email"
    elif password != repassword:
        return "passwords should match"
    elif len(regno) != 5:
        return "regno should be exactly 5 charactors"

    elif len(password) < 8:
        return "password should have 8 or more charactors"

    else:
        conn = pyodbc.connect(
            "Driver={SQL Server Native Client 11.0};"
            "Server=DESKTOP-015KT2K;"
            "Database=library;"
            "Trusted_Connection=yes;")
        cursor = conn.cursor()
        cursor.execute(

            "SELECT * FROM [user] WHERE regno=?", (regno)
        )

        for row in cursor:
            dbregno = row[1]
            if dbregno == regno:
                return "regno already exists"
                conn.commit()

        conn = pyodbc.connect(
            "Driver={SQL Server Native Client 11.0};"
            "Server=DESKTOP-015KT2K;"
            "Database=library;"
            "Trusted_Connection=yes;")
        cursor = conn.cursor()

        cursor.execute(

            "INSERT INTO [user](regno,password,firstname,lastname,roleno,email) VALUES(?,?,?,?,?,?);",
            (regno, password, firstname, lastname, 2, email)
        )
        conn.commit()
        x = "You have successfuly registered!.Now you can login"
        return render_template("login.html", x=x)

   return render_template("register.html")


@app.route("/books" )
def books():
    if 'user' in session:
      dbfirstname = session['user']
      conn = pyodbc.connect(
          "Driver={SQL Server Native Client 11.0};"
          "Server=DESKTOP-015KT2K;"
          "Database=library;"
          "Trusted_Connection=yes;")
      cursor = conn.cursor()
      cursor.execute(

          "SELECT * FROM [book] ORDER BY booknumber"
      )
      if session['roleno']==2:
        return render_template('books.html', cursor=cursor,dbfirstname=dbfirstname)

      elif session['roleno']==3:
        return render_template('booksforreader.html', cursor=cursor, dbfirstname=dbfirstname)

    else:
        return redirect(url_for("login"))

@app.route("/createbook",methods=['POST','GET'] )
def createbook():

    if 'user' in session and session['roleno']==2:
        dbfirstname = session['user']
        if request.method == 'POST':
            bookno = request.form['bookno']
            bookname = request.form['bookname']
            author = request.form['author']
            noofcopies = request.form['noofcopies']
            availablecopies = request.form['availablecopies']


            conn = pyodbc.connect(
                "Driver={SQL Server Native Client 11.0};"
                "Server=DESKTOP-015KT2K;"
                "Database=library;"
                "Trusted_Connection=yes;")
            cursor = conn.cursor()
            cursor.execute(

                  "INSERT INTO [book](booknumber,bookname,author,noofcopies,availablecopies) VALUES(?,?,?,?,?);",(bookno,bookname,author,noofcopies,availablecopies)
            )
            conn.commit()
            return redirect(url_for('books'))
        else:

            return render_template('createbook.html',dbfirstname=dbfirstname)
    else:
      return redirect(url_for('login'))

@app.route("/deletebook/<string:id>" )
def deletebook(id):
    if 'user' in session:

      conn = pyodbc.connect(
        "Driver={SQL Server Native Client 11.0};"
        "Server=DESKTOP-015KT2K;"
        "Database=library;"
        "Trusted_Connection=yes;")
      cursor1 = conn.cursor()
      cursor1.execute(

        "DELETE FROM [book] WHERE id=?",(id)
      )
      conn.commit()
      return redirect(url_for('books'))
    else:
      return redirect(url_for('login'))

@app.route("/updatebook/<string:id>",methods=['POST','GET'] )
def updatebook(id):

    if 'user' in session and session['roleno']==2:
        dbfirstname = session['user']
        if request.method == 'POST':
            bookno = request.form['bookno']
            bookname = request.form['bookname']
            author = request.form['author']
            noofcopies = request.form['noofcopies']
            availablecopies = request.form['availablecopies']


            conn = pyodbc.connect(
                "Driver={SQL Server Native Client 11.0};"
                "Server=DESKTOP-015KT2K;"
                "Database=library;"
                "Trusted_Connection=yes;")
            cursor = conn.cursor()
            cursor.execute(

                 "UPDATE book SET booknumber=?,bookname=?,author=?,noofcopies=?,availablecopies=? WHERE id=?;",(bookno,bookname,author,noofcopies,availablecopies,id)
            )
            conn.commit()
            return redirect(url_for('books'))
        else:
            conn = pyodbc.connect(
                "Driver={SQL Server Native Client 11.0};"
                "Server=DESKTOP-015KT2K;"
                "Database=library;"
                "Trusted_Connection=yes;")
            cursor1 = conn.cursor()
            cursor1.execute(

                "SELECT* FROM [book] WHERE id=?", (id)
            )
            for row in cursor1:
                id = row[0]
                booknumber = row[1]
                bookname = row[2]
                author =row[3]
                noofcopies =row [4]
                availablecopies =row [5]
            return render_template('updatebook.html', id=id, booknumber=booknumber, bookname
                                   =bookname, author=author,
                                   noofcopies=noofcopies,availablecopies=availablecopies,dbfirstname=dbfirstname)

    return redirect(url_for('login'))


@app.route("/users" )
def users():
    if 'user' in session and session['roleno'] == 2:
        dbfirstname = session['user']
        conn = pyodbc.connect(
            "Driver={SQL Server Native Client 11.0};"
            "Server=DESKTOP-015KT2K;"
            "Database=library;"
            "Trusted_Connection=yes;")
        cursor = conn.cursor()
        cursor.execute(

            "SELECT * FROM [user] ORDER BY regno"
        )
        return render_template('users.html', cursor=cursor, dbfirstname=dbfirstname)

    else:
        return redirect(url_for("login"))

@app.route("/deleteuser/<string:id>")
def deleteuser(id):
    if 'user' in session and session['roleno'] == 2:
        conn = pyodbc.connect(
            "Driver={SQL Server Native Client 11.0};"
            "Server=DESKTOP-015KT2K;"
            "Database=library;"
            "Trusted_Connection=yes;")
        cursor1 = conn.cursor()
        cursor1.execute(

            "DELETE FROM [user] WHERE id=?", (id)
        )
        conn.commit()
        return redirect(url_for('users'))
    else:
        return redirect(url_for('login'))

@app.route("/updateuser/<string:id>",methods=['GET','POST'])
def updateuser(id):
    if 'user' in session and session['roleno'] == 2:
        dbfirstname = session['user']
        if request.method == 'POST':
            regno = request.form['regno']
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            email = request.form['email']

            conn = pyodbc.connect(
                "Driver={SQL Server Native Client 11.0};"
                "Server=DESKTOP-015KT2K;"
                "Database=library;"
                "Trusted_Connection=yes;")
            cursor = conn.cursor()
            cursor.execute(

                 "UPDATE [user] SET regno=?,firstname=?,lastname=?,email=? WHERE id=?;",(regno,firstname,lastname,email,id)
            )
            conn.commit()
            return redirect(url_for('users'))
        else:
            conn = pyodbc.connect(
                "Driver={SQL Server Native Client 11.0};"
                "Server=DESKTOP-015KT2K;"
                "Database=library;"
                "Trusted_Connection=yes;")
            cursor = conn.cursor()
            cursor.execute(

                "SELECT* FROM [user] WHERE id=?", (id)
            )
            for row in cursor:
                id = row[0]
                regno = row[1]
                firstname = row[3]
                lastname = row[4]
                email = row[6]
            return render_template('updateuser.html', id=id, regno=regno, firstname=firstname, lastname=lastname,
                                   email=email, dbfirstname=dbfirstname)
    else:
         return redirect(url_for('login'))


@app.route("/rentals",methods=['POST','GET'] )
def rentals():

  if 'user' in session and session['roleno'] == 2:
    dbfirstname = session['user']

    conn = pyodbc.connect(
        "Driver={SQL Server Native Client 11.0};"
        "Server=DESKTOP-015KT2K;"
        "Database=library;"
        "Trusted_Connection=yes;")
    cursor = conn.cursor()
    cursor.execute(

        "SELECT * FROM [rental] WHERE status=? ORDER BY regno;",(1)
    )
    return render_template('rentals.html',cursor=cursor,dbfirstname=dbfirstname)

  elif 'user' in session and session['roleno'] == 3:
    dbfirstname = session['user']
    dbregno=session['regno']
    conn = pyodbc.connect(
        "Driver={SQL Server Native Client 11.0};"
        "Server=DESKTOP-015KT2K;"
        "Database=library;"
        "Trusted_Connection=yes;")
    cursor = conn.cursor()
    cursor.execute(

        "SELECT rental.regno, rental.booknumber,book.bookname,book.author, rental.rentdate, rental.duedate  FROM (rental INNER JOIN book ON rental.booknumber=book.booknumber) WHERE rental.regno=? ORDER BY rental.rentdate DESC;",(dbregno)
    )

    return render_template('rentalsforreader.html', cursor=cursor, dbfirstname=dbfirstname)


  else:
      return redirect(url_for("login"))


@app.route("/rentals/booknumber", methods=['POST', 'GET'])
def booknumber():
    if 'user' in session and session['roleno'] == 2:
        dbfirstname = session['user']
        conn = pyodbc.connect(
            "Driver={SQL Server Native Client 11.0};"
            "Server=DESKTOP-015KT2K;"
            "Database=library;"
            "Trusted_Connection=yes;")
        cursor = conn.cursor()
        cursor.execute(

            "SELECT * FROM [rental] WHERE status=? ORDER BY booknumber;",(1)
        )
        return render_template('rentals.html', cursor=cursor, dbfirstname=dbfirstname)



    else:
        return redirect(url_for("login"))

@app.route("/rentals/rentdate", methods=['POST', 'GET'])
def rentdate():
    if 'user' in session and session['roleno'] == 2:
        dbfirstname = session['user']
        conn = pyodbc.connect(
            "Driver={SQL Server Native Client 11.0};"
            "Server=DESKTOP-015KT2K;"
            "Database=library;"
            "Trusted_Connection=yes;")
        cursor = conn.cursor()
        cursor.execute(

            "SELECT * FROM [rental] WHERE status=? ORDER BY rentdate DESC;",(1)
        )
        return render_template('rentals.html', cursor=cursor, dbfirstname=dbfirstname)

    else:
        return redirect(url_for("login"))

@app.route("/rentals/duedate", methods=['POST', 'GET'])
def duedate():
    if 'user' in session and session['roleno'] == 2:
        dbfirstname = session['user']
        conn = pyodbc.connect(
            "Driver={SQL Server Native Client 11.0};"
            "Server=DESKTOP-015KT2K;"
            "Database=library;"
            "Trusted_Connection=yes;")
        cursor = conn.cursor()
        cursor.execute(

            "SELECT * FROM [rental] WHERE status=? ORDER BY duedate DESC;",(1)
        )
        return render_template('rentals.html', cursor=cursor, dbfirstname=dbfirstname)

    else:
        return redirect(url_for("login"))



@app.route("/deleterental/<string:id>",methods=['POST','GET'] )
def deleterental(id):
    if 'user' in session and session['roleno'] == 2:
        dbfirstname = session['user']
        conn = pyodbc.connect(
          "Driver={SQL Server Native Client 11.0};"
          "Server=DESKTOP-015KT2K;"
          "Database=library;"
          "Trusted_Connection=yes;")
        cursor = conn.cursor()

        cursor.execute(


           "UPDATE [rental]  SET status=? WHERE id=?;", (0,id)
        )
        conn.commit()
        return redirect(url_for('rentals'))
    else:
        return redirect(url_for('login'))

@app.route("/updaterental/<string:id>" , methods=['GET','POST'])
def updaterental(id):
    if 'user' in session and session['roleno'] == 2:
        dbfirstname = session['user']
        if request.method == 'POST':
            regno = request.form['regno']
            booknumber = request.form['booknumber']
            rentdate = request.form['rentdate']
            duedate = request.form['duedate']

            conn = pyodbc.connect(
                "Driver={SQL Server Native Client 11.0};"
                "Server=DESKTOP-015KT2K;"
                "Database=library;"
                "Trusted_Connection=yes;")
            cursor = conn.cursor()
            cursor.execute(

                 "UPDATE [rental] SET regno=?,booknumber=?,rentdate=?,duedate=?,status=? WHERE id=?;",(regno,booknumber,rentdate,duedate,1,id)
            )
            conn.commit()
            return redirect(url_for('rentals'))
        else:
            conn = pyodbc.connect(
                "Driver={SQL Server Native Client 11.0};"
                "Server=DESKTOP-015KT2K;"
                "Database=library;"
                "Trusted_Connection=yes;")
            cursor = conn.cursor()
            cursor.execute(

                "SELECT* FROM [rental] WHERE id=?", (id)
            )
            for row in cursor:
                id = row[0]
                regno = row[1]
                booknumber = row[2]
                rentdate = row[3]
                duedate = row[4]
            return render_template('updaterental.html', id=id, regno=regno, booknumber=booknumber, rentdate=rentdate,
                                   duedate=duedate, dbfirstname=dbfirstname)
    else:
         return redirect(url_for('login'))

@app.route("/createrental",methods=['POST','GET'] )
def createrental():

    if 'user' in session and session['roleno']==2:
        dbfirstname = session['user']
        if request.method == 'POST':
            regno = request.form['regno']
            booknumber = request.form['booknumber']
            rentdate = request.form['rentdate']
            duedate = request.form['duedate']

            conn = pyodbc.connect(
                "Driver={SQL Server Native Client 11.0};"
                "Server=DESKTOP-015KT2K;"
                "Database=library;"
                "Trusted_Connection=yes;")
            cursor = conn.cursor()
            cursor.execute(

                 "INSERT INTO [rental](regno,booknumber,rentdate,duedate,status) VALUES(?,?,?,?,?);",(regno,booknumber,rentdate,duedate,1)
            )
            conn.commit()
            conn = pyodbc.connect(
                "Driver={SQL Server Native Client 11.0};"
                "Server=DESKTOP-015KT2K;"
                "Database=library;"
                "Trusted_Connection=yes;")
            cursor = conn.cursor()
            cursor.execute(

                "SELECT * FROM[book] WHERE booknumber=?;",(booknumber)

            )
            for row in cursor:
                id=row[0]
                availablebooks=row[5]
                newavailablebooks=availablebooks-1
            conn.commit()
            conn = pyodbc.connect(
                "Driver={SQL Server Native Client 11.0};"
                "Server=DESKTOP-015KT2K;"
                "Database=library;"
                "Trusted_Connection=yes;")
            cursor = conn.cursor()
            cursor.execute(

                    "UPDATE [book] SET availablecopies=? WHERE id=?;",(newavailablebooks,id)

            )
            conn.commit()

            return redirect(url_for('rentals'))
        else:
            conn = pyodbc.connect(
                "Driver={SQL Server Native Client 11.0};"
                "Server=DESKTOP-015KT2K;"
                "Database=library;"
                "Trusted_Connection=yes;")
            cursor = conn.cursor()
            cursor.execute(

                "SELECT* FROM [user]"
            )

            conn = pyodbc.connect(
                "Driver={SQL Server Native Client 11.0};"
                "Server=DESKTOP-015KT2K;"
                "Database=library;"
                "Trusted_Connection=yes;")

            cursor2 = conn.cursor()
            cursor2.execute(

                "SELECT* FROM [book]"
            )

            return render_template('createrental.html',dbfirstname=dbfirstname,cursor=cursor,cursor2=cursor2)
    else:
      return redirect(url_for('login'))

@app.route("/analysis",methods=['POST','GET'] )
def analysis():

    if 'user' in session and session['roleno']==2:
        dbfirstname = session['user']
        conn = pyodbc.connect(
            "Driver={SQL Server Native Client 11.0};"
            "Server=DESKTOP-015KT2K;"
            "Database=library;"
            "Trusted_Connection=yes;")
        cursor = conn.cursor()
        cursor.execute(

            "SELECT COUNT(id),booknumber FROM[rental] GROUP BY booknumber ORDER BY COUNT(id) DESC"
        )
        bookarray = []
        countarray = []


        for row in cursor :
         booklist = [row[1]]
         countlist = [str(row[0])]
         bookarray = bookarray + booklist
         countarray = countarray + countlist



        return render_template('analysisforadmin.html',bookarray=bookarray,countarray=countarray,dbfirstname=dbfirstname)
    else:
        return redirect(url_for('login'))



if __name__ == "__main__":
    app.run()
