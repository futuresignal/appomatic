# -*- coding: utf-8 -*-
import re, json, os, time
import jinja2
import pkg_resources

# Load resources from the appomatic directory rather than the CWD
resource_package = __name__
templatePath = pkg_resources.resource_filename(resource_package, "templates")

templateLoader = jinja2.FileSystemLoader( searchpath=templatePath )
templateEnv = jinja2.Environment( loader=templateLoader, lstrip_blocks=True, trim_blocks=True )

postgres2go = { 
	
	'DATETIME':'*string',
	'DATE':'*string',
	'STRING':'*string',
	'INTEGER':'*int64',
	'DECIMAL':'*float64',
	'SERIAL':'*int64',
	'MEDIUMTEXT':"*string",
	'BOOLEAN':"*bool",
	'BIGINT':'*int64',
	'VARCHAR':'*string',
	'TEXT':'*string',
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
			mname = self.app[k]['comment']['module']
			if mname not in modules:
				modules[mname] = {k:self.app[k]}
			else:
				modules[mname][k] = self.app[k]

		#print(json.dumps(modules))

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
		elif line.startswith("ALTER TABLE"):
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
			"go_type":postgres2go[col_type],
			"struct_var":name[0].upper()+name[1:]
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

		#print("parent", parent_table)
		#print("child", child_table)

		parent_module = self.app[parent_table]['comment']['module']
		child_module = self.app[child_table]['comment']['module']

		#add parent ref
		self.app[child_table]["relations"].append({
			"relation":"belongsTo",
			"table":parent_table,
			"key":col_key,
			"module":parent_module,
			"owner":child_table
		})
		
		#add child ref
		self.app[parent_table]["relations"].append({
			"relation":"hasMany",
			"table":child_table,
			"key":col_key,
			"module":child_module
		})




def setupPathFolder(fp):
	if not os.path.exists(fp):
		os.makedirs(fp)

def generate_main(fp, db_models, config):
	""" generates our main file """
	main = templateEnv.get_template( "/main/main.go")
	s = main.render(config=config)
	f = open(fp, "w")
	f.write(s)
	f.close()

def generate_routes(fp, db_models, config):
	""" creates and adds any generated routes """
	routes = templateEnv.get_template( "/main/routes.go")

	s = routes.render(db_models=db_models, config=config, date=time.strftime("%m/%d/%Y"), package=config["server_dir"])
	f = open(fp, "w")
	f.write(s)
	f.close()

def okCols(model):
	""" 
	Defines which columns can be overwritten in an update
	"""
	ok = {}
	for col in model["columns"]:
		if col["db_type"] == 'SERIAL':
			ok[col['title']] = 'false'
		elif col['title'].startswith('id_'):
			ok[col['title']] = 'false'
		else:
			ok[col['title']] = 'true'
	return ok


def generate_api(fp, mname, db_models, config):
	""" Generates our API file """

	f = open(fp, "w")

	#keeps track off all function names we're generating for relations
	generated = {}

	headerT = templateEnv.get_template( "/api/api_header.go")
	packages = ["net/http",config["path"]+"/modules/utils", "github.com/gorilla/mux", "strconv", "fmt", "log", "encoding/json"]
	header = headerT.render(module_name=mname, packages=packages, date=time.strftime("%m/%d/%Y"))
	f.write(header)

	for submodule in db_models[mname]:
		struct_name = submodule[0].upper() + submodule[1:]

		get_one = templateEnv.get_template( "/api/get_one.go")
		f.write(get_one.render(table_name=submodule, struct_name=struct_name))
		
		post_one = templateEnv.get_template( "/api/post_one.go")
		f.write(post_one.render(table_name=submodule, struct_name=struct_name))
		
		put_one = templateEnv.get_template( "/api/put_onev2.go")
		f.write(put_one.render(table_name=submodule, struct_name=struct_name))
		
		delete_one = templateEnv.get_template( "/api/delete_one.go")
		f.write(delete_one.render(table_name=submodule, struct_name=struct_name))

		#any relations add those here
		for rel in db_models[mname][submodule]["relations"]:
			if rel['relation'] == 'belongsTo':
				get_children = templateEnv.get_template( "/api/get_children.go")
				f.write(get_children.render(table_name=submodule, table_parent_fkey=rel["key"], struct_name=struct_name))

	f.close()

def postCols(model):
	""" returns a list of columns that can be posted to"""
	include = []
	for col in model['columns']:
		if col["db_type"] == 'SERIAL':
			continue #skip main id
		else:
			include.append(col)
	return include

def postValues(model):
	""" sets the values """
	values = []
	defaults = {"date_created":'time.Now().Unix()', "date_modified":'time.Now().Unix()', "deleted":'false'}
	for col in model['columns']:
		if col["db_type"] == 'SERIAL':
			continue #skip main id
		elif col['title'] in defaults:
			values.append(defaults[col['title']])
		else:
			values.append("&x."+col["struct_var"])
	return values


def putCols(model):
	""" returns a list of columns that can be updated """
	cols = []
	exclude = ["date_created", "date_modified", "deleted"]

	for col in model["columns"]:
		if col["db_type"] == 'SERIAL':
			continue #skip main id
		elif col['title'].startswith('id_'):
			continue #skip foreign keys
		elif col['title'] in exclude:
			continue
		else:
			cols.append(col)
	return cols

def generate_db(fp, mname, db_models, config):
	""" Generates our db file """

	f = open(fp, "w")

	headerT = templateEnv.get_template( "/db/db_header.go")
	packages = ["database/sql","time", config["path"]+"/modules/utils"]
	header = headerT.render(module_name=mname, packages=packages, date=time.strftime("%m/%d/%Y"))
	f.write(header)

	for submodule in db_models[mname]:
		struct_name = submodule[0].upper() + submodule[1:]

		t = templateEnv.get_template( "/db/read_one.go")
		f.write(t.render(table_name=submodule, struct_name=struct_name,  model=db_models[mname][submodule], len_cols=len(db_models[mname][submodule]['columns'])))
		
		t = templateEnv.get_template( "/db/create_one.go")
		post_columns = postCols(db_models[mname][submodule])
		post_values  = postValues(db_models[mname][submodule])
		len_cols = len(post_columns)
		f.write(t.render(table_name=submodule, struct_name=struct_name, post_columns=post_columns, post_values=post_values, len_cols=len_cols, model=db_models[mname][submodule]))
		
		put_one = templateEnv.get_template( "/db/update_one.go")
		put_cols = putCols(db_models[mname][submodule])
		f.write(put_one.render(table_name=submodule, struct_name=struct_name, put_cols=put_cols, len_cols=len(put_cols)))
		
		delete_one = templateEnv.get_template( "/db/delete_one.go")
		f.write(delete_one.render(table_name=submodule, struct_name=struct_name,))

		#any relations add those here
		for rel in db_models[mname][submodule]["relations"]:
			if rel['relation'] == 'belongsTo':
				get_children = templateEnv.get_template( "/db/read_children.go")
				#get relative module
				#len_cols = len(db_models[rel_m][rel['table']]['columns'])
				
				len_cols = len(db_models[mname][submodule]['columns'])
				model = db_models[mname][submodule]
				rel_struct = rel['table'][0].upper()+rel['table'][1:]
				f.write(get_children.render(table_name=submodule, len_cols=len_cols, rel=rel, model=model, struct_name=struct_name))

	f.close()

def addSpacing(model, minsize):
	""" adds a set amount of padding for the vars in the structs for readability"""
	for col in model['columns']:
		size = len(col['title'])+len(col['go_type'])
		diff = minsize - size
		col['spacing'] = " "*diff
	return model


def generate_types(fp, mname, db_models, config):
	""" Generates our types file """

	f = open(fp, "w")
	t = templateEnv.get_template( "/types/types_header.go") 
	f.write(t.render(module_name=mname, date=time.strftime("%m/%d/%Y")))
	for submodule in db_models[mname]:
		struct_name = submodule[0].upper() + submodule[1:]
		t = templateEnv.get_template( "/types/simple.go")
		model = addSpacing(db_models[mname][submodule], 30)
		f.write(t.render(table_name=submodule,  model=model, struct_name=struct_name))
		
	f.close()

def json_type(model):
	""" Adds default types to our model and creates a json string"""
	j = {}
	
	exclude = ["date_created", "date_modified", "deleted"]
	for col in model['columns']:
		if col["title"] in exclude:
			continue
		if col["db_type"] == 'SERIAL':
			j[col["title"]] = 1
		elif col["db_type"] == 'INTEGER':
			j[col["title"]] = 1
		elif col["db_type"].startswith("VARCHAR"):
			j[col["title"]] = ""
		elif col["db_type"] == 'TEXT':
			j[col["title"]] = ""
		elif col["db_type"] == 'BOOLEAN':
			j[col["title"]] = False	
	return json.dumps(j)

def generate_curl_queries(fp, mname, db_models, config):
	""" for each of our modules, generate sample curl queries"""
	f = open(fp, "w")
	
	for sub in db_models[mname]:
		t = templateEnv.get_template( "/curl/curl_get.sh")
		f.write(t.render(username="test@gmail.com", password="xyz", submodule=sub, config=config))
		
		t = templateEnv.get_template( "/curl/curl_post.sh")
		j = json_type(db_models[mname][sub])
		f.write(t.render(json=j, submodule=sub, model=db_models[mname][sub], config=config))
		
		put_one = templateEnv.get_template( "/curl/curl_put.sh")
		f.write(put_one.render(json=j, submodule=sub, config=config))
		
		delete_one = templateEnv.get_template( "/curl/curl_delete.sh")
		f.write(delete_one.render(submodule=sub, config=config))

		#any relations add those here
		for rel in db_models[mname][sub]["relations"]:
			if rel['relation'] == 'hasMany':
				get_children = templateEnv.get_template( "/curl/curl_get_children.sh")
				f.write(get_children.render(submodule=sub, config=config, rel=rel, child=db_models[rel['module']][rel['table']]))
		f.write("\n\n")
	f.close()



