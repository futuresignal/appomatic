
func DeleteOne_{{table_name}}(w http.ResponseWriter, r *http.Request){
	vars := mux.Vars(r)
	id,err := strconv.ParseInt(vars["{{table_name}}_id"], 10, 64)
	if err != nil {
		log.Println(err)
		w.WriteHeader(400)
		m := `{"error":"Bad Request: No Id found"}`
		fmt.Fprint(w, m)
		return
	}
	if DelOne_{{table_name}}(id){
		w.WriteHeader(200)
		m := `{"result":"successfully deleted {{table_name}} 1"}`
		fmt.Fprint(w, m)
		return
	} else {
		w.WriteHeader(500)
		m := `{"error":"Resource Not Deleted"}`
		fmt.Fprint(w, m)
		return
	}
}

