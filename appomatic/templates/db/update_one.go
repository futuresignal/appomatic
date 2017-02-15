
func UpdateOne_{{table_name}}(x *{{struct_name}}) bool {

	_, err := db.Exec(`
		UPDATE "{{table_name}}" SET 
		{% for col in put_cols %}
		{{col['title']}} = ${{loop.index}},
		{%endfor%}
		date_modified = ${{len_cols + 1}}
		WHERE "id" = ${{len_cols + 2}} AND "deleted" = 'f'`, 
		{% for col in put_cols %}
		&x.{{col['struct_var']}},
		{% endfor %}
		time.Now().Unix(),
		&x.Id)

	if err != nil {
		utils.HandleDbError("UpdateOne_{{table_name}}", err)
		return false
	}
	return true
}

