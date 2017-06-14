package {{module_name}}

/* Generated on {{date}} */

{% if packages | length > 0 %}
import (
	{% for p in packages %}
	"{{p}}"
	{% endfor %}
)
{% endif %}

