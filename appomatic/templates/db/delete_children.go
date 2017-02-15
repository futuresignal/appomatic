func DeleteAll{{table_name}}_By{{parent_name}}(fk int64) bool{
	rows, err := db.Query(`
		UPDATE "{{table_name}}"
		SET "deleted" = 't' 
		WHERE "{{parent_key}}" = $1`, fk)
	if err != nil {
		utils.HandleDbErr(err, "DeleteAll{{table_name}}_By{{parent_name}}")
		return false
	}

	return true
}