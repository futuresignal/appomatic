

//
// Reads an item, accepts struct as param
// Params: int64 Item id
// Returns: {{struct_name}}
//
func ReadOne_{{table_name}}(id int64) ({{struct_name}},error) {
	db_struct := {{struct_name}}{}
	err := db.QueryRow(`
		SELECT "id", {% for col in post_columns %}"{{col['title']}}"{% if loop.index is not equalto len_post_cols %},{%endif%}{%endfor%}
		
		FROM "{{table_name}}"
		WHERE id = $1`, &id).Scan(
		{% for col in model['columns']%}
        &db_struct.{{col['struct_var']}}{% if loop.index is not equalto len_cols %},
        {%endif%}{%endfor%})
	return db_struct,err
}
