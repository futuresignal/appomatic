
func GetAll_{{table_name}}_By_{{table_parent_fkey}}(w http.ResponseWriter, r *http.Request){
	vars := mux.Vars(r)
	fk,err := strconv.ParseInt(vars["{{table_parent}}_id"], 10, 64)
	if err != nil {
		m := `{"error":"Bad Request: No Id found"}`
		w.WriteHeader(400)
		fmt.Fprint(w, m)
		return
	}
	
	if ok, items := ReadAll_{{table_name}}_By_{{table_parent_fkey}}(fk); ok {
		byteArray, err := json.Marshal(&items)
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
		w.WriteHeader(404)
		m := `{"error":Resource Not Found"}`
		fmt.Fprint(w, m)
		return
	}
}

