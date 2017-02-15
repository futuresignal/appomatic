
func PutOne_{{table_name}}(w http.ResponseWriter, r *http.Request){
	
	vars := mux.Vars(r)
	id,err := strconv.ParseInt(vars["{{table_name}}_id"], 10, 64)

	if err != nil {
		w.WriteHeader(400)
		m := `{"error":"Bad Request: No Id found"}`
		fmt.Fprintf(w, m)
		return
	}

	//decode json
	var db_struct {{struct_name}}
	if ok := utils.DecodePost(&db_struct, w, r); !ok {
		w.WriteHeader(400)
		m := `{"error":"Bad Request: Not able to decode object"}`
		fmt.Fprintf(w, m)
		return
	}

	//make sure to add the id to this struct
	db_struct.Id = &id
	
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

