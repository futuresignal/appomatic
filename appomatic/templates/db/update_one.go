
//
// Updates one {{table_name}}
// Params: *{{struct_name}} must include parent id
// Returns: nil or error
//
func UpdateOne_{{table_name}}(x *{{struct_name}}) error {

	_, err := db.Exec(`
		UPDATE "{{table_name}}" SET 
		{% for col in put_cols %}
		{{col['title']}} = ${{loop.index}},
		{%endfor%}
		date_modified = ${{len_cols + 1}}
		WHERE "id" = ${{len_cols + 2}}`, 
		{% for col in put_cols %}
		&x.{{col['struct_var']}},
		{% endfor %}
		time.Now().Unix(),
		&x.Id)
	return err
}

