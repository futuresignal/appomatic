# -*- coding: utf-8 -*-
"""
	Crud Restful API Generator

	Generates Golang backend API from Postgresql sql
"""
from __future__ import print_function
import sys,os,json,time
from . import utils
from . import sql_diff
import pkg_resources

def main():
    if len(sys.argv) < 2:
        print("Usage: appomatic [appomatic_config.json]")
        return
    config = json.loads(open(sys.argv[1],"r").read())

    #generate our migration file if we have a prev_schema supplied
    if "prev_schema" in config and config["prev_schema"] != "":
        sql_diff.gen_migration(config["prev_schema"], config["schema"], config["migration"])
        print("Migration file located at ", config["migration"])

    #parse our sql into a dict respresentation of the models
    sql = utils.SqlParser(config["schema"])
    db_models = sql.parse()

    # Generate main file once
    if not os.path.isfile(os.getcwd()+"/main.go"):
        utils.generate_main(os.getcwd()+"/main.go", db_models, config)

    utils.generate_routes(os.getcwd()+"/"+config["server_dir"]+"/gen_routes.go", db_models, config)

    for m in db_models:
        #CORE API
        # Setup generated code in CWD (target project dir)
        #path = os.path.join(os.getcwd(), "modules", m)
        path = "/".join([os.getcwd(), config["module_dir"], m, ""])
        utils.setupPathFolder(path)
        utils.generate_api(path+"gen_api.go", m, db_models, config)
        utils.generate_db(path+"gen_db.go", m, db_models, config)
        utils.generate_types(path+"gen_types.go", m, db_models, config)

        #helpful generated items
        relPath = "/".join([os.getcwd(), config["tools_dir"], "queries", m, ""])
        utils.setupPathFolder(relPath)
        utils.generate_curl_queries(relPath+"gen_queries.sh", m, db_models, config)
        utils.generate_tests(config["integration_tests_dir"], m, db_models, config)

    print("Generated ", len(db_models), " Modules ", sum([len(db_models[x]) for x in db_models]), " Submodules")

