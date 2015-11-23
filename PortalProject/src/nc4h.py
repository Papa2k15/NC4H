from flask.app import Flask
from flask.templating import render_template
import urllib2
from flask.globals import request
from bs4 import BeautifulSoup
import sqlite3 as lite
import HTMLParser

DATABASE = 'nc4h.db'
nc4hers = ["Sarah Kotzian","Amy Chilcote","David Herpy Larry Hancock","Michael Yoder","Salim Oden","Shannon McCollum","Mitzi Downing"]

nc4h = Flask(__name__)
nc4h.secret_key = 'nc4h'

@nc4h.route('/')
def home():
    return render_template('home.html')

@nc4h.route('/add')
def add_submission():
    return render_template('index.html')

@nc4h.route('/getname/',methods=["GET"])
def getname():
    url = request.args.get('transferurl')
    usock = urllib2.urlopen(url)
    filer = usock.read();
    parsed_html = BeautifulSoup(filer,  "html5lib")
    my_out = str(parsed_html.find('title')).replace('<title>','').replace('</title>','').replace('|','').replace('NC 4-H Youth Development','')
    h = HTMLParser.HTMLParser()
    s = h.unescape(my_out)
    usock.close()
    if my_out is not None:
        return s
    else:
        return "Not 4-H Page"

@nc4h.route('/sendtogreg/', methods=["POST"])
def sendtogreg():
    pagename = None
    if 'pagename' in request.form:
        pagename = request.form['pagename']
    wtd = None
    if 'wtd' in request.form:
        wtd = request.form['wtd']
    nc4her = None
    if 'nc4her' in request.form:
        nc4her =  request.form['nc4her']
    textsource = None
    if 'textsource' in request.form:
        textsource = request.form['textsource']
    notes = None
    if 'notes' in request.form:
        notes = request.form['notes']
    medialinks = []
    for x in request.form:
        if 'medialink' in x:
            medialinks.append(request.form[str(x)])
    print medialinks
    otherlinks = []
    for x in request.form:
        if 'otherlink' in x:
            otherlinks.append(request.form[str(x)])
    print otherlinks
    store_info(wtd,nc4her,textsource,notes,medialinks,otherlinks,pagename)
    return render_template('confirm.html',message="Thats all you have to do, your information was successfully sent to Greg")

@nc4h.route('/gregview/<pageid>', methods=["GET"])
def myview(pageid=None):
    con = None
    try:
        con = lite.connect(DATABASE)
        with con:
            con.rollback()
            cur = con.cursor()
            cur.execute("SELECT * FROM page WHERE pageid = ?", (pageid,))
            con.commit()
            pageinfo = cur.fetchone()
            con.rollback()
            cur = con.cursor()
            cur.execute("SELECT * FROM medialinks WHERE pageid = ?", (pageid,))
            con.commit()
            medial = cur.fetchall()
            con.rollback()
            cur = con.cursor()
            cur.execute("SELECT * FROM otherlinks WHERE pageid = ?", (pageid,))
            con.commit()
            otherl = cur.fetchall()
            wtd = pageinfo[3]
            nc4her = pageinfo[1]
            textsource = pageinfo[4]
            notes = pageinfo[5]
            pagename = pageinfo[2]
            medialinks = []
            for m in medial:
                medialinks.append(m[1])
            otherlinks = []
            for o in otherl:
                otherlinks.append(o[1])
            return render_template('recevied.html',wtd=wtd,nc4her=nc4her,textsource=textsource,
                           notes=notes,medialinks=medialinks,otherlinks=otherlinks,
                           pagename=pagename)
    except lite.Error, e:
        return str(e)
    finally:
        if con:
            con.close()
            
def store_info(wtd,nc4her,textsource,notes,medialinks,otherlinks,pagename):
    con = None
    try:
        con = lite.connect(DATABASE)
        with con:
            con.rollback()
            cur = con.cursor()
            cur.execute("INSERT INTO page (nc4her,pagename,wtd,textsource,notes) VALUES (?,?,?,?,?)", 
                        (nc4her,pagename,wtd,textsource,notes))
            con.commit()
            pageid = cur.lastrowid
            if len(medialinks) > 0:
                for x in medialinks:  
                    cur.execute("INSERT INTO medialinks (link,pageid) VALUES (?,?)", (x,pageid))
                con.commit()
            if len(otherlinks) > 0:
                for x in otherlinks:  
                    cur.execute("INSERT INTO otherlinks (link,pageid) VALUES (?,?)", (x,pageid))
                con.commit() 
    except lite.Error, e:
        return str(e)
    finally:
        if con:
            con.close()

@nc4h.route('/search')
def searchnc4hers():
    return render_template('search.html')
    
@nc4h.route('/my_submissions')
def mysubmissions():
    return render_template("mysubmissions.html");
    
@nc4h.route('/finddata', methods=["GET"])
def finddataforuser():
    nc4her = request.args.get('nc4her').replace("%20"," ")
    returnhtml = ""
    con = None
    try:
        con = lite.connect(DATABASE)
        with con:
            con.rollback()
            cur = con.cursor()
            cur.execute("SELECT * FROM page WHERE nc4her = ?", (nc4her,))
            con.commit()
            data = cur.fetchall()
            for x in data:
                returnhtml += """
                    <li class="list-group-item"><span><a href='/gregview/"""+str(x[0])+"""'>"""+str(x[0])+ " " + str(x[3]) + """</a></span></li>
                """
            return returnhtml
    except lite.Error, e:
        return str(e)
    finally:
        if con:
            con.close()

@nc4h.route('/finddatat', methods=["GET"])
def findmydata():
    nc4her = request.args.get('nc4her').replace("%20"," ")
    returnhtml = ""
    con = None
    try:
        con = lite.connect(DATABASE)
        with con:
            con.rollback()
            cur = con.cursor()
            cur.execute("SELECT * FROM page WHERE nc4her = ?", (nc4her,))
            con.commit()
            data = cur.fetchall()
            for x in data:
                returnhtml += """
                    <li class="list-group-item"><span><a href='/theirview/"""+str(x[0])+"""'>"""+str(x[0])+ " " + str(x[3]) + """</a></span></li>
                """
            return returnhtml
    except lite.Error, e:
        return str(e)
    finally:
        if con:
            con.close()

@nc4h.route('/remove_all', methods=['GET'])
def removeall():
    nc4her = request.args.get('nc4her').replace("%20"," ")
    con = None
    try:
        con = lite.connect(DATABASE)
        with con:
            con.rollback()
            cur = con.cursor()
            cur.execute("SELECT * FROM page WHERE nc4her = ?", (nc4her,))
            con.commit();
            pageids = []
            for x in cur.fetchall():
                pageids.append(x[0])
            
            cur.execute("DELETE FROM page WHERE nc4her = ?", (nc4her,))
            for ids in pageids:
                cur.execute("DELETE FROM medialinks WHERE pageid = ?", (ids,))
                cur.execute("DELETE FROM otherlinks WHERE pageid = ?", (ids,))
            con.commit()
            return "Removed All"
    except lite.Error, e:
        return str(e)
    finally:
        if con:
            con.close()


@nc4h.route('/theirview/<pageid>', methods=["GET"])
def theirview(pageid=None):
    con = None
    try:
        con = lite.connect(DATABASE)
        with con:
            con.rollback()
            cur = con.cursor()
            cur.execute("SELECT * FROM page WHERE pageid = ?", (pageid,))
            con.commit()
            pageinfo = cur.fetchone()
            con.rollback()
            cur = con.cursor()
            cur.execute("SELECT * FROM medialinks WHERE pageid = ?", (pageid,))
            con.commit()
            medial = cur.fetchall()
            con.rollback()
            cur = con.cursor()
            cur.execute("SELECT * FROM otherlinks WHERE pageid = ?", (pageid,))
            con.commit()
            otherl = cur.fetchall()
            wtd = pageinfo[3]
            nc4her = pageinfo[1]
            textsource = pageinfo[4]
            notes = pageinfo[5]
            pagename = pageinfo[2]
            medialinks = []
            for m in medial:
                medialinks.append(m[1])
            otherlinks = []
            for o in otherl:
                otherlinks.append(o[1])
            return render_template('managesubmissions.html',wtd=wtd,nc4her=nc4her,textsource=textsource,
                           notes=notes,medialinks=medialinks,otherlinks=otherlinks,
                           pagename=pagename)
    except lite.Error, e:
        return str(e)
    finally:
        if con:
            con.close()

if __name__ == '__main__':
    nc4h.run(host='0.0.0.0',port=2000,debug=True)