
//
// GetAll_{{table_name}}_By_{{table_parent_fkey}} 
// Params:  id_{{table_parent_fkey}}
// Returns: Slice of {{table_name}} as json
//
func GetAll_{{table_name}}_By_{{table_parent_fkey}}(w *utils.ResponseWrapper, r *http.Request){
	vars := mux.Vars(r)
	fk,err := strconv.ParseInt(vars["id_{{table_parent_fkey}}"], 10, 64)
	if err != nil {
		w.SendResponse(400, map[string]string{"error":"Bad request, no Id found"}, err)
		return
	}
	items,err := ReadAll_{{table_name}}_By_{{table_parent_fkey}}(fk);
	if err != nil {
		w.SendResponse(500, map[string]string{"error":"Internal error"}, err)
		return
	}
	w.SendResponse(200, items, err)
}

