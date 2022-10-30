# importing flask module fro
import datetime

from flask import (Flask, render_template, request, redirect, session, flash)
from flaskext.mysql import MySQL
from datetime import date

mysql = MySQL()

# initializing a variable of Flask
app = Flask(__name__)

app.secret_key = 'wwwww'     #you can set any secret key but remember it should be secret

 # MySQL configurations
 # USing SQL WORKBENCH
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'ssss'
app.config['MYSQL_DATABASE_DB'] = 'tmdb'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'


mysql.init_app(app)

# Accessing the landing page and updating datebase and Current date
@app.route('/', methods=["GET"])
def home():
    return render_template('index.html')

#Add new timesheet
@app.route('/addtm', methods=["GET"])
def addtm():
    print(mondays())
    return render_template('layouts/Addtimesheet.html', arr=mondays())

def loginpages(page,msg,title):
    return render_template('/'+ page + '.html', msg=msg, title=title)

@app.route('/adminlogin')
def logingppage():
    return loginpages("adminlogin", "", "Admin Sign in")

@app.route('/loginstaffpage')
def loginstaffpage():
    return loginpages("loginstaffpage", "", "Staff Sign in")

def clearSession():
    for key in list(session.keys()):
        session.pop(key)

#View Staff profile
@app.route('/loginstaff', methods=['POST', 'GET'])
def loginstaff():
    clearSession() #Clear previous sessions
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pass']

        con = mysql.connect()
        cur = con.cursor()
        cur.execute('SELECT count(*) FROM staffsdetails WHERE username=%s AND password=%s AND status="ACTIVE"',
                    (username,password)) #count all with same username and Actice status
        count = cur.fetchall()

        con.commit()

        if count[-1][-1] > 0:

            cur.execute('select staffId,gpId,email from staffsdetails WHERE username=%s AND status="ACTIVE"',
                    (username)) #Select staffId,gpId,email with same username and Actice status

            gp = cur.fetchall()
            con.commit()

            session['email'] = gp[-1][2]
            session['staffId'] = gp[-1][0]
            session['gpId'] = gp[-1][1]
            session['staffuser'] = username
            session['logged'] = "staff"

            msg = "<h1>You are signed In as Staff</h1>"
            return profilestaff() #Call Function to open staff profile
        else:
            msg = "Incorrect password or username. Try Again!"
            flash(msg, "error")
            return loginpages("loginstaffpage", "","Care-giver Sign in") # Wrong password entered
        con.close()

# # Open Staff profile
@app.route('/profilest')
def profilestaff():
    if 'staffuser' in session: # here we are checking whether the user is logged in or not
        return render_template("profilestaff.html", gpd= gpds(), getassignments= getassignments(),
                           countassignments=countassignments())

    return render_template("page-404.html")  # if the user is not in the session

# -------------------------------------------------------------------------------------------------

def gpds():
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM staffsdetails WHERE username=%s', (session['staffuser']))
    count = cur.fetchall()

    con.commit()
    if count[-1][-1] > 0:
        #print("Successful!")
        cur.execute(
            'select staffid,gpId,fname,lname,phone,dob,email, gender,address, city, postcode,idtype,idnumber,dateadded, status from staffsdetails WHERE username=%s',
            (session['staffuser']))
        #
        gpd = cur.fetchall()
        con.commit()

        return gpd
    con.close()
# -------------------------------------------------------------------------------------------------

#login Admin
@app.route('/adminlogin', methods=['POST', 'GET'])
def adminlogin():
    clearSession()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pass']
        con = mysql.connect()
        cur = con.cursor()
        cur.execute('SELECT count(*) FROM adminlogin WHERE uname=%s AND pass=%s',
                    (username, password))
        count = cur.fetchall()

        con.commit()
        #print(count[-1][-1])

        if count[-1][-1] > 0:
            session['gpname'] = username
            session['user'] = username
            return dashboard()
        else:
            msg = "Incorrect password or username. Try Again!"
            flash(msg, "error")
            return loginpages("adminlogin", "","Admin Sign in")
        con.close()


@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template("home/dashboard.html", user=session['user'],
                               gpname=session['gpname'], countpatients=allcountassignments(),
                               countstaffs=countstaffs(), countcovid=0)
        # here we are checking whether the user is logged in or not
    return render_template("page-404.html")  # if the user is not in the session

@app.route('/staffview')
def staffview():
    if 'user' in session:
        return render_template("home/staffview.html", user=session['user'],
                               gpname=session['gpname'], getstaffs=getstaffs(), countstaffs=countstaffs())
        # here we are checking whether the user is logged in or not
    return render_template("page-404.html")  # if the user is not in the session

@app.route('/registerstaff')
def registerstaff():
    if 'user' in session:
        if 'gpname' in session:
            return render_template('home/registerstaff.html', user=session['user'], gpname=session['gpname'])
        # here we are checking whether the user is logged in or not
    return render_template("page-404.html")  # if the user is not in the session

#Add Staff
@app.route('/addstaff', methods=['POST', 'GET'])
def addstaff():
    date_time = ""
    if request.method == 'POST':
        con = mysql.connect()

        cur = con.cursor()
        cur.execute('select count(*) from staffsdetails')

        count = cur.fetchall()
        con.commit()
        if count[-1][-1] == 0:
            idkey = 0
        else:
            cur.execute('select id from staffsdetails')

            key = cur.fetchall()
            con.commit()
            idkey = key[-1][-1]

        #print(idkey)
        staffId = "staff-" + str(int(idkey)+1)
        fname = request.form['fname']
        lname = request.form['lname']
        address = request.form['address']
        city = request.form['city']
        postcode = request.form['postcode']
        phone = request.form['phone']
        username = request.form['username']
        email = request.form['email']
        password = request.form['pass']
        gender = request.form['gender']
        idtype = request.form['idtype']
        idnumber = request.form['idnumber']
        gpid = "staff"
        dob = request.form['dob']
        dateadded = date.today().strftime("%d/%m/%Y")
        status = "ACTIVE"

        cur.execute('INSERT INTO staffsdetails (staffId, fname, lname, address, city, postcode, phone, username, email, password, gender, idtype, idnumber, gpid, dob, dateadded, status)VALUES( %s, %s,  %s, %s, %s,  %s, %s , %s, %s,  %s, %s , %s,  %s, %s, %s,  %s, %s)',
                    (staffId, fname, lname, address, city, postcode, phone, username, email, password, gender, idtype, idnumber, gpid, dob, dateadded, status))

        con.commit()
        msg = "Staff has been Sucessfully Added!"
        flash(msg, "success")
        return redirect("/staffview")
        con.close()



# # -------------------------------------------------------------------------------------------------
#
def getstaffs():
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM staffsdetails')
    count = cur.fetchall()

    con.commit()
    #print(count[-1][-1])

    if count[-1][-1] > 0:
        #print("Successful!")
        cur.execute(
            'select staffid, fname,lname,email, gender, dateadded, status from staffsdetails')
        #
        getstaffs = cur.fetchall()
        con.commit()

        #print(session['gpId'])
        #print(getstaffs)
        return getstaffs
    else:
        getstaffs = " "
        return getstaffs
    con.close()

def countstaffs():
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM staffsdetails')
    countstaffs = cur.fetchall()

    con.commit()
    #print(countstaffs[-1][-1])
    return countstaffs[-1][-1]
    con.close()


#Open Staff Profile page on dashboard
#-----------------------------------------------------------------------------------------------------------------
@app.route('/calc', methods=['POST', 'GET'])
def calc():
    if request.method == 'POST':
        start = [request.form['start0'],request.form['start1'],request.form['start2'],request.form['start3'],request.form['start4'],request.form['start5'], request.form['start6']]
        end = [request.form['end0'],request.form['end1'],request.form['end2'],request.form['end3'],request.form['end4'],request.form['end5'],request.form['end6']]
        breakd = [request.form['break0'],request.form['break1'],request.form['break2'],request.form['break3'],request.form['break4'],request.form['break5'],request.form['break6']]


        con = mysql.connect()
        cur = con.cursor()
        cur.execute('select count(*) from wts')

        count = cur.fetchall()
        con.commit()
        if count[-1][-1] == 0:
            idkey = 0
        else:
            cur.execute('select id from wts')

            key = cur.fetchall()
            con.commit()
            idkey = key[-1][-1]

        grandtotal = 0
        for i in range(7):
            hours = int(end[i]) - int(start[i]) - int(breakd[i])
            grandtotal += hours
            print(str(hours))
        print("gt: " + str(grandtotal))

        staffId = session['staffId']
        datefrom = str(request.form['week'])
        tmid = staffId + datefrom
        grandtotal = grandtotal
        dateadded = str(date.today().strftime("%d/%m/%Y"))
        status = "SUBMITTED"
        cur.execute(
            'INSERT INTO wts(tmid,staffId,datefrom,hours,status,dateadded)VALUES( %s, %s,  %s, %s, %s,  %s)',
            (tmid,staffId,datefrom, grandtotal, status, dateadded))

        con.commit()

        for i in range(7):
            cur.execute(
                'INSERT INTO ets(tmid,start,end,break)VALUES( %s, %s,  %s, %s)',
                (tmid, start[i], end[i], breakd[i]))
            con.commit()
        msg = "Timesheet has been Sucessfully Added!"
        flash(msg, "success")

        return profilestaff()
        con.close()

# get timesheets
def getassignments():
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM wts WHERE staffid=%s',
                (session['staffId']))
    count = cur.fetchall()

    con.commit()
    #print(count[-1][-1])

    if count[-1][-1] > 0:
        #print("Successful!")
        cur.execute(
            'select id, tmid, datefrom, hours, dateadded, status from wts WHERE staffid=%s',
            (session['staffId']))
        #
        getpatients = cur.fetchall()
        con.commit()

    else:
        getpatients = " "
    return getpatients
    con.close()


#count timesheets
def countassignments():
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM wts WHERE staffid=%s',
                (session['staffId']))
    countpatients = cur.fetchall()

    con.commit()
    #print(countpatients[-1][-1])
    return countpatients[-1][-1]
    con.close()


#count timesheets
def allcountassignments():
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM wts')
    countpatients = cur.fetchall()

    con.commit()
    #print(countpatients[-1][-1])
    return countpatients[-1][-1]
    con.close()


#creating route for logging out
@app.route('/logout')
def logout():
    clearSession()
    # here we are checking whether the user is logged in or not
    return redirect('/')  # if the user is not in the session


def mondays():
    # getting today's date
    todayDate = datetime.date.today()
    print('Today Date:', todayDate)

    # Increment today's date with 1 week to get the next Monday
    lastMonday1 = todayDate + datetime.timedelta(days=-todayDate.weekday(), weeks=-2)
    lastMonday2 = todayDate + datetime.timedelta(days=-todayDate.weekday(), weeks=-1)
    lastMonday3 = todayDate + datetime.timedelta(days=-todayDate.weekday(), weeks=0)
    print('Next Monday Date:', lastMonday1)
    print('Next Monday Date:', lastMonday2)
    print('Next Monday Date:', lastMonday3)
    arr = [lastMonday1, lastMonday2, lastMonday3]
    return arr


@app.route('/patientview')
def patientview():
    if 'user' in session:
        return render_template("home/patientview.html", getpatients=getpatients(), countpatients=countpatients() )
        # here we are checking whether the user is logged in or not
    return render_template("page-404.html")  # if the user is not in the session

def getpatients():
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM wts')
    count = cur.fetchall()

    con.commit()

    if count[-1][-1] > 0:
        cur.execute(
            'select id, staffid, tmid, datefrom, hours, dateadded,status from wts',)
        #
        getpatients = cur.fetchall()
        con.commit()

        return getpatients
    else:
        getpatients = " "
        return getpatients
    con.close()

def countpatients():
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM wts')
    countpatients = cur.fetchall()

    con.commit()
    return countpatients[-1][-1]
    con.close()


#Action - Update Timesheet
@app.route('/action', methods=['POST', 'GET'])
def action():
    if request.method == 'POST':
        newstatus = request.form['newstatus']
        medpatientId = request.form['medpatientId']

        con = mysql.connect()
        cur = con.cursor()
        cur.execute('UPDATE wts SET status=%s WHERE tmid=%s',
                    (newstatus, medpatientId))
        con.commit()
        con.close()
        return redirect("/patientview")

if __name__ == "__main__":
    app.run()
