# -*- coding: utf-8 -*-
import json, re

postgres2go = { 
	'DATETIME':'string',
	'DATE':'string',
	'STRING':'string',
	'INTEGER':'int64',
	'DECIMAL':'float64',
	'SERIAL':'int64',
	'MEDIUMTEXT':"string",
	'BOOLEAN':"bool",
	'BIGINT':'int64',
	'VARCHAR':'string',
	'TEXT':'string',
	'TIMESTAMP WITH TIME ZONE':'time.Time',
	'TIMESTAMP WITH TIME ZONE(CURRENT_TIMESTAMP)':'time.Time',
}


class SqlParser:
	""" 
		a simple sql parser 
		returns a dict representation of the tables
	"""
	def __init__(self, db_path):
		self.db_path = db_path
		self.db_file = open(db_path)
		self.state = "ignore" #ignore, table, col, comment, relation
		self.current_table = ""
		self.app = {} #dict representation of our db

	def parse(self):
		""" main function, runs the parser"""
		for line in self.db_file:
			self.parse_state(line)
		#package all of our tables into modules
		modules = {}
		for k in self.app:
			print self.app[k]['comment']
			mname = self.app[k]['comment']['module']
			if mname not in modules:
				modules[mname] = {k:self.app[k]}
			else:
				modules[mname][k] = self.app[k]

		return modules

	def parse_state(self, line):
		""" parses the current line and sets our current parser state """
		if line.startswith("CREATE TABLE"):
			self.state = "table"
			self.parse_table(line)
		elif line.startswith('"'):
			self.state = "col"
			self.parse_col(line)
		elif line.startswith("COMMENT"):
			self.state = "comment"
			self.parse_comment(line)
		elif line.startswith("ALTER"):
			self.state = "relation"
			self.parse_rel(line)
		else:
			self.state = "ignore"

	def create_table(self, table_name):
		""" checks if table exists, then creates it """
		if table_name not in self.app:
			self.app[table_name] = {"comment":{}, "columns":[],"relations":[]}

	def parse_table(self, line):
		""" Parses table name, creates an inner dict in the app"""
		name = re.search(r'".*?"', line).group(0).replace('"','')
		self.create_table(name)
		self.current_table = name

	def parse_col(self, line):
		""" parses a column, add it to the current table"""
		items = re.findall(r"\w+", line)
		name = items[0].replace('"','')
		col_type = items[1]
		
		self.app[self.current_table]["columns"].append({
			"title":name,
			"db_type":col_type,
			"go_type":postgres2go[col_type]
		})

	def parse_comment(self, line):
		""" parses the comment as json, then adds to the current table """
		com = re.search(r"'.*?'", line).group(0)
		com = com.replace("'","")
		self.app[self.current_table]["comment"] = json.loads(com)

	def parse_rel(self, line):
		""" parses the relation and adds a note to the relative tables """
		items = re.findall(r"\w+", line)
		child_table = items[2]
		col_key = items[6]
		parent_table = items[8].replace('"','')
		#add parent ref
		self.app[self.current_table]["relations"].append({
			"relation":"belongsTo",
			"table":parent_table,
			"key":col_key
		})
		
		#add child ref
		self.app[parent_table]["relations"].append({
			"relation":"hasMany",
			"table":child_table,
			"key":col_key
		})






