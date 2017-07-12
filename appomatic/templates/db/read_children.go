
//
// Reads all {{table_name}} by {{rel['key']}}
// Params: id int64 of {{rel['key']}}
// Returns: []{{struct_name}}, error (can be nil)
//
func ReadAll_{{table_name}}_By_{{rel['key']}}(fk int64) ([]{{struct_name}}, error){
	items := make([]{{struct_name}}, 0)
	rows, err := db.Query(`
		SELECT "id", {% for col in post_columns %}"{{col['title']}}"{% if loop.index is not equalto len_post_cols %},{%endif%}{%endfor%}
		
		FROM "{{table_name}}"
		WHERE "{{rel['key']}}" = $1 AND ("deleted" = 'f' OR "deleted" IS NULL)`, &fk)
	defer rows.Close()
	
	//note: if no rows are found, assume this isn't an error and return an empty list
	if err == sql.ErrNoRows {
		return items, nil
	} else if err != nil {
		return items,err
	}

	for rows.Next() {
		var item {{struct_name}}
		err = rows.Scan(
			{% for col in model['columns'] %}
			&item.{{col['struct_var']}}{% if loop.index is equalto len_cols %}){%else%},
			{%endif%}
			{% endfor %}

		if err != nil {
			return items, err
		}
		items = append(items, item)
	}
	return items,err
}
