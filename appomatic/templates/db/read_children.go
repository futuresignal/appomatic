

func ReadAll_{{table_name}}_By_{{rel['key']}}(fk int64) (bool, []{{struct_name}}){
	items := make([]{{struct_name}}, 0)
	rows, err := db.Query(`
		SELECT *
		FROM "{{table_name}}"
		WHERE "{{rel['key']}}" = $1 AND "deleted" = 'f'`, &fk)
	defer rows.Close()

	if err != nil {
		utils.HandleDbError("ReadAll_{{table_name}}_By_{{rel['key']}}", err)
		return false, items
	}

	for rows.Next() {
		var item {{struct_name}}
		err = rows.Scan(
			{% for col in model['columns'] %}
			&item.{{col['struct_var']}}{% if loop.index is equalto len_cols %}){%else%},
			{%endif%}
			{% endfor %}


		if err != nil {
			utils.HandleDbError("Error scanning in ReadAll_{{table_name}}_By_{{rel['key']}}", err)
		}
		items = append(items, item)
	}
	return true, items
}

