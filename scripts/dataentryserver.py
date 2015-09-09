import sqlite3
import json
import os.path
import os
from bottle import Bottle, template, request, redirect, response
import csv

app = Bottle()

class DataBase:
    def __init__(self, filename, schema):
        self.schema = schema
        self.db  = sqlite3.connect(filename)
        
        self.create()


    def close(self):
        self.db.close()


    def create(self):
        result, = self.db.execute(
            "SELECT COUNT() FROM sqlite_master WHERE type='table' AND name='data';").fetchone()

        if result == 0:
            query = "CREATE TABLE IF NOT EXISTS data ("
            for i in range(0, len(self.schema)):
                col = self.schema[i]
                if len(col) > 1:
                    query += col[0]
                    query += " "
                    if col[1] == "INTINDX":
                        query += "INTEGER PRIMARY KEY"
                    elif col[1] == "INT":
                        query += "INTEGER"
                    elif col[1] == "REAL":
                        query += "REAL"
                    elif col[1] == "DATE":
                        query += "DATE"
                    elif col[1] == "TIME":
                        query += "TIME"
                    else:
                        query += "TEXT"
                    if (i != len(self.schema)-1):
                        query += ", "
            query += ");"

            self.db.execute(query)
            self.db.commit()

        iqcols = ''
        iqvalues = ''
        uqvalues = ''
        sqcols = ''
        for i in range(0, len(self.schema)):
            col = self.schema[i]
            if len(col) > 1:
                sqcols += col[0]
                if (i != len(self.schema)-1):
                    sqcols += ", "
                if col[1] != 'INTINDX':
                    iqcols += col[0]
                    iqvalues += ':' + col[0]
                    uqvalues += "{0} = :{0} ".format(col[0])
                    if (i != len(self.schema)-1):
                        iqcols += ", "
                        iqvalues += ", "
                        uqvalues += ", "
                

        self.iquery = "INSERT INTO  data({0}) VALUES({1})".format(iqcols, iqvalues)
        self.uquery = "UPDATE data SET {0} WHERE {1}=:{1}".format(uqvalues, '{0}')
        self.squery = "SELECT {0} FROM data WHERE {1}=:{1}".format(sqcols, '{0}')

        result, = self.db.execute(
            "SELECT COUNT() FROM sqlite_master WHERE type='table' AND name='uniquecounter';").fetchone()

        if result == 0:
            query = "CREATE TABLE IF NOT EXISTS uniquecounter (id INTEGER PRIMARY KEY, counter INTEGER)"
            self.db.execute(query)
            query = "INSERT INTO  uniquecounter(counter) VALUES(1)"
            self.db.execute(query)
            self.db.commit()


    def add(self, data):
        datai = {}
        for col in self.schema:
            if len(col) >  1:
                if col[1] != 'INTINDX':
                    try:
                        datai[col[0]] = data[col[0]]
                    except KeyError:
                        datai[col[0]] = ''

        print(datai)

        try:
            result = self.db.execute(self.iquery, datai)
            
            self.db.commit()

            return result.lastrowid
        except sqlite3.DatabaseError:
            self.db.rollback()

            return False


    def update(self, data):
        datai = {}
        indexcol = ""
        for col in self.schema:
            if len(col) > 1:
                if col[1] == 'INTINDX':
                    indexcol = col[0]
                try:
                    datai[col[0]] = data[col[0]]
                except KeyError:
                    datai[col[0]] = ''

        if indexcol == "":
            return False

        query = self.uquery.format(indexcol)

        try:
            result = self.db.execute(query, datai)
            
            self.db.commit()

            return True
        except sqlite3.DatabaseError:
            self.db.rollback()

            return False


    def get(self, col, filter):
        query = self.squery.format(col)

        try:
            row = self.db.execute(query, { col : filter }).fetchone()
        except sqlite3.DatabaseError:
            return False

        if row == None:
            return False

        result = {}
        coli = 0
        for i in range(0, len(self.schema)):
            col = self.schema[i]
            if len(col) > 1:
                result[col[0]] = row[coli]
                coli += 1

        return result


    def list(self, cols, filter=""):
        query = "SELECT {0} FROM data".format(cols)
        if filter != "":
            query += " WHERE {0}".format(filter)
        
        try:
            rows = self.db.execute(query)
        except sqlite3.DatabaseError:
            return False

        return rows


    def getuniqueid(self):
        counter, = self.db.execute('SELECT counter FROM uniquecounter WHERE id = 1').fetchone()

        uniqueid = counter

        counter += 1

        try:
            result = self.db.execute("UPDATE uniquecounter SET counter={0} WHERE id=1".format(counter))
            
            self.db.commit()

            return uniqueid
        except sqlite3.DatabaseError:
            self.db.rollback()

            return False


class DataEntry(Bottle):
    def __init__(self, settingsfile):
        Bottle.__init__(self)
        self.settings = self.loadSettings(settingsfile)

        if self.settings == False:
            self.alert('Error', 'Error loading settings from "{0}"'.format(settingsfile))
            
        self.schema = self.settings['schema']

        self.db = DataBase(self.settings['dbfile'], self.schema)

        self.imageStore = self.settings['imagestore']

        self.status = ""


    def loadSettings(self, settingsfile):
        settingstr = ""
        try:
            with open(settingsfile) as f:
                settingstr = f.read()
            settings = json.loads(settingstr)
        except IOError:
            print 'Settings file not found at {0}'.format(settingsfile)
            return False

        if 'dbfile' in settings and 'imagestore' in settings and 'schema' in settings:
            if len(settings['schema']) > 0:
                return settings

        print 'Settings format wrong in {0}'.format(settingsfile)
        return False


    def alert(self, title, message):
        print("{0} : {1}".format(title, message))


    def setStatus(self, message):
        self.status = message


    def template(self, name, page=None):
        try:
            filename = "{0}{1}.html".format(self.settings['templates'],name)
            with open(filename) as f:
                templatestr = f.read()
            return template(templatestr, page=page, status=self.status)
            
        except IOError:
            return 'Template not found at {0}'.format(filename)


    def listPatients(self, filter):
        patientList = {}
        patientList['headers'] = ("#", "IP", "Name", "Age", "Sex")
        patientList['rows'] = self.db.list('patientid, ipnumber, name, age, sex', filter)

        return self.template('list', patientList)


    def viewPatientById(self, patientid):
        page = {}
        data = self.db.get('patientid', patientid)

        if data == False:
            return self.template("error", "Patient {0} not found".format(patientid))
        
        page['form'] = self.generateForm(data)
        page['action'] = "/patients/{0}/update".format(patientid)

        return '<form method="post" action="{0}">{1}<input type="submit" value="Save"></form>'.format(page['action'], page['form'])


    def viewPatientByIp(self, ipnumber):
        page = {}
        data = self.db.get('ipnumber', ipnumber)

        if data == False:
            return self.template("error", "Patient with IP Number {0} not found".format(ipnumber))

        patientid = data['patientid']

        page['form'] = self.generateForm(data)
        page['action'] = "/patients/{0}/update".format(patientid)

        return '<form method="post" action="{0}">{1}<input type="submit" value="Save"></form>'.format(page['action'], page['form'])


    def newPatientForm(self):
        page = {}
        
        page['form'] = self.generateForm()
        page['action'] = "/patients/new"

        return '<form method="post" action="{0}" >{1}<input type="submit" value="Save"></form>'.format(page['action'], page['form'])


    def addPatient(self, data):
        patientid = self.db.add(data)

        return patientid


    def processForm(self, form):
        data = {}

        for col in self.schema:
            if len(col) > 1:
                data[col[0]] = form.get(col[0])

        return data


    def generateForm(self, data={}):
        form = '<table>'
        for col in self.schema:
            if len(col) > 1:
                if col[0] in data:
                    form += self.generateInput(col, data[col[0]])
                else:
                    form += self.generateInput(col)
            else:
                form += '<tr><td colspan="2" style="text-align: center;"><b>{0}</b></td></tr>'.format(col[0])
        form += '</table>'
        return form


    def generateInput(self, col, value=""):
        value = template("{{value}}", value = value)
        form = '<tr>'
        form += '<td><label for="{0}">{1}</label></td>'.format(col[0], col[2])
        form += '<td>'
        if col[1] == 'SEL':
            selList = ''
            for selvalue, sellabel in col[3].iteritems():
                seleted = ""
                if value == selvalue:
                    seleted = "selected"
                selList += '<option value="{0}" {2}>{1}</option>'.format(selvalue, sellabel, seleted)
            form += '<select id="{0}" name="{0}"/ >{1}</select>'.format(col[0], selList)
        elif col[1] == 'INTINDX':
            disabled = "disabled"
            form += '<input id="{0}" name="{0}" type="text" value="{1}" {2} />'.format(col[0], value, disabled)
        elif col[1] == 'DATE':
            form += '<input id="{0}" name="{0}" type="date" value="{1}"/>'.format(col[0], value)
        elif col[1] == 'TIME':
            form += '<input id="{0}" name="{0}" type="time" value="{1}" />'.format(col[0], value)
        elif col[1] == 'INT':
            form += '<input id="{0}" name="{0}" type="number" value="{1}" />'.format(col[0], value)
        elif col[1] == 'REAL':
            form += '<input id="{0}" name="{0}" type="number" value="{1}" />'.format(col[0], value)
        else:
            form += '<input id="{0}" name="{0}" type="text" value="{1}" />'.format(col[0], value)
        form += '</td>'
        form += '</tr>'
        return form


    def getCSV(self):
        selectcols = []
        coltitles = []
        for col in self.schema:
            if len(col) > 1:
                selectcols.append(col[0])
                coltitles.append(col[2])
                
        selectcolsstr = ",".join(selectcols)
        coltitlesstr = ",".join(coltitles)
            
        rows = self.db.list(selectcolsstr, "")

        result = "{0}\r\n".format(coltitlesstr)
        result += "{0}\r\n".format(selectcolsstr)

        for row in rows:
            rowstr = []
            for col in row:
                colstr = str(col)
                colstr = colstr.replace("\"", "\"\"")
                colstr = "\"{0}\"".format(colstr)
                rowstr.append(colstr)
            result += "{0}\r\n".format(",".join(rowstr))
            
        return result


    def importCSV(self, csvfile):
        csvreader = csv.reader(csvfile)
        colLables = csvreader.next()
        colNames = csvreader.next()
        for row in csvreader:
            data = {}
            try:
                for i in range(0, len(colNames)):
                    data[colNames[i]] = row[i]
            except KeyError:
                print "Too few cols"

            patientid = self.addPatient(data)

            print "Added new patient {0}".format(patientid)

        return True
            
        


if __name__ == '__main__':
    settingsfile = '/sdcard/sl4a/res/dataentry.settings'
    #settingsfile = '../res/dataentry.settings'

    app = DataEntry(settingsfile)

    @app.get("/")
    def index():
        redirect("/patients/")


    @app.get("/patients")
    def index():
        redirect("/patients/")


    @app.get("/patients/")
    def list():
        return app.listPatients("")


    @app.post("/search")
    def search():
        ipnumber = request.forms.get('ipnumber')
        return patientip(ipnumber)


    @app.get("/patients.csv")
    def exportcsv():
        response.set_header("Content_Type", "text/csv")
        return app.getCSV()


    @app.get("/patients/importcsv")
    def importcsv():
        return app.template("importcsv")


    @app.post("/patients/importcsv")
    def do_importcsv():
        category   = request.forms.get('category')
        upload     = request.files.get('upload')
        name, ext = os.path.splitext(upload.filename)
        if ext not in ('.csv'):
            return 'File extension not allowed.'

        #upload.save(app.settings["tmp"]) # appends upload.filename automatically
        #filename = app.settings["tmp"]+upload.filename
        
        if app.importCSV(upload.file):
            return 'CSV Uploaded'
        else:
            return "An Error Occured"

        redirect("/list")


    @app.get("/patients/<patientid>")
    def patient(patientid):
        return app.viewPatientById(patientid)


    @app.get("/patients/ip/<ipnumber>")
    def patientip(ipnumber):
        return app.viewPatientByIp(ipnumber)


    @app.post("/patients/<patientid>/update")
    def updatepatient(patientid):
        data = app.processForm(request.forms)

        data['patientid'] = int(patientid)

        result = app.db.update(data)

        if patientid != False:
            redirect("/patients/{0}".format(patientid))
            return 'Patient updates {0}'.format(patientid)
        else:
            return 'Error updating patient'


    @app.get("/patients/new")
    def newpatient():
        return app.newPatientForm()


    @app.post("/patients/new")
    def do_newpatient():
        data = app.processForm(request.forms)

        patientid = app.db.add(data)

        if patientid != False:
            redirect("/patients/{0}".format(patientid))
            return 'Patient saved {0}'.format(patientid)
        else:
            return 'Error saving patient'


    app.run(host="0.0.0.0", port="8080")
    
    '''
    try:
        main.start()
    except sqlite3.InterfaceError:
        main.alert('Error', 'Database interface error')
    except sqlite3.DatabaseError:
        main.lert('Error', 'Database error')
    finally:
        main.exit()
    '''


