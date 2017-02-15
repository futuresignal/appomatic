package main

/* Generated on {{date}} */

import (
	"github.com/gorilla/mux"
	"database/sql"

	//generated imports
    {% for module in db_models %}
    "{{config['path']}}/modules/{{module}}"
    {% endfor %}
)

func InitGeneratedDbPointers(db *sql.DB){
	{% for module in db_models %}
    {{module}}.SetDB(db)
    {% endfor%}
}

func InitGeneratedRoutes(router *mux.Router){
	{% for module in db_models %}
	
	//{{module}} routes
	{% for submodule in db_models[module] %}
	//{{submodule}} routes
	router.HandleFunc("/api/{{config['api_version']}}/{{submodule}}/{{ '{' }}{{submodule}}_id:[0-9]+}/", {{module}}.GetOne_{{submodule}}).Methods("GET")
	router.HandleFunc("/api/{{config['api_version']}}/{{submodule}}/", {{module}}.PostOne_{{submodule}}).Methods("POST")
	router.HandleFunc("/api/{{config['api_version']}}/{{submodule}}/{{ '{' }}{{submodule}}_id:[0-9]+}/", {{module}}.PutOne_{{submodule}}).Methods("PUT")
	router.HandleFunc("/api/{{config['api_version']}}/{{submodule}}/{{ '{' }}{{submodule}}_id:[0-9]+}/", {{module}}.DeleteOne_{{submodule}}).Methods("DELETE"){% for rel in db_models[module][submodule]["relations"] %}{% if rel['relation'] == 'belongsTo' %} 
	router.HandleFunc("/api/{{config['api_version']}}/{{submodule}}_By_{{rel['table']}}/{{ '{' }}{{rel['table']}}_id:[0-9]+}/", {{module}}.GetAll_{{submodule}}_By_{{rel['table']}}).Methods("GET"){% endif %}{% endfor %}


	{% endfor%}
	{% endfor%}
}