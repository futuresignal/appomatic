package {{module_name}}

/* Generated on {{date}} */

import (
	{% for p in packages %}
	"{{p}}"
	{% endfor %}
)

var (
	db *sql.DB
)

func SetDB(database *sql.DB){
	db = database
}

