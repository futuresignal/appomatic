

//
// Read one {{table_name}} by Id, returns a new struct 
//
func ReadOne_{{table_name}}_ById(id int64) ({{struct_name}}, error) {
	db_struct := {{struct_name}}{}
	err := db.QueryRow(`
		SELECT "id", {% for col in post_columns %}"{{col['title']}}"{% if loop.index is not equalto len_post_cols %},{%endif%}{%endfor%}
		
		FROM "{{table_name}}"
		WHERE id = $1
		AND ("deleted" = 'f' OR "deleted" IS NULL)`, &id).Scan(
		{% for col in model['columns']%}
        &db_struct.{{col['struct_var']}}{% if loop.index is not equalto len_cols %},
        {%endif%}{%endfor%})
	
	if err == sql.ErrNoRows{
		return db_struct, nil
	} 
	return db_struct, err
}
