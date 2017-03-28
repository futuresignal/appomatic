
func ReadOne_{{table_name}}_by_id(id int64) (bool, {{struct_name}}) {
	db_struct := {{struct_name}}{}
	err := db.QueryRow(`
		SELECT "id", {% for col in post_columns %}"{{col['title']}}"{% if loop.index is not equalto len_post_cols %},{%endif%}{%endfor%}
		
		FROM "{{table_name}}"
		WHERE id = $1
		AND "deleted" = 'f'`, &id).Scan(
		{% for col in model['columns']%}
        &db_struct.{{col['struct_var']}}{% if loop.index is not equalto len_cols %},
        {%endif%}{%endfor%})
	
	if err == sql.ErrNoRows{
		return false, db_struct
	} else if err != nil {
		utils.HandleDbError("ReadOne_{{struct_name}}",err)
		return false, db_struct
	}
	return true, db_struct
}
