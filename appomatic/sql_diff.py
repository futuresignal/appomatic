import os,json,time
import pkg_resources
from . import utils
import jinja2

# Load resources from the appomatic directory rather than the CWD
resource_package = __name__
templatePath = pkg_resources.resource_filename(resource_package, "templates")

templateLoader = jinja2.FileSystemLoader( searchpath=templatePath )
templateEnv = jinja2.Environment( loader=templateLoader, lstrip_blocks=True, trim_blocks=True )

def compare_cols(a, b):
	""" Takes two db table objects, compares their columns for new columns in b """
	old_cols = {}
	new_cols = {}

	for col in a["columns"]:
		new_cols[col["title"]] = col
	for col in b["columns"]:
		old_cols[col["title"]] = col

	cols = []

	for col in new_cols:
		if col not in old_cols:
			cols.append(new_cols[col])
	return cols

def compare_rels(a, b):
	""" Takes two db table objects, compares their relations for new relations in b """
	old_rels = {}
	new_rels = {}

	for rel in a["relations"]:
		new_rels[rel["key"]] = rel
	for rel in b["relations"]:
		old_rels[rel["key"]] = rel

	rels = []

	for rel in new_rels:
		if rel not in old_rels:
			rels.append(new_rels[rel])
	return rels

def compare_tables(a,b):
	""" compares two tables, returns any new columns, relations in b """
	#check for new columns
	new_cols = compare_cols(a, b)
	#check for new relations
	new_rels = compare_rels(a, b)
	return {"rels":new_rels, "cols":new_cols}

def compare(a,b,d):
	""" compares two db objects a & b, any new items in b are added to the dictionary 'd' """

	for m in b: 
		#new module, add all tables
		if m not in a:
			for t in b[m]:
				temp = b[m][t]
				temp["title"] = t #adds our table title to the table object
				d["tables"].append(temp)
				d["relations"] += temp["relations"] #add any relations that are part of this table
			continue

		#check for new tables
		for t in b[m]:
			if t not in a[m]:
				temp = b[m][t]
				temp["title"] = t #adds our table title to the table object
				d["tables"].append(temp)
				d["relations"] += temp["relations"] #add any relations that are part of this table
				continue

			dx = compare_tables(b[m][t], a[m][t])
			for col in dx["cols"]:
				temp = col
				temp["table"] = t #adds our table to the column object
				d["columns"].append(temp)

			for rel in dx["rels"]:
				d["relations"].append(rel)


def gen_migration(o, n, path):
	""" Given two sql files old = o and new = n 
		writes a simple migration to the path provided
		Handles: new tables, new relations and new columns 
	"""

	old = utils.SqlParser(o)
	old_models = old.parse()

	new = utils.SqlParser(n)
	new_models = new.parse()

	additions = {"tables":[],"columns":[],"relations":[]} #types: "table, col, foreign_key"
	deletions = {"tables":[],"columns":[],"relations":[]} #types: "table, col, foreign_key"

	
	compare(old_models,new_models,additions)
	compare(new_models,old_models,deletions)

	#print("Additions", additions)
	#print("Deletions", deletions)

	f = open(path, "w")
	f.write("--Generated Migration "+time.strftime("%m/%d/%Y")+" \n")
	f.write("--Deleted Relations\n")
	#run our deletions first
	for rel in deletions["relations"]:
		if rel["relation"] == "belongsTo":
			#print(rel)
			tmpl = templateEnv.get_template( "/sql/drop_fk.sql")
			f.write(tmpl.render(table_name=rel["owner"], key=rel["key"]))
			f.write("\n")
	f.write("\n")
	
	f.write("--Deleted Tables\n")
	for t in deletions["tables"]:
		#write our table
		tmpl = templateEnv.get_template( "/sql/drop_table.sql")
		f.write(tmpl.render(table_name=t["title"]))
		f.write("\n")
	f.write("\n")
	
	f.write("--Deleted Columns\n")
	for c in deletions["columns"]:
		tmpl = templateEnv.get_template( "/sql/drop_col.sql")
		f.write(tmpl.render(table_name=c["table"], col_name=c["title"]))
		f.write("\n")
	f.write("\n")
	
	#run our additons second
	f.write("--Created tables\n")
	for t in additions["tables"]:
		#write our table
		tmpl = templateEnv.get_template( "/sql/create_table.sql")
		f.write(tmpl.render(table_name=t["title"], cols=t["columns"], comment=json.dumps(t["comment"])))
		f.write("\n")
	f.write("\n")
	
	f.write("--Created columns\n")
	for c in additions["columns"]:
		tmpl = templateEnv.get_template( "/sql/add_col.sql")
		f.write(tmpl.render(table_name=c["table"], col_name=c["title"], db_type=c["db_type"]))
		f.write("\n")
	f.write("\n")
	
	f.write("--Created relations\n")
	for rel in additions["relations"]:
		if rel["relation"] == "belongsTo":
			tmpl = templateEnv.get_template( "/sql/add_fk.sql")
			f.write(tmpl.render(table_name=rel["owner"], key=rel["key"], target=rel["table"]))
			f.write("\n")

		


	



