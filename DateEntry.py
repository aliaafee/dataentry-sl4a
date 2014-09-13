import android
import sqlite3
import json


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
				query += col[0]
				query += " "
				if col[1] == "INTINDX":
					query += "INTEGER PRIMARY KEY"
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


	def add(self, data):
		datai = {}
		for col in self.schema:
			if col[1] != 'INTINDX':
				try:
					datai[col[0]] = data[col[0]]
				except KeyError:
					datai[col[0]] = ''

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


	def get(self, col, filter):
		query = self.squery.format(col)

		try:
			row = self.db.execute(query, { col : filter }).fetchone()
		except sqlite3.DatabaseError:
			return False

		if row == None:
			return False

		result = {}
		for	i in range(0, len(self.schema)):
			col = self.schema[i]
			result[col[0]] = row[i]

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




class DataEntry:
	def __init__(self, droid, schema, dbfile):
		self.title = "Data Entry"
		self.droid = droid

		self.db = DataBase(dbfile, schema)
		self.schema = schema


	def start(self):
		self.droid.webViewShow('file:///sdcard/sl4a/res/DateEntryUI.html')

		while True:
			event = self.droid.eventWait().result

			if event['name'] == 'load':
				self.droid.eventPost('setForm', self.generateForm());
			elif event['name'] == 'add':
				self.addPatient(event['data'])
			elif event['name'] == 'viewbyip':
				self.viewPatientByIp(event['data'])
			elif event['name'] == 'viewbyid':
				self.viewPatientById(int(event['data']))
			elif event['name'] == 'update':
				self.updatePatient(event['data'])
			elif event['name'] == 'list':
				self.listPatients(event['data'])
			elif event['name'] == 'exit':
				self.exit()


	def status(self, message):
		self.droid.eventPost('status', message)


	def alert(self, title, message):
		self.status(message)
		droid.dialogCreateAlert(title, message)
		droid.dialogSetPositiveButtonText('Ok')
		droid.dialogShow()


	def addPatient(self, datastr):
		data = json.loads(datastr)

		patientid = self.db.add(data)

		if patientid != False:
			self.status('Patient saved')
			self.viewPatientById(patientid)
		else:
			self.status('Error saving patient')


	def updatePatient(self, datastr):
		data = json.loads(datastr)
		patientid = int(data['patientid'])

		result = self.db.update(data)

		if result != False:
			self.alert('Update', 'Update Complete')
			self.viewPatientById(patientid)
		else:
			self.alert('Update', 'Error updating patient id {0}'.format(patientid))


	def viewPatientByIp(self, ipnumber):
		'''
		data = ''
		for patientid, patient in self.patients.iteritems():
			if patient['ipnumber'] == ipnumber:
				data = patient
		'''
		data = self.db.get('ipnumber', ipnumber)

		if data != False:
			self.droid.eventPost('loadFormData', json.dumps(data))
		else:
			self.status('Patient not Found')


	def viewPatientById(self, patientid):
		data = self.db.get('patientid', patientid)

		if data != False:
			self.droid.eventPost('loadFormData', json.dumps(data))
		else:
			self.status('Patient not Found')


	def listPatients(self, filter):
		rows = self.db.list('patientid, ipnumber, name, age, sex', filter)

		html = "<table>"
		html += "<thead><tr><td>#</td><td>IP</td><td>Name</td><td>Age</td><td>Sex</td></tr></thead>"
		html += "<tbody>"
		if rows != False:
			for row in rows:
				html += '<tr onClick="droid.eventPost(\'viewbyid\', \'{0}\')"><td><a href="javascript:droid.eventPost(\'viewbyid\', \'{0}\')">{0}</a></td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td></tr>'.format(row[0], row[1], row[2], row[3], row[4])
		else:
			self.status('Non found')
		html += "</tbody>"
		html += "</table>"
		self.droid.eventPost('setList', html)


	def generateForm(self):
		form = '<table>'
		for col in self.schema:
			form += self.generateInput(col)
		form += '</table>'
		return form


	def generateInput(self, col, value='', disabled=False):
		if disabled:
			disabled = 'disabled'
		else:
			disbaled = ''
		form = '<tr>'
		form += '<td><label for="{0}">{1}</label><td>'.format(col[0], col[2])
		form += '<td>'
		if col[1] == 'SEL':
			selList = ''
			for selvalue, sellabel in col[3].iteritems():
				if value == selvalue:
					selList += '<option value={0} selected="selected">{1}</option>'.format(selvalue, sellabel)
				else:
					selList += '<option value={0}>{1}</option>'.format(selvalue, sellabel)
			form += '<select name="{0}"/ >{1}</select>'.format(col[0], selList)
		elif col[1] == 'INTINDX':
			form += '<input name="{0}" type="text" value="{0}" disabled />'.format(col[0])
		elif col[2] == 'DATE':
			form += '<input name="{0}" type="date" value="{0}"/>'.format(col[0])
		else:
			form += '<input name="{0}" type="text" value="{0}"/>'.format(col[0])
		form += '</td>'
		form += '</tr>'
		return form

		
	def exit(self):
		self.db.close()
		exit()




if __name__ == '__main__':
	droid = android.Android()

	dbfile = "/sdcard/sl4a/DataEntry.db"
	schema = [
		('patientid',	'INTINDX',	'PatientId'),
		('ipnumber',	'INT',	'IpNumber'),
		('name',	'STR',	'Name'),
		('sex',	'SEL',	'Sex', {'m' : 'Male', 'f' : 'Female'}),
		('age',	'INT',	'Age'),
		('admittedDate',	'DATE',	'Admitted Date'),
		('admittedTime',	'TIME',	'Admitted Time'),
		('DischargedDate',	'DATE',	'Discharged Date'),
		('hb',	'REAL',	'Hemoglobin(mg/dl)')
	]
	
	try:
		main = DataEntry(droid, schema, dbfile)
		main.start()
	except sqlite3.InterfaceError:
		main.alert('Error', 'Database interface error')
	except sqlite3.DatabaseError:
		main.lert('Error', 'Database error')
	finally:
		main.exit()
