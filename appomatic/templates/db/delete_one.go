
func DelOne_{{table_name}}(id int64) bool {
	_, err := db.Exec(`
		UPDATE "{{table_name}}"
		SET "deleted" = 't',
		date_modified = $2 
		WHERE id = $1`, 
		id, 
		time.Now().Unix())

	if err != nil {
		utils.HandleDbError("DelOne_{{table_name}}", err)
		return false
	}
	return true
}
