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
	'NUMERIC':'*float64',
	'SERIAL':'*int64',
	'MEDIUMTEXT':"*string",
	'BOOLEAN':"*bool",
	'BIGINT':'*int64',
	'VARCHAR':'*string',
	'TEXT':'*string',
	'JSON':'*json.RawMessage',
	'JSONB':'*json.RawMessage',
	'TIMESTAMP WITH TIME ZONE':'time.Time',
	'TIMESTAMP WITH TIME ZONE(CURRENT_TIMESTAMP)':'time.Time',

}

default_vals = {
	"*string":"&default_string",
	"*int64":"&default_int",
	"*float64":"&default_float",
	"*json.RawMessage":{'"foo"':'"bar"'},
	"*bool":"&default_bool",
}

put_vals = {
	"*string":"&new_string",
	"*int64":"&new_int",
	"*float64":"&new_float",
	"*json.RawMessage":{'"bar"':'"foo"'},
	"*bool":"&new_bool",
}

default_types = {
	"*string":'default_string := "foo"',
	"*int64":"default_int := int64(1)",
	"*float64":"default_float := float64(3.14)",
	"*json.RawMessage":'{"foo":"bar"}',
	"*bool":"default_bool := false",
}

new_types = {
	"*string":'new_string := "bar"',
	"*int64":"new_int := int64(321)",
	"*float64":"new_float := float64(41.3)",
	"*json.RawMessage":'{"bar":"foo"}',
	"*bool":"new_bool := false",
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
			if 'module' not in self.app[k]['comment']:
				continue

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
		elif line.startswith("ALTER TABLE") and re.search("FOREIGN KEY", line):
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
		name = re.search(r'".*?"', line)
		if name == None:
			#print("Error parsing table name")
			return
		name = name.group(0).replace('"','')
		self.create_table(name)
		self.current_table = name

	def parse_col(self, line):
		""" parses a column, add it to the current table"""
		items = re.findall(r"\w+", line)
		name = items[0].replace('"','')
		col_type = items[1]
		db_type = col_type
		#special case for varchar
		if col_type == "VARCHAR":
			db_type = col_type + "(" + items[2] + ")"

		self.app[self.current_table]["columns"].append({
			"title":name,
			"db_type":db_type,
			"go_type":postgres2go[col_type],
			"struct_var":name[0].upper()+name[1:]
		})

	def parse_comment(self, line):
		""" parses the comment as json, then adds to the current table """
		if self.current_table == "":
			return
		com = re.search(r"'.*?'", line).group(0)
		com = com.replace("'","")
		d = {}
		try:
			d = json.loads(com)
		except:
			#invalid comment type
			return
		self.app[self.current_table]["comment"] = d


	def parse_rel(self, line):
		""" parses the relation and adds a note to the relative tables """
		items = re.findall(r"\w+", line)
		child_table = items[2]
		col_key = items[6]
		parent_table = items[8].replace('"','')

		#print("parent", parent_table)
		#print("child", child_table)

		if 'module' not in self.app[parent_table]['comment']:
			return

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
	s = routes.render(db_models=db_models, config=config, date=time.strftime("%m/%d/%Y"), package="server")
	f = open(fp, "w")
	f.write(s)
	f.close()

def getOkCols(model, useBool=True):
	"""
	Defines which columns can be overwritten in an update 
	useBool = True sets them as a bool 'true' / 'false'
	useBool = False returns a list of items where the value was 'true'
	"""
	ok = {}
	exclude = ['date_created', 'date_modified', 'deleted', 'password']
	for col in model["columns"]:
		if col["db_type"] == 'SERIAL':
			ok[col['title']] = 'false'
		elif col['title'].startswith('id_'):
			ok[col['title']] = 'false'
		elif col['title'] in exclude:
			ok[col['title']] = 'false'
		else:
			ok[col['title']] = 'true'

	if useBool == False:
		return [k[0].upper()+k[1:] for k in ok if ok[k] == 'true']

	return ok



def generate_api(fp, mname, db_models, config):
	""" Generates our API file """

	f = open(fp, "w")

	#keeps track off all function names we're generating for relations
	generated = {}

	headerT = templateEnv.get_template( "/api/api_header.go")
	packages = ["net/http",config["path"]+"/modules/utils", "github.com/gorilla/mux", "strconv"]
	header = headerT.render(module_name=mname, packages=packages, date=time.strftime("%m/%d/%Y"))
	f.write(header)

	for submodule in db_models[mname]:
		struct_name = submodule[0].upper() + submodule[1:]

		get_one = templateEnv.get_template( "/api/get_one.go")
		f.write(get_one.render(table_name=submodule, struct_name=struct_name))

		post_one = templateEnv.get_template( "/api/post_one.go")
		f.write(post_one.render(table_name=submodule, struct_name=struct_name))

		put_one = templateEnv.get_template( "/api/put_onev2.go")
		ok_cols = getOkCols(db_models[mname][submodule], useBool=False)
		f.write(put_one.render(table_name=submodule, struct_name=struct_name, okCols=ok_cols))

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
	packages = ["database/sql","time"]
	header = headerT.render(module_name=mname, packages=packages, date=time.strftime("%m/%d/%Y"))
	f.write(header)

	for submodule in db_models[mname]:
		struct_name = submodule[0].upper() + submodule[1:]
		post_columns = postCols(db_models[mname][submodule])
		len_post_cols = len(post_columns)

		t = templateEnv.get_template( "/db/read_one.go")
		f.write(t.render(table_name=submodule, struct_name=struct_name, post_columns=post_columns, model=db_models[mname][submodule], len_post_cols=len_post_cols, len_cols=len(db_models[mname][submodule]['columns'])))

		t = templateEnv.get_template( "/db/create_one.go")
		post_values  = postValues(db_models[mname][submodule])
		f.write(t.render(table_name=submodule, struct_name=struct_name, post_columns=post_columns, post_values=post_values, len_cols=len_post_cols, len_rec_cols=len_post_cols+1, model=db_models[mname][submodule]))

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
				f.write(get_children.render(table_name=submodule, len_cols=len_cols, rel=rel, model=model, struct_name=struct_name, post_columns=post_columns, len_post_cols=len_post_cols))

	f.close()

def addSpacing(model, minsize):
	""" adds a set amount of padding for the vars in the structs for readability"""
	for col in model['columns']:
		size = len(col['title'])+len(col['go_type'])
		diff = minsize - size
		col['spacing'] = " "*diff
	return model

def genDefaults(model, key, m):
	for col in model['columns']:
		#skip settting id default
		if col["db_type"] == 'SERIAL':
			continue 
		go_type = col["go_type"]

		if go_type in m:
			col[key] = m[go_type]
	return model

def getDefaultTypes(model, m):
	types = {}
	for col in model['columns']:
		#skip settting id default
		if col["db_type"] == 'SERIAL':
			continue 
		go_type = col["go_type"]

		if go_type in m:
			types[m[go_type]] = True
	return types


def generate_types(fp, mname, db_models, config):
	""" Generates our types file """

	f = open(fp, "w")
	t = templateEnv.get_template( "/types/types_header.go")

	packages = {}

	#check if we need to add json support to this module
	for sub in db_models[mname]:
		for c in db_models[mname][sub]['columns']:
			if c['db_type'].startswith("JSON"):
				packages["encoding/json"]=True
				break

	f.write(t.render(module_name=mname, date=time.strftime("%m/%d/%Y"), packages=packages.keys()))
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

def generate_tests(fp, mname, db_models, config):
	""" Generates tests for our api """
	f = open(fp+mname+"_test.go", "w")

	th = templateEnv.get_template( "/tests/crud_header.go")
	f.write(th.render(package_name="integration_tests", package_import=config['path']+"/modules/"+mname))

	for submodule in db_models[mname]:
		t = templateEnv.get_template( "/tests/crud.go")
		struct_name = submodule[0].upper() + submodule[1:]
		model = addSpacing(db_models[mname][submodule], 30)
		model = genDefaults(model, "value", default_vals)
		model = genDefaults(model, "put_value", put_vals)
		dt = getDefaultTypes(model, default_types)
		nt = getDefaultTypes(model, new_types)
		route = "/api/"+config['api_version']+"/"+submodule+"/"
		f.write(t.render(submodule=submodule, module=mname, route=route, model=model, struct_name=struct_name, default_types=dt, new_types=nt))







