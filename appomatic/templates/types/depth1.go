
/* this container struct contains a list wrapping children */

{% for t in tables %}
type {{t.name}} struct {
	{% for c in t.columns %}
	{{c.title}} {{c.type}}{{c.spacing}}`json:"{{c.json}},omitempty"`
	{% endfor %}
}
{% endfor %}