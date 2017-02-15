
func PostOne_{{table_name}}(w http.ResponseWriter, r *http.Request){
	var db_struct {{struct_name}}
	if ok := utils.DecodePost(&db_struct, w, r); ok {
		if k := CreateOne_{{table_name}}(&db_struct); k {
			w.WriteHeader(201)
			byteArray := utils.MarshalGet(&db_struct, w, r)
			fmt.Fprint(w, string(byteArray))
			return
		} else {
			w.WriteHeader(500)
			m := `{"error":Resource not added"}`
			fmt.Fprint(w, m)
			return
		}
	}
}

