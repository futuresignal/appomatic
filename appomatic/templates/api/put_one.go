
func PutOne_{{table_name}}(w http.ResponseWriter, r *http.Request){
	
	vars := mux.Vars(r)
	id,err := strconv.ParseInt(vars["{{table_name}}_id"], 10, 64)

	if err != nil {
		w.WriteHeader(200)
		m := `{"error":"Bad Request: No Id found"}`
		fmt.Fprintf(w, m)
		return
	}
	
	//get the current DB version of this struct by ID
	db_struct := {{struct_name}}{Id:&id}
	if !ReadOne_{{table_name}}(&db_struct){
		w.WriteHeader(500)
		m := `{"error":"Unable to read item"}`
		fmt.Fprint(w, m)
		return
	}

	//these are the allowed fields to be ovewritten
	okFields := map[string]bool{
		{% for col in okCols %}
		"{{col}}":{{okCols[col]}},
		{% endfor %}
	}
	
	//replaces any fields with new put object
	utils.DecodePut(&db_struct, okFields, w, r)	

	if UpdateOne_{{table_name}}(&db_struct){
		w.WriteHeader(201)
		byteArray := utils.MarshalGet(&db_struct, w, r)
		fmt.Fprint(w, string(byteArray))
		return
	} else {
		m := `{"error":"Resource not updated"}`
		w.WriteHeader(500)
		fmt.Fprint(w, m)
		return
	}
}

