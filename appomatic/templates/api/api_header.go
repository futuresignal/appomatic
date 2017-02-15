package {{module_name}}

/* Generated on {{date}} */

import (

	{% for p in packages %}
	"{{p}}"
	{% endfor %}
)

