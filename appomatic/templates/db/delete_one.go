

//
// Deletes one {{table_name}} by id
// Params: int64 id
// Returns: nil or error
//
func DelOne_{{table_name}}(id int64) error {
	_, err := db.Exec(`
		UPDATE "{{table_name}}"
		SET "deleted" = 't',
		date_modified = $2 
		WHERE id = $1`, 
		id, 
		time.Now().Unix())
	return err
}


