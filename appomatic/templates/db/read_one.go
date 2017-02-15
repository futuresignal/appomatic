
func ReadOne_{{table_name}}(db_struct *{{struct_name}}) bool {
	err := db.QueryRow(`
		SELECT *
		FROM "{{table_name}}" 
		WHERE id = $1
		AND "deleted" = 'f'`, &db_struct.Id).Scan(
		{% for col in model['columns']%}
        &db_struct.{{col['struct_var']}}{% if loop.index is not equalto len_cols %},
        {%endif%}{%endfor%})

	if err != nil {
		utils.HandleDbError("ReadOne_{{struct_name}}",err)
		return false
	}
	return true
} 

