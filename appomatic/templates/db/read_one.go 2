
func ReadOne_{{table_name}}(db_struct *{{struct_name}}) bool {
	err := db.QueryRow(`
		SELECT "id", {% for col in post_columns %}"{{col['title']}}"{% if loop.index is not equalto len_post_cols %},{%endif%}{%endfor%}
		
		FROM "{{table_name}}"
		WHERE id = $1
		AND "deleted" = 'f'`, &db_struct.Id).Scan(
		{% for col in model['columns']%}
        &db_struct.{{col['struct_var']}}{% if loop.index is not equalto len_cols %},
        {%endif%}{%endfor%})
	
	if err == sql.ErrNoRows{
		return false
	} else if err != nil {
		utils.HandleDbError("ReadOne_{{struct_name}}",err)
		return false
	}
	return true
}
