
//
// Deletes all {{table_name}} by {{parent_name}}
// params: id int64 of {{parent_name}}
// returns: nil or error
//
func DeleteAll_{{table_name}}_By{{parent_name}}(fk int64) error {
	_, err := db.Exec(`
		UPDATE "{{table_name}}"
		SET "deleted" = 't' 
		WHERE "{{parent_key}}" = $1`, fk)
	return err
}