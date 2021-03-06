package {{package}}

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
	router.HandleFunc("/api/{{config['api_version']}}/{{submodule}}/{{ '{' }}{{submodule}}_id:[0-9]+}/", route_handler({{module}}.GetOne_{{submodule}})).Methods("GET")
	router.HandleFunc("/api/{{config['api_version']}}/{{submodule}}/", route_handler({{module}}.PostOne_{{submodule}})).Methods("POST")
	router.HandleFunc("/api/{{config['api_version']}}/{{submodule}}/{{ '{' }}{{submodule}}_id:[0-9]+}/", route_handler({{module}}.PutOne_{{submodule}})).Methods("PUT")
	router.HandleFunc("/api/{{config['api_version']}}/{{submodule}}/{{ '{' }}{{submodule}}_id:[0-9]+}/", route_handler({{module}}.DeleteOne_{{submodule}})).Methods("DELETE"){% for rel in db_models[module][submodule]["relations"] %}{% if rel['relation'] == 'belongsTo' %} 
	router.HandleFunc("/api/{{config['api_version']}}/{{submodule}}_By_{{rel['key']}}/{{ '{' }}{{rel['key']}}_id:[0-9]+}/", route_handler({{module}}.GetAll_{{submodule}}_By_{{rel['key']}})).Methods("GET"){% endif %}{% endfor %}


	{% endfor%}
	{% endfor%}
}