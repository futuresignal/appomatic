
func GetOne_{{table_name}}(w http.ResponseWriter, r *http.Request){
	
	vars := mux.Vars(r)
	id,err := strconv.ParseInt(vars["{{table_name}}_id"], 10, 64)

	if err != nil {
		log.Println(err)
		w.WriteHeader(400)
		m := `{"error":"invalid id"}`
		fmt.Fprint(w, m)
		return
	}

	db_struct := {{struct_name}}{Id:&id}

	if ReadOne_{{table_name}}(&db_struct){
		byteArray, err := json.Marshal(&db_struct)
		if err != nil {
			w.WriteHeader(500)
			m := `{"error":"Internal error"}`
			fmt.Fprint(w, m)
			return
		}
		w.WriteHeader(200)
		fmt.Fprint(w, string(byteArray))
		return
	} else {
		w.WriteHeader(500)
		m := `{"error":"Internal error"}`
		fmt.Fprint(w, m)
		return
	}
}

