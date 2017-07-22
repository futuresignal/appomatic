
//
// GetOne_{{table_name}} Profides our read endpoint
// Vars: id_{{table_name}}
// Returns: 
//
func GetOne_{{table_name}}(w *utils.ResponseWrapper, r *http.Request){
	
	vars := mux.Vars(r)
	id,err := strconv.ParseInt(vars["id_{{table_name}}"], 10, 64)

	if err != nil {
		w.SendResponse(400, map[string]string{"error":"Invalid id"}, err)
		return
	}

	db_struct,err := ReadOne_{{table_name}}(id)
	if err != nil {
		w.SendResponse(500,  map[string]string{"error":"Interanl error"}, nil)
		return
		
	} 

	w.SendResponse(200, db_struct, nil)
	return
}

