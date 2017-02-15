# -*- coding: utf-8 -*-
"""
	Crud Restful API Generator

	Generates Golang backend API from Postgresql sql
"""

import sys,os,json
from . import utils
import pkg_resources

def main():
    if len(sys.argv) < 2:
        print("Usage: appomatic [appomatic_config.json]")
        return
    config = json.loads(open(sys.argv[1],"r").read())

    #preliminary dir
    sql = utils.SqlParser(config["db_file"])
    db_models = sql.parse()
    #print json.dumps(db_models)

    # Generate main file once
    if not os.path.isfile("./main.go"):
        utils.generate_main("./main.go", db_models, config)

    utils.generate_routes("./gen_routes.go", db_models, config)

    for m in db_models:
        #CORE API

        # Setup generated code in CWD (target project dir)
        path = os.path.join(os.getcwd(), "modules", m)
        utils.setupPathFolder(path)
        utils.generate_api(path+"gen_api.go", m, db_models, config)
        utils.generate_db(path+"gen_db.go", m, db_models, config)
        utils.generate_types(path+"gen_types.go", m, db_models, config)

        #helpful generated items
        relPath = "/".join(["src", "queries", m])
        querypath = pkg_resources.resource_filename(__name__, relPath)
        utils.setupPathFolder(querypath)
        utils.generate_curl_queries(querypath+"gen_queries.sh", m, db_models, config)

    print("Generated ", len(db_models), " Modules ", sum([len(db_models[x]) for x in db_models]), " Submodules")
