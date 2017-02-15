

type {{struct_name}} struct {
	{% for col in model['columns'] %}
	{{col['struct_var']}} {{col['go_type']}}{{col['spacing']}}`json:"{{col['title']}},omitempty"`
	{% endfor %}
}
