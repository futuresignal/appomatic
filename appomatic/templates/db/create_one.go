

//
// CreateOne_{{table_name}}
// Params: {{table_name}} pointer
// Returns: nil or error
//
func CreateOne_{{table_name}}(x *{{struct_name}}) error {

	err := db.QueryRow(`
		INSERT INTO "{{table_name}}"
		({% for col in post_columns %}"{{col['title']}}"{% if loop.index is not equalto len_cols %},{%endif%}{%endfor%})
		VALUES ({% for col in post_columns %}${{loop.index}}{% if loop.index is not equalto len_cols %},{%endif%}{%endfor%})
		RETURNING "id", {% for col in post_columns %}"{{col['title']}}"{% if loop.index is not equalto len_cols %},{%endif%}{%endfor%}`,
		{% for val in post_values %}
		{{val}}{% if loop.index is not equalto len_cols %},
		{%endif%}{% endfor %}).Scan(
		{% for col in model['columns'] %}
		&x.{{col['struct_var']}}{% if loop.index is not equalto len_rec_cols %},
		{% endif %}{% endfor %})

	return err
}


